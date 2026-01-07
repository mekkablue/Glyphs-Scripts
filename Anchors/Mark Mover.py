# MenuTitle: Mark Mover
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Move marks to their respective heights, e.g. *comb.case to cap height, *comb to x-height, etc.
"""

import vanilla
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
	prefID = ""
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
		windowWidth = 310
		windowHeight = 224
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Mark Mover",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Move connecting anchors on metric line", sizeStyle='small')
		linePos += lineHeight

		self.w.arabicMarks = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Move Arabic marks to Alef Height", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.lowercaseMarks = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Move …comb marks to x-height", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.uppercaseMarks = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Move …comb.case marks to cap height", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.smallcapMarks = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Move …comb.sc to smallcap height", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.setMetricsKeys = vanilla.CheckBox((inset + 2, linePos - 1, 140, 20), "Set metrics keys, LSB", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.leftMetricsKey = vanilla.EditText((inset + 135, linePos - 1, 55, 19), "=40", callback=self.SavePreferences, sizeStyle='small')
		self.w.rightMetricsKeyText = vanilla.TextBox((inset + 195, linePos + 2, 30, 14), "RSB", sizeStyle='small')
		self.w.rightMetricsKey = vanilla.EditText((inset + 225, linePos - 1, 55, 19), "=|", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.includeAllGlyphs = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Include all glyphs in font (otherwise just selection)", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.newTab = vanilla.CheckBox((inset + 2, linePos - 1, 140, 20), "Open tab with marks", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab = vanilla.CheckBox((inset + 140, linePos - 1, -inset, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Move", callback=self.MarkMoverMain)
		self.w.setDefaultButton(self.w.runButton)

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

				descriptionText = self.pref("descriptionText")
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
