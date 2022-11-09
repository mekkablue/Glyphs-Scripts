#MenuTitle: Mark Mover
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Move marks to their respective heights, e.g. *comb.case to cap height, *comb to x-height, etc.
"""

import vanilla

import math
from AppKit import NSAffineTransform, NSAffineTransformStruct
from Foundation import NSPoint

def italicize(thisPoint, italicAngle=0.0, pivotalY=0.0):
	"""
	Returns the italicized position of an NSPoint 'thisPoint'
	for a given angle 'italicAngle' and the pivotal height 'pivotalY',
	around which the italic slanting is executed, usually half x-height.
	Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
	"""
	x = thisPoint.x
	yOffset = thisPoint.y - pivotalY # calculate vertical offset
	italicAngle = math.radians(italicAngle) # convert to radians
	tangens = math.tan(italicAngle) # math.tan needs radians
	horizontalDeviance = tangens * yOffset # vertical distance from pivotal point
	x += horizontalDeviance # x of point that is yOffset from pivotal point
	return x

def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct() # returns the 6-float tuple
	Apply the matrix tuple like this:
		Layer.applyTransform(tMatrix)
		Component.applyTransform(tMatrix)
		Path.applyTransform(tMatrix)
	Chain multiple NSAffineTransform objects t1, t2 like this:
		t1.appendTransform_(t2)
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX, shiftY)
	if skew:
		skewStruct = NSAffineTransformStruct()
		skewStruct.m11 = 1.0
		skewStruct.m22 = 1.0
		skewStruct.m21 = math.tan(math.radians(skew))
		skewTransform = NSAffineTransform.transform()
		skewTransform.setTransformStruct_(skewStruct)
		myTransform.appendTransform_(skewTransform)
	return myTransform

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
			else:
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
			else:
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

class MarkMover(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 310
		windowHeight = 220
		windowWidthResize = 100 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Mark Mover", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.MarkMover.mainwindow" # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Move connecting anchors on metric line:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.lowercaseMarks = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Move …comb marks to x-height", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.uppercaseMarks = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Move …comb.case marks to cap height", value=True, callback=self.SavePreferences, sizeStyle='small'
			)
		linePos += lineHeight

		self.w.smallcapMarks = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Move …comb.sc to smallcap height", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.setMetricsKeys = vanilla.CheckBox((inset, linePos - 1, 140, 20), "Set metrics keys, LSB:", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.leftMetricsKey = vanilla.EditText((inset + 140, linePos - 1, 50, 19), "=40", callback=self.SavePreferences, sizeStyle='small')
		self.w.rightMetricsKeyText = vanilla.TextBox((inset + 197, linePos + 2, 30, 14), "RSB:", sizeStyle='small', selectable=True)
		self.w.rightMetricsKey = vanilla.EditText((inset + 230, linePos - 1, 50, 19), "=|", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.includeAllGlyphs = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Include all glyphs in font (otherwise just selection)", value=True, callback=self.SavePreferences, sizeStyle='small'
			)
		linePos += lineHeight

		self.w.newTab = vanilla.CheckBox((inset, linePos - 1, 140, 20), "Open tab with marks", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab = vanilla.CheckBox((inset + 140, linePos - 1, -inset, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Move", sizeStyle='regular', callback=self.MarkMoverMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Mark Mover' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		onOff = self.w.lowercaseMarks.get() or self.w.uppercaseMarks.get() or self.w.smallcapMarks.get()
		self.w.runButton.enable(onOff)

		onOff = self.w.setMetricsKeys.get()
		self.w.leftMetricsKey.enable(onOff)
		self.w.rightMetricsKey.enable(onOff)

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.MarkMover.lowercaseMarks"] = self.w.lowercaseMarks.get()
			Glyphs.defaults["com.mekkablue.MarkMover.uppercaseMarks"] = self.w.uppercaseMarks.get()
			Glyphs.defaults["com.mekkablue.MarkMover.smallcapMarks"] = self.w.smallcapMarks.get()
			Glyphs.defaults["com.mekkablue.MarkMover.setMetricsKeys"] = self.w.setMetricsKeys.get()
			Glyphs.defaults["com.mekkablue.MarkMover.leftMetricsKey"] = self.w.leftMetricsKey.get()
			Glyphs.defaults["com.mekkablue.MarkMover.rightMetricsKey"] = self.w.rightMetricsKey.get()
			Glyphs.defaults["com.mekkablue.MarkMover.includeAllGlyphs"] = self.w.includeAllGlyphs.get()
			Glyphs.defaults["com.mekkablue.MarkMover.newTab"] = self.w.newTab.get()
			Glyphs.defaults["com.mekkablue.MarkMover.reuseTab"] = self.w.reuseTab.get()

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.MarkMover.lowercaseMarks", 1)
			Glyphs.registerDefault("com.mekkablue.MarkMover.uppercaseMarks", 1)
			Glyphs.registerDefault("com.mekkablue.MarkMover.smallcapMarks", 0)
			Glyphs.registerDefault("com.mekkablue.MarkMover.setMetricsKeys", 0)
			Glyphs.registerDefault("com.mekkablue.MarkMover.leftMetricsKey", "=40")
			Glyphs.registerDefault("com.mekkablue.MarkMover.rightMetricsKey", "=|")
			Glyphs.registerDefault("com.mekkablue.MarkMover.includeAllGlyphs", 1)
			Glyphs.registerDefault("com.mekkablue.MarkMover.newTab", 1)
			Glyphs.registerDefault("com.mekkablue.MarkMover.reuseTab", 1)

			# load previously written prefs:
			self.w.lowercaseMarks.set(Glyphs.defaults["com.mekkablue.MarkMover.lowercaseMarks"])
			self.w.uppercaseMarks.set(Glyphs.defaults["com.mekkablue.MarkMover.uppercaseMarks"])
			self.w.smallcapMarks.set(Glyphs.defaults["com.mekkablue.MarkMover.smallcapMarks"])
			self.w.setMetricsKeys.set(Glyphs.defaults["com.mekkablue.MarkMover.setMetricsKeys"])
			self.w.leftMetricsKey.set(Glyphs.defaults["com.mekkablue.MarkMover.leftMetricsKey"])
			self.w.rightMetricsKey.set(Glyphs.defaults["com.mekkablue.MarkMover.rightMetricsKey"])
			self.w.includeAllGlyphs.set(Glyphs.defaults["com.mekkablue.MarkMover.includeAllGlyphs"])
			self.w.newTab.set(Glyphs.defaults["com.mekkablue.MarkMover.newTab"])
			self.w.reuseTab.set(Glyphs.defaults["com.mekkablue.MarkMover.reuseTab"])

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def MarkMoverMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Mark Mover' could not write preferences.")

			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Mark Mover Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")

				descriptionText = Glyphs.defaults["com.mekkablue.MarkMover.descriptionText"]
				lowercaseMarks = Glyphs.defaults["com.mekkablue.MarkMover.lowercaseMarks"]
				uppercaseMarks = Glyphs.defaults["com.mekkablue.MarkMover.uppercaseMarks"]
				smallcapMarks = Glyphs.defaults["com.mekkablue.MarkMover.smallcapMarks"]
				setMetricsKeys = Glyphs.defaults["com.mekkablue.MarkMover.setMetricsKeys"]
				leftMetricsKey = Glyphs.defaults["com.mekkablue.MarkMover.leftMetricsKey"]
				rightMetricsKey = Glyphs.defaults["com.mekkablue.MarkMover.rightMetricsKey"]
				includeAllGlyphs = Glyphs.defaults["com.mekkablue.MarkMover.includeAllGlyphs"]
				newTab = Glyphs.defaults["com.mekkablue.MarkMover.newTab"]
				reuseTab = Glyphs.defaults["com.mekkablue.MarkMover.reuseTab"]

				if includeAllGlyphs:
					glyphs = thisFont.glyphs
				else:
					glyphs = [l.parent for l in thisFont.selectedLayers]

				glyphNames = []
				movedMarks = 0
				for glyph in glyphs:
					glyphParts = glyph.name.split(".")
					if glyphParts[0].endswith("comb"):
						if setMetricsKeys:
							glyph.leftMetricsKey = leftMetricsKey
							glyph.rightMetricsKey = rightMetricsKey
						glyphNames.append(glyph.name)
						if "sc" in glyphParts or "smcp" in glyphParts or "c2sc" in glyphParts or "small" in glyphParts:
							movedMarks += moveGlyphToSmallCapHeight(glyph)
						elif "case" in glyphParts or "uc" in glyphParts:
							movedMarks += moveGlyphToCapHeight(glyph)
						else:
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
			print("Mark Mover Error: %s" % e)
			import traceback
			print(traceback.format_exc())

MarkMover()
