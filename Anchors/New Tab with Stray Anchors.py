# MenuTitle: New Tab with Stray Anchors
__doc__="""
Find all anchors that are not where they are supposed to be.
"""

import sys
import objc
import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight, NSWindowStyleMaskResizable
from Foundation import NSNumberFormatter, NSSize
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, newLineControlLayer, UpdateButton, reportFontName

horizontals = (
	"LSB",
	"RSB",
	"LSB or RSB",
	"Center (min 1u tolerance)",
	"Center or LSB or RSB",
)

verticals = (
	"Any metric line",
	"Baseline",
	"Cap or x-height",
)


def anchorIsAstray(thisAnchor, thisLayer, shouldHorizontalAlign, shouldVerticalAlign, horizontalAlignment, verticalAlignment, tolerance=0.0):
	x, y = thisAnchor.position

	def isNotAt(value, target):
		"""True if value is farther from target than the tolerance."""
		return target is None or abs(value - target) > tolerance

	if shouldHorizontalAlign:
		isNotAtLSB = isNotAt(x, 0)
		isNotAtRSB = isNotAt(x, thisLayer.width)
		isNotInCenter = abs(x - thisLayer.width / 2) > max(1, tolerance)

		# none of the positions are taken -> definitely astray
		if all((isNotAtLSB, isNotAtRSB, isNotInCenter)):
			return True

		if horizontalAlignment <= 2 and isNotAtLSB and isNotAtRSB:
			return True

		# LSB
		if horizontalAlignment == 0 and isNotAtLSB:
			return True

		# RSB
		if horizontalAlignment == 1 and isNotAtRSB:
			return True

		# Center (min 1u tolerance)
		if horizontalAlignment == 3 and isNotInCenter:
			return True

	if shouldVerticalAlign:
		xHeight, capHeight = None, None
		for m in thisLayer.metrics:
			if m.name == "x-Height":
				xHeight = m.position
			if m.name == "Cap Height":
				capHeight = m.position

		isNotAtBaseline = isNotAt(y, 0)
		isNotAtXHeight = isNotAt(y, xHeight)
		isNotAtCapHeight = isNotAt(y, capHeight)
		isNotOnAnyMetric = all(isNotAt(y, m.position) for m in thisLayer.metrics)

		# Any metric line
		if verticalAlignment == 0 and isNotOnAnyMetric:
			return True

		# Baseline
		if verticalAlignment == 1 and isNotAtBaseline:
			return True

		# Cap or x-height
		if verticalAlignment == 2 and isNotAtXHeight and isNotAtCapHeight:
			return True

	return False


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


