# MenuTitle: Snap Anchors to Nearest Metric
__doc__ = """
Moves specified anchors to the nearest metric (e.g. x-height, ascender, etc.), within a specified threshold.
"""

import objc
import vanilla
from Foundation import NSPoint
from AppKit import (
	NSAffineTransform,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityWindowSizeStayPut,
	NSWindowStyleMaskResizable,
)
from GlyphsApp import Glyphs, Message, addPoints
from mekkablue import mekkaObject, match, UpdateButton, reportFontName
from mekkablue.geometry import italicize


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def closestMetric(position, metrics):
	return sorted(metrics, key=lambda metric: abs(metric - position))[0]


def legibleNum(number):
	try:
		return f"{float(number):0.1f}".rstrip("0").rstrip(".")
	except:
		return number


class SnapAnchorsToNearestMetric(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"anchorNames": "_top, _bottom, top, bottom, ogonek, _ogonek",
		"threshold": 30,
		"respectItalic": True,
		"focusOnMarkAnchorsInMarks": True,
		"allFonts": False,
		"verbose": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 330
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Snap Anchors to Nearest Metric",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Move these anchors to the nearest vertical metric line:", sizeStyle="small", selectable=True)

		self.w.anchorNames = vanilla.ComboBox("auto", self.allAnchorNamesInFrontmostFont(), sizeStyle="small", callback=self.SavePreferences)
		self.w.anchorNames.setToolTip("You can use wildcards * and ?, and add multiple anchor names with commas.")
		self.w.anchorNamesUpdate = UpdateButton("auto", callback=self.updateUI)
		self.w.anchorNamesUpdate.setToolTip("Reload the anchor names of the frontmost font.")

		self.w.anchorNamesDescription = vanilla.TextBox("auto", "For mark anchors (like _top), will shift complete glyph.", sizeStyle="small", selectable=True)

		tooltipText = "Anchors further away from the nearest metric than this value are not moved."
		self.w.thresholdText = vanilla.TextBox("auto", "Max vertical move:", sizeStyle="small", selectable=True)
		self.w.threshold = SteppingEditText("auto", "30", callback=self.thresholdChanged, sizeStyle="small")
		self.w.thresholdText.setToolTip(tooltipText)
		self.w.threshold.setToolTip(tooltipText)

		self.w.respectItalic = vanilla.CheckBox("auto", "Respect italic angle (otherwise always vertical)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.focusOnMarkAnchorsInMarks = vanilla.CheckBox("auto", "In marks, ignore non-underscore anchors", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.focusOnMarkAnchorsInMarks.setToolTip("Will look only for _xxx anchors in marks (i.e., with an underscore), and ignore those not starting with an underscore.")
		self.w.allFonts = vanilla.CheckBox("auto", "Apply to ⚠️ ALL fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose = vanilla.CheckBox("auto", "Verbose reporting", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Snap", callback=self.SnapAnchorsToNearestMetricMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[anchorNames]-gap-[anchorNamesUpdate(20)]-inset-|",
				"H:|-inset-[anchorNamesDescription]-inset-|",
				"H:|-inset-[thresholdText]-gap-[threshold(50)]-(>=inset)-|",
				"H:|-inset-[respectItalic]-(>=inset)-|",
				"H:|-inset-[focusOnMarkAnchorsInMarks]-(>=inset)-|",
				"H:|-inset-[allFonts]-gap-[verbose]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[anchorNames]-row-[anchorNamesDescription]-row-[threshold]-row-[respectItalic]-checkRow-[focusOnMarkAnchorsInMarks]-checkRow-[allFonts]-inset-[runButton]-inset-|",
				{"view1": self.w.anchorNamesUpdate, "attribute1": "centerY", "view2": self.w.anchorNames, "attribute2": "centerY"},
				{"view1": self.w.thresholdText, "attribute1": "centerY", "view2": self.w.threshold, "attribute2": "centerY"},
				{"view1": self.w.verbose, "attribute1": "centerY", "view2": self.w.allFonts, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# resizable horizontally only: content height stays fixed
		nsWindow = self.w.getNSWindow()
		contentHeight = nsWindow.contentRectForFrameRect_(nsWindow.frame()).size.height
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.setContentMinSize_((windowWidth, contentHeight))
		nsWindow.setContentMaxSize_((windowWidth + 500, contentHeight))

	def thresholdChanged(self, sender=None):
		"""Threshold cannot be negative: resets the field to 0 when stepped or typed below 0."""
		try:
			isNegative = float(self.w.threshold.get()) < 0
		except ValueError:
			isNegative = False
		if isNegative:
			self.w.threshold.set("0")
		self.SavePreferences(sender)

	def allAnchorNamesInFrontmostFont(self, sender=None):
		font = Glyphs.font
		if not font:
			return []
		anchors = []
		for g in font.glyphs:
			for l in g.layers:
				for a in l.anchors:
					if a.name not in anchors:
						anchors.append(a.name)
		return sorted(anchors)


	def updateUI(self, sender=None):
		self.w.anchorNames.setItems(self.allAnchorNamesInFrontmostFont())


	def moveAnchorsToNearestMetricsOnLayer(self, layer, anchorNames=["_top", "_bottom", "top", "bottom"], respectItalic=True, threshold=30, verbose=False, underscoreOnlyInMarks=True):
		didMove = False
		reports = []
		isMark = layer.parent.category == "Mark"
		beyondThreshold = False

		if not layer.anchors:
			if verbose:
				reports.append(f"   🤷🏻‍♀️ no anchors on layer {layer.name}")
			return didMove, reports, beyondThreshold

		if not any([match(an, a.name) for a in layer.anchors for an in anchorNames]):
			if verbose:
				reports.append(f"   🤷🏻‍♀️ no matching anchors on layer {layer.name}, only: {', '.join([a.name for a in layer.anchors])}")
			return didMove, reports, beyondThreshold

		respectItalic = respectItalic and layer.italicAngle != 0
		positions = tuple(m.position for m in layer.metrics)
		for anchorName in anchorNames:
			for anchor in layer.anchors:
				if match(anchorName, anchor.name):
					currentHeight = anchor.position.y
					targetHeight = closestMetric(currentHeight, positions)
					verticalMovement = targetHeight - currentHeight

					if verticalMovement == 0:
						continue

					if abs(verticalMovement) > threshold:
						reports.append(f"   ⚠️ layer {layer.name}, anchor {anchor.name}: move {legibleNum(verticalMovement)} beyond threshold {threshold}")
						beyondThreshold = True
						continue

					move = NSPoint(0, verticalMovement)
					if respectItalic:
						move = italicize(move, italicAngle=layer.italicAngle)
					if anchor.name.startswith("_"):
						moveTransform = NSAffineTransform.transform()
						moveTransform.translateXBy_yBy_(move.x, move.y)
						# moveMatrix = moveTransform.transformStruct()
						layer.applyTransform(moveTransform)
						if verbose:
							reports.append(f"   ↕️ shifted layer {layer.name} {legibleNum(move.x)} {legibleNum(move.y)}")
					elif not isMark or not underscoreOnlyInMarks:
						anchor.position = addPoints(anchor.position, move)
						if verbose:
							reports.append(f"   ⚓️ moved {layer.name} {anchor.name} {legibleNum(move.x)} {legibleNum(move.y)}")
					didMove = True

		return didMove, reports, beyondThreshold


	def SnapAnchorsToNearestMetricMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if Glyphs.font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			allFonts = self.prefBool("allFonts")
			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			# read prefs:
			threshold = self.prefInt("threshold")
			respectItalic = self.prefBool("respectItalic")
			verbose = self.prefBool("verbose")
			anchorNamesList = sorted(set([a.strip() for a in self.pref("anchorNames").strip().split(",")]))
			focusOnMarkAnchorsInMarks = self.prefBool("focusOnMarkAnchorsInMarks")

			for thisFont in theseFonts:
				reportName = reportFontName(thisFont)
				print(f"Snap Anchors to Nearest Metric Report for {reportName}")
				print()

				thisFont = Glyphs.font
				if thisFont.filepath:
					fontName = thisFont.filepath.lastPathComponent().stringByDeletingLastDotSuffix()
				else:
					fontName = thisFont.familyName
				print(f"Moving Anchors in {fontName}:\n")
				tabText = ""
				glyphsBeyondThreshold = []
				for g in thisFont.glyphs:
					movedAnchorsInGlyph = False
					glyphReports = []
					beyondThreshold = False
					for layer in g.layers:
						if layer.isMasterLayer or layer.isSpecialLayer:
							movedAnchorsOnLayer, layerReports, layerBeyondThreshold = self.moveAnchorsToNearestMetricsOnLayer(
								layer,
								anchorNames=anchorNamesList,
								respectItalic=respectItalic,
								threshold=threshold,
								underscoreOnlyInMarks=focusOnMarkAnchorsInMarks,
								verbose=verbose,
							)
							movedAnchorsInGlyph = movedAnchorsInGlyph or movedAnchorsOnLayer
							glyphReports.extend(layerReports)
							beyondThreshold = beyondThreshold or layerBeyondThreshold

					if glyphReports:
						reports = '\n'.join(glyphReports)
						print(f"🔤 {g.name}:\n{reports}")

					if movedAnchorsInGlyph:
						tabText += f"/{g.name}"

					if beyondThreshold:
						glyphsBeyondThreshold.append(g.name)

				if tabText:
					if glyphsBeyondThreshold:
						tabText += f"\n\nBeyond threshold:\n/{'/'.join(glyphsBeyondThreshold)}"
					thisFont.newTab(f"Snapped anchors:\n{tabText}")

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Snap Anchors to Nearest Metric Error: {e}")
			import traceback
			print(traceback.format_exc())


SnapAnchorsToNearestMetric()
