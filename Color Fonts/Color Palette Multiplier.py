#MenuTitle: Color Palette Multiplier
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Apply a list of filter parameters to copies of CPAL/COLR layers. This way you can derive a shadow layer from a front layer, for example.
"""

import vanilla
import sys
from mekkablue import mekkaObject, UpdateButton
from GlyphsApp import Glyphs, GSLayer, GSCustomParameter, Message
from Foundation import NSString
from AppKit import NSFont
from copy import copy

filterPrefix = """
{
	customParameters = (
		{
			name = Filter;
			value = "
"""

prefilterPrefix = """
{
	customParameters = (
		{
			name = PreFilter;
			value = "
"""

filterSuffix = """
";
		}
	);
}
"""

def extractNumber(s):
	while len(s) > 0 and not s.isdigit():
		if not s[0].isdigit():
			s = s[1:]
		if not s[-1].isdigit():
			s = s[:-1]
	return int(s)

def whitespaceAtBeginning(s):
	i = 0
	while i < len(s) and s[i].isspace():
		i += 1
	return s[:i]

def lastIndentOfText(text):
	indent = ""
	lines = text.splitlines()
	if len(lines) >=2:
		indent = whitespaceAtBeginning(lines[-2])
	return indent

class ColorPaletteMultiplier(mekkaObject):
	prefID = "com.mekkablue.ColorPaletteMultiplier"
	prefDict = {
		# "prefName": defaultValue,
		"build": "# Color 1\nOffsetCurve;10;10;0;0.5;keep;\nExtrude;50;-46",
		"derive": 0,
		"allGlyphs": 0,
		"overwrite": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 280
		windowHeight = 360
		windowWidthResize = 400  # user can resize width by this value
		windowHeightResize = 1000   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Color Palette Multiplier",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.deriveText = vanilla.TextBox((inset, linePos+2, 70, 14), "Derive from", sizeStyle="small", selectable=True)
		self.w.derive = vanilla.PopUpButton((inset+70, linePos, -inset-22, 17), self.currentColors(), sizeStyle="small", callback=self.SavePreferences)
		self.w.deriveUpdate = UpdateButton((-inset-16, linePos-3, -inset, 18), callback=self.updateDerive)
		linePos += lineHeight

		self.w.allGlyphs = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Apply to all glyphs (otherwise selected only)", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.overwrite = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Overwrite preexisting target colors", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.descriptionText = vanilla.TextBox((inset, linePos+2, -inset, 14), "Build target colors with filter parameters:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.build = vanilla.TextEditor((1, linePos, -1, -40), "", callback=self.CleanInputAndSavePreferences)
		self.w.build.getNSTextView().setFont_(NSFont.userFixedPitchFontOfSize_(14.0))
		self.w.build.getNSTextView().turnOffLigatures_(1)
		self.w.build.getNSTextView().useStandardLigatures_(0)
		self.w.build.selectAll()
	
		# Action Button:
		actionItems = (
			{"title": "Add RemoveOverlap", "callback":self.removeOverlaps},
			{"title": "Add CorrectPathDirections", "callback":self.correctPathDirections},
			{"title": "Add TurnAllPathsClockwise", "callback":self.turnAllPathsClockwise},
			{"title": "Add TurnAllPathsCounterClockwise", "callback":self.turnAllPathsCounterClockwise},
		)
		self.w.ActionButton = vanilla.ActionButton((inset, -20-inset, 40, 20), actionItems, sizeStyle="regular")
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Build", sizeStyle="regular", callback=self.ColorPaletteMultiplierMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def CleanInputAndSavePreferences(self, sender=None):
		currentText = self.w.build.get()
		originalText = currentText
		for replaceString in (filterPrefix, filterSuffix, prefilterPrefix):
			currentText = currentText.replace(replaceString, "")
			replaceString = replaceString.strip()
			currentText = currentText.replace(replaceString, "")
		if originalText != currentText:
			self.w.build.set(currentText)
		self.SavePreferences()

	def removeOverlaps(self, sender=None):
		self.addLine(content="RemoveOverlap")
	
	def correctPathDirections(self, sender=None):
		self.addLine(content="CorrectPathDirections")
	
	def turnAllPathsClockwise(self, sender=None):
		self.addLine(content="TurnAllPathsClockwise")
	
	def turnAllPathsCounterClockwise(self, sender=None):
		self.addLine(content="TurnAllPathsCounterClockwise")
	
	def addLine(self, sender=None, content=""):
		if not content:
			return

		currentText = self.w.build.get()
		if currentText[-1] != "\n":
			currentText += "\n"

		indent = lastIndentOfText(currentText)
		currentText += f"{indent}{content.strip()}\n"
		self.w.build.set(currentText)
		self.SavePreferences()

	def currentColors(self, sender=None):
		font = Glyphs.font
		if not font:
			return []
		for parameter in font.customParameters:
			if parameter.name != "Color Palettes":
				continue
			return [f"Color {i}" for i in range(len(parameter.value[0]))]
		return []

	def updateDerive(self, sender=None):
		self.w.derive.setItems(self.currentColors())

	def ColorPaletteMultiplierMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Color Palette Multiplier’ could not write preferences.")

			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)

			buildOrder = []
			for buildLine in build.strip().splitlines():
				buildLine = buildLine.strip()
				if not buildLine:
					continue
				if buildLine[0] == "#":
					buildOrder.append(extractNumber(buildLine))
				else:
					filterString = buildLine.strip().strip(";")
					if filterString in ("CorrectPathDirections", "TurnAllPathsClockwise", "TurnAllPathsCounterClockwise"):
						buildOrder.append(filterString)
					else:
						customParameter = GSCustomParameter(name="Filter", value=filterString)
						buildOrder.append(customParameter)

			if not buildOrder:
				Message(
					title="Input Error",
					message="Could not parse the input. Try ‘# Color 1:’ for the target layers and filter parameter strings split into lines below.",
					OKButton=None,
				)
				return

			targetColors = set([i for i in buildOrder if isinstance(i, int)])
			print("targetColors", targetColors)

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Color Palette Multiplier Report for {reportName}")
				print()

				if self.pref("allGlyphs"):
					theseGlyphs = thisFont.glyphs
				else:
					theseGlyphs = [l.parent for l in thisFont.selectedLayers if isinstance(l, GSLayer)]

				derive = int(self.pref("derive"))
				for thisGlyph in theseGlyphs:
					layerCount = 0
					for layerIndex in range(len(thisGlyph.layers)-1, -1, -1):
						thisLayer = thisGlyph.layers[layerIndex]

						# remove layers to be regenerated
						if self.pref("overwrite") and thisLayer.attributes["colorPalette"] in buildOrder:
							del thisGlyph.layers[layerIndex]
							continue

						# process layer duplicates and insert them
						if thisLayer.attributes and thisLayer.attributes["colorPalette"] == derive:
							print(thisLayer)
							# colorPalette = 0
							for step in buildOrder:
								if isinstance(step, int):
									newLayer = copy(thisLayer)
									newLayer.attributes["colorPalette"] = step
									newLayer.layerId = NSString.UUID()
									# thisGlyph.layers.insert(layerIndex, newLayer)
									thisGlyph.insertObject_inLayersArrayAtIndex_(newLayer, layerIndex)
									layerCount += 1
								elif isinstance(step, str):
									step = step.strip()
									if step == "CorrectPathDirections":
										newLayer.correctPathDirection()
									elif step == "TurnAllPathsClockwise":
										for path in newLayer.paths:
											path.direction = 1
									elif step == "TurnAllPathsCounterClockwise":
										for path in newLayer.paths:
											path.direction = -1
								else:
									newLayer.applyCustomParameters_callbacks_font_error_([step], None, thisFont, None)

					print(f"🔡 {thisGlyph.name}: {layerCount} layer{'' if layerCount==1 else 's'} built.")

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Color Palette Multiplier Error: {e}")
			import traceback
			print(traceback.format_exc())


ColorPaletteMultiplier()