class FindStrayAnchors(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"shouldHorizontalAlign": False,
		"shouldVerticalAlign": False,
		"horizontalAlignment": 2, # LSB or RSB
		"verticalAlignment": 0, # Any Metric Line
		"anchors": "top, bottom, _top, _bottom",
		"tolerance": 0,
		"reuseTab": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Find Stray Anchors",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		anchorsTooltip = "All anchors you want to find. Separate multiple names with comma’s, e.g., ‘top, bottom’ or ‘exit, entry’."

		self.w.descriptionText = vanilla.TextBox("auto", "Open a new tab with glyphs where anchors are not where they are supposed to be:", sizeStyle="small", selectable=True)

		self.w.anchorsText = vanilla.TextBox("auto", "Find anchors", sizeStyle="small", selectable=True)
		self.w.anchorsText.setToolTip(anchorsTooltip)
		self.w.anchors = vanilla.EditText("auto", "top, bottom, _top, _bottom", callback=self.SavePreferences, sizeStyle="small")
		self.w.anchors.setToolTip(anchorsTooltip)
		self.w.updateButton = UpdateButton("auto", callback=self.updateAnchorNames)
		self.w.updateButton.setToolTip("Insert all anchor names of the frontmost font. Resets to default ‘top, bottom, _top, _bottom’ if there is no font open (or no anchors in the frontmost font).")

		self.w.shouldHorizontalAlign = vanilla.CheckBox("auto", "Horizontally not on:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.shouldHorizontalAlign.setToolTip("Find anchors that are not at the chosen horizontal position.")
		self.w.horizontalAlignment = vanilla.PopUpButton("auto", horizontals, sizeStyle="small", callback=self.SavePreferences)
		self.w.horizontalAlignment.setToolTip("Horizontal positions that count as correct. Anchors anywhere else are stray.")

		self.w.shouldVerticalAlign = vanilla.CheckBox("auto", "Vertically not on:", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.shouldVerticalAlign.setToolTip("Find anchors that are not at the chosen vertical position.")
		self.w.verticalAlignment = vanilla.PopUpButton("auto", verticals, sizeStyle="small", callback=self.SavePreferences)
		self.w.verticalAlignment.setToolTip("Vertical positions that count as correct. Anchors anywhere else are stray.")

		toleranceTooltip = "Anchors this many units or fewer away from the chosen position still count as being on it. Applies to horizontal and vertical positions."
		self.w.toleranceText = vanilla.TextBox("auto", "Tolerance:", sizeStyle="small", selectable=True)
		self.w.toleranceText.setToolTip(toleranceTooltip)
		toleranceFormatter = NSNumberFormatter.alloc().init()
		toleranceFormatter.setAllowsFloats_(False)
		toleranceFormatter.setMinimum_(0)
		self.w.tolerance = SteppingEditText("auto", "0", callback=self.SavePreferences, sizeStyle="small", formatter=toleranceFormatter)
		self.w.tolerance.setToolTip(toleranceTooltip)

		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.setToolTip("Put the report in the current Edit tab, if there is one, instead of opening a new tab.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Find", callback=self.FindStrayAnchorsMain)
		self.w.runButton.setToolTip("Open a tab with the layers that have stray anchors.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels keep their text on one line, except for the description, which wraps
		for labelName in ("anchorsText", "toleranceText"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		# the checkbox titles stay on one line
		for checkBoxName in ("shouldHorizontalAlign", "shouldVerticalAlign"):
			getattr(self.w, checkBoxName).getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[anchorsText]-gap-[anchors]-gap-[updateButton]-inset-|",
				"H:|-inset-[shouldHorizontalAlign]-gap-[horizontalAlignment(>=100)]-inset-|",
				"H:|-inset-[shouldVerticalAlign]-gap-[verticalAlignment]-inset-|",
				"H:|-inset-[toleranceText]-gap-[tolerance(60)]-(>=inset)-|",
				"H:|-inset-[reuseTab]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText(30)]-row-[anchors]-row-[horizontalAlignment]-row-[verticalAlignment]-row-[tolerance]-row-[reuseTab]-inset-[runButton]-inset-|",
				# the first column shares one width, so the fields start at one x-position
				{"view1": self.w.anchorsText, "attribute1": "width", "view2": self.w.shouldHorizontalAlign, "attribute2": "width"},
				{"view1": self.w.shouldVerticalAlign, "attribute1": "width", "view2": self.w.shouldHorizontalAlign, "attribute2": "width"},
				{"view1": self.w.verticalAlignment, "attribute1": "width", "view2": self.w.horizontalAlignment, "attribute2": "width"},
				{"view1": self.w.toleranceText, "attribute1": "width", "view2": self.w.shouldHorizontalAlign, "attribute2": "width"},
				{"view1": self.w.toleranceText, "attribute1": "centerY", "view2": self.w.tolerance, "attribute2": "centerY"},
				{"view1": self.w.anchorsText, "attribute1": "centerY", "view2": self.w.anchors, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.anchors, "attribute2": "centerY"},
				{"view1": self.w.shouldHorizontalAlign, "attribute1": "centerY", "view2": self.w.horizontalAlignment, "attribute2": "centerY"},
				{"view1": self.w.shouldVerticalAlign, "attribute1": "centerY", "view2": self.w.verticalAlignment, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Find Stray Anchors’ could not load preferences. Will resort to defaults.")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# resizable horizontally only: lock the content height Auto Layout arrived at
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()
		contentHeight = nsWindow.contentView().frame().size.height
		nsWindow.setContentMinSize_(NSSize(windowWidth, contentHeight))
		nsWindow.setContentMaxSize_(NSSize(windowWidth + 1000, contentHeight))

	def updateAnchorNames(self, sender=None):
		anchorText = self.collectAnchors()
		self.w.anchors.set(anchorText)


	def updateUI(self, sender=None):
		activeH = self.uiElement("shouldHorizontalAlign").get()
		activeV = self.uiElement("shouldVerticalAlign").get()
		activeButton = activeH or activeV
		self.uiElement("horizontalAlignment").enable(activeH)
		self.uiElement("verticalAlignment").enable(activeV)
		self.uiElement("runButton").enable(activeButton)


	def collectAnchors(self, default="top, bottom, _top, _bottom"):
		currentFont = Glyphs.font
		if not currentFont:
			return default

		collectedAnchors = []
		for glyph in currentFont.glyphs:
			for layer in glyph.layers:
				if not layer.isMasterLayer and not layer.isSpecialLayer:
					continue
				for anchor in layer.anchors:
					if not anchor.name in collectedAnchors:
						collectedAnchors.append(anchor.name)

		if not collectedAnchors:
			return default

		return ", ".join(sorted(collectedAnchors))


	def FindStrayAnchorsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			self.SavePreferences()
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			else:
				reportName = reportFontName(thisFont)
				print(f"Find Stray Anchors Report for {reportName}")
				print()
				
				anchors = self.pref("anchors")
				if not anchors:
					print("No anchors specified by user. Exiting.")
					Message(
						title="No anchors specified",
						message="Write comma-separated anchor names in the ‘Find anchors’ field, or click on the update button to populate the field with all anchor names of the frontmost font.",
						OKButton=None,
						)
					return

				shouldHorizontalAlign = self.pref("shouldHorizontalAlign")
				shouldVerticalAlign = self.pref("shouldVerticalAlign")
				horizontalAlignment = self.pref("horizontalAlignment")
				verticalAlignment = self.pref("verticalAlignment")
				tolerance = max(0.0, self.prefFloat("tolerance"))

				report = {}
				anchorNames = [a.strip() for a in anchors.split(",")]

				for anchorName in anchorNames:
					report[anchorName] = []

				for thisGlyph in thisFont.glyphs:
					for thisLayer in thisGlyph.layers:
						if not thisLayer.isMasterLayer and not thisLayer.isSpecialLayer:
							continue
						thisLayer.selection = []
						for thisAnchor in thisLayer.anchors:
							if not thisAnchor.name in anchorNames:
								continue

							if anchorIsAstray(thisAnchor, thisLayer, shouldHorizontalAlign, shouldVerticalAlign, horizontalAlignment, verticalAlignment, tolerance):
								report[thisAnchor.name].append(thisLayer)
								thisLayer.selection.append(thisAnchor)

				# none found, celebrate
				if all([bool(report[a])==False for a in report.keys()]):
					Message(
						title="All good!",
						message="No stray anchors found with the specified settings.",
						OKButton="Cheers🍻",
						)
					return

				# determine the report tab
				if thisFont.currentTab and self.pref("reuseTab"):
					reportTab = thisFont.currentTab
					reportTab.layers = []
				else:
					reportTab = thisFont.newTab()
				
				# fill report tab with all affected layers
				for anchorName in sorted(report.keys()):
					if not report[anchorName]:
						continue
					for character in anchorName:
						glyph = thisFont.glyphForCharacter_(ord(character))
						if not glyph:
							continue
						reportTab.layers.append(glyph.layers[0])
					reportTab.layers.append(newLineControlLayer())
					for reportedLayer in report[anchorName]:
						reportTab.layers.append(reportedLayer)
					for x in range(2):
						reportTab.layers.append(newLineControlLayer())

				# self.w.close() # delete if you want window to stay open

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Find Stray Anchors Error: {e}")
			import traceback
			print(traceback.format_exc())


FindStrayAnchors()
