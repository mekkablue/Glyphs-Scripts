# MenuTitle: Tackle Short Segments
__doc__ = """
Finds short segments (measuring between the on-curve nodes, ignoring handles) and can remove them, multiply the length of short line segments, or straighten short curve segments.
"""

import vanilla
from mekkablue import mekkaObject, SteppingEditText, decimalFormatter
from GlyphsApp import Glyphs, GSLINE, GSOFFCURVE
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)

REMOVE = 0
STRAIGHTEN = 1
MULTIPLY = 2  # last, so it sits right above the field that belongs to it


class TackleShortSegments(mekkaObject):
	prefDict = {
		"threshold": 1,
		"actionType": REMOVE,  # new name: the order of the choices changed, so old saved values would mean something else
		"factor": 1,
	}

	def __init__(self):
		windowWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Tackle Short Segments",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		inset = 15

		# threshold line:
		tooltipText = "Segments whose horizontal and vertical extents (measured between the surrounding on-curve nodes) are both at or below this many units count as short."
		self.w.thresholdText = vanilla.TextBox("auto", "Short segments up to:", selectable=True, sizeStyle="small")
		self.w.threshold = SteppingEditText("auto", "1", callback=self.SavePreferences, sizeStyle="small", formatter=decimalFormatter(0))
		self.w.thresholdText.setToolTip(tooltipText)
		self.w.threshold.setToolTip(tooltipText)

		# action radio buttons:
		self.w.actionType = vanilla.RadioGroup(
			"auto",
			[
				"Remove short segments",
				"Straighten curve segments",
				"Multiply line segments",
			],
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.actionType.getNSMatrix().setToolTip_("Choose what to do with short segments. Removal and straightening treat both lines and curves; multiplication only affects line segments.")

		# factor field:
		tooltipText = "Factor by which the length of a short line segment gets multiplied (e.g. 2 doubles it)."
		self.w.factorText = vanilla.TextBox("auto", "Multiply by:", selectable=True, sizeStyle="small")
		self.w.factor = SteppingEditText("auto", "2", callback=self.SavePreferences, sizeStyle="small", formatter=decimalFormatter(0))
		self.w.factorText.setToolTip(tooltipText)
		self.w.factor.setToolTip(tooltipText)

		# run button (regular size):
		self.w.runButton = vanilla.Button("auto", "Tackle", callback=self.TackleShortSegmentsMain)
		self.w.runButton.setToolTip("Finds short segments and applies the chosen action to them.")
		self.w.setDefaultButton(self.w.runButton)

		# status line:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")

		# the status line takes the leftover width, the button stays as wide as its title needs:
		nsStatus = self.w.status.getNSTextField()
		nsStatus.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		nsStatus.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		nsRunButton = self.w.runButton.getNSButton()
		nsRunButton.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsRunButton.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# labels: right-aligned, same width
		labelNames = ("thresholdText", "factorText")
		widestLabel = "thresholdText"  # the label with the longest text
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# keep every control at its natural height, so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[thresholdText]-gap-[threshold(60)]-(>=inset)-|",
				"H:|-inset-[actionType]-inset-|",
				"H:|-inset-[factorText]-gap-[factor(60)]-(>=inset)-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[threshold]-row-[actionType(radioHeight)]-row-[factor]-inset-[runButton]-inset-|",
				{"view1": self.w.thresholdText, "attribute1": "centerY", "view2": self.w.threshold, "attribute2": "centerY"},
				{"view1": self.w.factorText, "attribute1": "centerY", "view2": self.w.factor, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "radioHeight": 56},
		)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		isMultiply = self.prefInt("actionType") == MULTIPLY
		self.w.factor.enable(isMultiply)
		self.w.factorText.enable(isMultiply)

	def process(self, thisLayer, threshold, action, factor):
		count = 0
		for thisPath in thisLayer.paths:
			# collect on-curve nodes first, so index shifts from editing do not disturb the loop:
			onCurveNodes = [thisNode for thisNode in thisPath.nodes if thisNode.type != GSOFFCURVE]
			for thisNode in reversed(onCurveNodes):
				prevNode = thisNode.prevNode
				if prevNode is None:
					continue  # open path start node

				if prevNode.type == GSOFFCURVE:
					isCurve = True
					startNode = prevNode.prevNode.prevNode  # the previous on-curve node
				else:
					isCurve = False
					startNode = prevNode

				if startNode is None:
					continue

				xDistance = thisNode.x - startNode.x
				yDistance = thisNode.y - startNode.y
				if abs(xDistance) > threshold or abs(yDistance) > threshold:
					continue  # not a short segment

				if action == REMOVE:
					thisPath.removeNodeCheckKeepShape_(thisNode)
					count += 1
				elif action == MULTIPLY:
					if not isCurve:
						thisNode.x = startNode.x + xDistance * factor
						thisNode.y = startNode.y + yDistance * factor
						count += 1
				elif action == STRAIGHTEN:
					if isCurve:
						secondHandle = prevNode
						firstHandle = prevNode.prevNode
						del thisPath.nodes[secondHandle.index]
						del thisPath.nodes[firstHandle.index]
						thisNode.type = GSLINE
						count += 1
		return count

	def TackleShortSegmentsMain(self, sender):
		self.SavePreferences()
		thisFont = Glyphs.font
		if not thisFont:
			self.setStatus("⚠️ No font open.")
			Glyphs.showNotification("Tackle Short Segments", "No font open.")
			return

		threshold = self.prefFloat("threshold")
		action = self.prefInt("actionType")
		factor = self.prefFloat("factor")
		selectedLayers = thisFont.selectedLayers
		if not selectedLayers:
			self.setStatus("⚠️ Select at least one glyph.")
			Glyphs.showNotification("Tackle Short Segments", "Select at least one glyph.")
			return

		Glyphs.clearLog()
		print("Tackle Short Segments\n")
		verbs = {
			REMOVE: ("Removed", "removed"),
			MULTIPLY: ("Multiplied", "multiplied"),
			STRAIGHTEN: ("Straightened", "straightened"),
		}
		pastTense, verb = verbs[action]

		thisFont.disableUpdateInterface()
		totalCount = 0
		thisGlyph = None
		self.setStatus("🛠️ Processing %i layer%s…" % (len(selectedLayers), "" if len(selectedLayers) == 1 else "s"))
		try:
			for thisLayer in selectedLayers:
				thisGlyph = thisLayer.parent
				self.setStatus("🔠 %s" % thisGlyph.name)
				count = self.process(thisLayer, threshold, action, factor)
				totalCount += count
				if count:
					print("\t✅ %s: %s %i segment%s" % (thisGlyph.name, verb, count, "" if count == 1 else "s"))
				else:
					print("\t☑️ %s: no short segments" % thisGlyph.name)
		except Exception as e:
			self.setStatus("❌ Error at %s. Details in Macro Window." % (thisGlyph.name if thisGlyph else "start"))
			Glyphs.showMacroWindow()
			print("\n⚠️ Script Error:\n")
			import traceback
			print(traceback.format_exc())
			print()
			raise e
		finally:
			thisFont.enableUpdateInterface()

		self.setStatus("✅ %s %i segment%s." % (pastTense, totalCount, "" if totalCount == 1 else "s"))
		Glyphs.showNotification("Tackle Short Segments", "%s %i segment%s. Details in Macro Window." % (pastTense, totalCount, "" if totalCount == 1 else "s"))


TackleShortSegments()
