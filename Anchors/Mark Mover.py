# MenuTitle: Mark Mover
__doc__ = """
Move marks to their respective heights, e.g. *comb.case to cap height, *comb to x-height, etc.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSPoint
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject
from mekkablue.geometry import transform, italicize


def moveLayer(thisLayer, verticalShift):
	if verticalShift != 0:
		print("  ↕︎ %i: %s" % (verticalShift, thisLayer.name))
		horizontalShift = 0
		italicAngle = thisLayer.master.italicAngle
		if italicAngle != 0:
			horizontalShift = italicize(NSPoint(0, verticalShift), italicAngle=italicAngle)
		shiftTransform = transform(shiftX=horizontalShift, shiftY=verticalShift)
		shiftMatrix = shiftTransform.transformStruct()
		thisLayer.applyTransform(shiftMatrix)
		thisLayer.syncMetrics()
		return 1
	else:
		print("  no shift, just syncing metrics: %s" % thisLayer.name)
		thisLayer.syncMetrics()
		return 0


def moveBottomLayer(thisLayer):
	bottomAnchor = thisLayer.anchors["_bottom"]
	if bottomAnchor:
		verticalShift = -bottomAnchor.y
		return moveLayer(thisLayer, verticalShift)
	else:
		return 0


def alefHeightForLayer(layer):
	for m in layer.metrics:
		if m.name == "Alef Height":
			return m.position
	return None


def moveGlyphToAlefHeight(thisGlyph):
	print("\n🔠 %s:" % thisGlyph.name)
	movedLayers = 0
	for thisLayer in thisGlyph.layers:
		if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
			topAnchor = thisLayer.anchors["_top"]
			if topAnchor:
				targetHeight = alefHeightForLayer(thisLayer)
				if not targetHeight:
					continue
				startHeight = topAnchor.y
				movedLayers += moveLayer(thisLayer, targetHeight - startHeight)
			else:
				movedLayers += moveBottomLayer(thisLayer)
	return movedLayers


def moveGlyphToCapHeight(thisGlyph):
	print("\n🔠 %s:" % thisGlyph.name)
	movedLayers = 0
	for thisLayer in thisGlyph.layers:
		if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
			topAnchor = thisLayer.anchors["_top"]
			if topAnchor:
				targetHeight = thisLayer.master.capHeight
				startHeight = topAnchor.y
				movedLayers += moveLayer(thisLayer, targetHeight - startHeight)
			elif thisLayer.anchors["_bottom"]:
				movedLayers += moveBottomLayer(thisLayer)
	return movedLayers


def moveGlyphToXHeight(thisGlyph):
	print("\n🔤 %s:" % thisGlyph.name)
	movedLayers = 0
	for thisLayer in thisGlyph.layers:
		if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
			topAnchor = thisLayer.anchors["_top"]
			if topAnchor:
				targetHeight = thisLayer.master.xHeight
				startHeight = topAnchor.y
				movedLayers += moveLayer(thisLayer, targetHeight - startHeight)
			elif thisLayer.anchors["_bottom"]:
				movedLayers += moveBottomLayer(thisLayer)
	return movedLayers


def moveGlyphToSmallCapHeight(thisGlyph):
	print("\n🆒 %s:" % thisGlyph.name)
	movedLayers = 0
	for thisLayer in thisGlyph.layers:
		if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
			topAnchor = thisLayer.anchors["_top"]
			if topAnchor:
				targetHeight = thisLayer.master.customParameters["smallCapHeight"]
				if targetHeight:
					startHeight = topAnchor.y
					movedLayers += moveLayer(thisLayer, targetHeight - startHeight)
			else:
				movedLayers += moveBottomLayer(thisLayer)
	return movedLayers


class MarkMover(mekkaObject):
	prefDict = {
		"arabicMarks": 1,
		"lowercaseMarks": 1,
		"uppercaseMarks": 1,
		"smallcapMarks": 0,
		"setMetricsKeys": 0,
		"leftMetricsKey": "=40",
		"rightMetricsKey": "=|",
		"includeAllGlyphs": 1,
		"newTab": 1,
		"reuseTab": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 330
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Mark Mover",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		metricsKeysTooltip = "Sets the metrics keys of the marks, so their sidebearings follow the keys: LSB for the left, RSB for the right sidebearing."

		self.w.descriptionText = vanilla.TextBox("auto", "Move connecting anchors on metric line", sizeStyle="small")
		self.w.arabicMarks = vanilla.CheckBox("auto", "Move Arabic marks to Alef Height", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.arabicMarks.setToolTip("Moves marks in Arabic script to the metric called Alef Height.")
		self.w.lowercaseMarks = vanilla.CheckBox("auto", "Move …comb marks to x-height", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.lowercaseMarks.setToolTip("Moves nonspacing marks (e.g. acutecomb) to x-height, by their _top anchor, or by their _bottom anchor onto the baseline.")
		self.w.uppercaseMarks = vanilla.CheckBox("auto", "Move …comb.case marks to cap height", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.uppercaseMarks.setToolTip("Moves marks with the .case or .uc suffix (e.g. acutecomb.case) to cap height.")
		self.w.smallcapMarks = vanilla.CheckBox("auto", "Move …comb.sc to smallcap height", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.smallcapMarks.setToolTip("Moves marks with the .sc, .smcp, .c2sc or .small suffix to the smallCapHeight master parameter.")

		self.w.setMetricsKeys = vanilla.CheckBox("auto", "Set metrics keys, LSB", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.setMetricsKeys.setToolTip(metricsKeysTooltip)
		self.w.leftMetricsKey = vanilla.EditText("auto", "=40", callback=self.SavePreferences, sizeStyle="small")
		self.w.leftMetricsKey.setToolTip("Left metrics key for the marks, e.g. =40")
		self.w.rightMetricsKeyText = vanilla.TextBox("auto", "RSB", sizeStyle="small")
		self.w.rightMetricsKeyText.setToolTip(metricsKeysTooltip)
		self.w.rightMetricsKey = vanilla.EditText("auto", "=|", callback=self.SavePreferences, sizeStyle="small")
		self.w.rightMetricsKey.setToolTip("Right metrics key for the marks, e.g. =|")

		self.w.includeAllGlyphs = vanilla.CheckBox("auto", "Include all glyphs in font (otherwise just selection)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeAllGlyphs.setToolTip("Processes all mark glyphs in the font. Otherwise only the selected glyphs.")
		self.w.newTab = vanilla.CheckBox("auto", "Open tab with marks", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.newTab.setToolTip("Opens an Edit tab with the processed marks.")
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.setToolTip("Puts the marks in the current Edit tab, if there is one, instead of opening a new tab.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Move", callback=self.MarkMoverMain)
		self.w.runButton.setToolTip("Move the marks.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the RSB label hugs its text
		nsLabel = self.w.rightMetricsKeyText.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[arabicMarks]-(>=inset)-|",
				"H:|-inset-[lowercaseMarks]-(>=inset)-|",
				"H:|-inset-[uppercaseMarks]-(>=inset)-|",
				"H:|-inset-[smallcapMarks]-(>=inset)-|",
				"H:|-inset-[setMetricsKeys]-gap-[leftMetricsKey(55)]-gap-[rightMetricsKeyText]-gap-[rightMetricsKey(55)]-(>=inset)-|",
				"H:|-inset-[includeAllGlyphs]-(>=inset)-|",
				"H:|-inset-[newTab]-gap-[reuseTab]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[arabicMarks]-checkRow-[lowercaseMarks]-checkRow-[uppercaseMarks]-checkRow-[smallcapMarks]-row-[leftMetricsKey]-row-[includeAllGlyphs]-checkRow-[newTab]-inset-[runButton]-inset-|",
				{"view1": self.w.setMetricsKeys, "attribute1": "centerY", "view2": self.w.leftMetricsKey, "attribute2": "centerY"},
				{"view1": self.w.rightMetricsKeyText, "attribute1": "centerY", "view2": self.w.leftMetricsKey, "attribute2": "centerY"},
				{"view1": self.w.rightMetricsKey, "attribute1": "centerY", "view2": self.w.leftMetricsKey, "attribute2": "centerY"},
				{"view1": self.w.reuseTab, "attribute1": "centerY", "view2": self.w.newTab, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		onOff = self.w.lowercaseMarks.get() or self.w.uppercaseMarks.get() or self.w.smallcapMarks.get() or self.w.arabicMarks.get()
		self.w.runButton.enable(onOff)

		onOff = self.w.setMetricsKeys.get()
		self.w.leftMetricsKey.enable(onOff)
		self.w.rightMetricsKey.enable(onOff)

	def MarkMoverMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Mark Mover Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")

				lowercaseMarks = self.pref("lowercaseMarks")
				uppercaseMarks = self.pref("uppercaseMarks")
				smallcapMarks = self.pref("smallcapMarks")
				setMetricsKeys = self.pref("setMetricsKeys")
				leftMetricsKey = self.pref("leftMetricsKey")
				rightMetricsKey = self.pref("rightMetricsKey")
				includeAllGlyphs = self.pref("includeAllGlyphs")
				arabicMarks = self.pref("arabicMarks")
				newTab = self.pref("newTab")
				reuseTab = self.pref("reuseTab")

				if includeAllGlyphs:
					glyphs = thisFont.glyphs
				else:
					glyphs = [layer.parent for layer in thisFont.selectedLayers]

				glyphNames = []
				movedMarks = 0
				for glyph in glyphs:
					glyphParts = glyph.name.split(".")
					if glyphParts[0].endswith("comb") or (glyph.category == "Mark" and glyph.subCategory == "Nonspacing"):
						if setMetricsKeys:
							glyph.leftMetricsKey = leftMetricsKey
							glyph.rightMetricsKey = rightMetricsKey
						glyphNames.append(glyph.name)
						if arabicMarks and glyph.script == "arabic":
							movedMarks += moveGlyphToAlefHeight(glyph)
						elif smallcapMarks and ("sc" in glyphParts or "smcp" in glyphParts or "c2sc" in glyphParts or "small" in glyphParts):
							movedMarks += moveGlyphToSmallCapHeight(glyph)
						elif uppercaseMarks and ("case" in glyphParts or "uc" in glyphParts):
							movedMarks += moveGlyphToCapHeight(glyph)
						elif lowercaseMarks:
							movedMarks += moveGlyphToXHeight(glyph)

			# Final report:
			Glyphs.showNotification(
				"%s: Done" % (thisFont.familyName),
				"Mark Mover shifted %i layer%s in %i mark%s. Details in Macro Window" % (
					movedMarks,
					"" if movedMarks == 1 else "s",
					len(glyphNames),
					"" if len(glyphNames) == 1 else "s",
				),
			)

			print("\nDone.")

			if newTab and glyphNames:
				if reuseTab and thisFont.currentTab:
					tab = thisFont.currentTab
				else:
					tab = thisFont.newTab()
				tab.text = "/" + "/".join(glyphNames)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Mark Mover Error: {e}")
			import traceback
			print(traceback.format_exc())


MarkMover()
