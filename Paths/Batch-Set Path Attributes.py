# MenuTitle: Batch-Set Path Attributes
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Set path attributes of all paths in selected glyphs, the master, the font, etc.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject


def intOrNone(value):
	value = str(value)
	if "." in value:
		value = value[:value.find(".")]
	newValue = ""
	for letter in value:
		if letter in "0123456789":
			newValue += letter
	if newValue:
		return newValue
	return None


allAttributeNames = (
	"lineCapStart",
	"lineCapEnd",
	"strokeWidth",
	"strokeHeight",
	"strokePos",
)

strokePositions = {
	"center": None,
	"inside (left of path)": 1,
	"outside (right of path)": 0,
}
sortedStrokePositionNames = sorted(strokePositions.keys(), key=lambda thisListItem: "cio".find(thisListItem[0]))

scopeMaster = (
	"current master",
	"all masters",
)

scopeGlyphs = (
	"selected glyphs",
	"exporting glyphs",
	"all glyphs",
)


class BatchSetPathAttributes(mekkaObject):
	prefDict = {
		"scopeGlyphs": 0,
		"scopeMaster": 0,
		"lineCaps": 2,
		"strokeWidth": 20,
		"strokeHeight": "",
		"strokePos": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 210
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Batch-Set Path Attributes",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		indent = 70

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, indent, 14), "Attributes in", sizeStyle='small', selectable=True)
		self.w.scopeGlyphs = vanilla.PopUpButton((inset + indent, linePos, -inset, 17), scopeGlyphs, sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight
		self.w.scopeMasterText = vanilla.TextBox((inset, linePos + 2, indent, 14), "for paths on", sizeStyle='small', selectable=True)
		self.w.scopeMaster = vanilla.PopUpButton((inset + indent, linePos, -inset, 17), scopeMaster, sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight + 5

		indent = 80

		tooltip = "Width of the path in units."
		self.w.strokeWidthText = vanilla.TextBox((inset * 2, linePos + 2, indent, 14), "Stroke Width", sizeStyle='small', selectable=True)
		self.w.strokeWidthText.getNSTextField().setToolTip_(tooltip)
		self.w.strokeWidth = vanilla.EditText((inset * 2 + indent, linePos, -inset, 19), "20", callback=self.SavePreferences, sizeStyle='small')
		self.w.strokeWidth.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		tooltip = "Height of the path in units. Leave empty for monoline (width=height)."
		self.w.strokeHeightText = vanilla.TextBox((inset * 2, linePos + 2, indent, 14), "Stroke Height", sizeStyle='small', selectable=True)
		self.w.strokeHeightText.getNSTextField().setToolTip_(tooltip)
		self.w.strokeHeight = vanilla.EditText((inset * 2 + indent, linePos, -inset, 19), "20", callback=self.SavePreferences, sizeStyle='small')
		self.w.strokeHeight.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		tooltip = "0: right\n1: left\nempty: center (default)"
		self.w.strokePosText = vanilla.TextBox((inset * 2, linePos + 2, indent, 14), "Position", sizeStyle='small', selectable=True)
		self.w.strokePosText.getNSTextField().setToolTip_(tooltip)
		self.w.strokePos = vanilla.PopUpButton((inset * 2 + indent, linePos, -inset, 19), sortedStrokePositionNames, sizeStyle='small', callback=self.SavePreferences)
		# self.w.strokePos = vanilla.EditText( (inset*2+indent, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.strokePos.getNSPopUpButton().setToolTip_(tooltip)
		linePos += lineHeight

		tooltip = "0: straight cutoff\n1: round (wide)\n2: round (tight)\n3: square\n4: orthogonal\n\nEnter one number for both start and end, enter two comma-separated numbers (e.g. ‘2, 1’) for different caps at start and end."
		self.w.lineCapsText = vanilla.TextBox((inset * 2, linePos + 2, indent, 14), "Line Caps", sizeStyle='small', selectable=True)
		self.w.lineCapsText.getNSTextField().setToolTip_(tooltip)
		self.w.lineCaps = vanilla.EditText((inset * 2 + indent, linePos, -inset, 19), "2", callback=self.SavePreferences, sizeStyle='small')
		self.w.lineCaps.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		# Buttons at the bottom:
		self.w.extractButton = vanilla.Button((inset, -20 - inset, 80, -inset), "Extract", sizeStyle='regular', callback=self.extractAttributes)
		self.w.extractButton.getNSButton().setToolTip_("Extract attributes from currently selected path, or (if none are selected) from the first path in the current glyph.")

		self.w.removeButton = vanilla.Button((inset + 90, -20 - inset, 80, -inset), "Remove", sizeStyle='regular', callback=self.removeAttributes)
		self.w.removeButton.getNSButton().setToolTip_("Clears all path attributes for selection above.")

		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Apply", sizeStyle='regular', callback=self.BatchSetPathAttributesMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Batch-Set Path Attributes' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def glyphScopeErrorMsg(self, sender=None):
		Message(title="Glyph Scope Error", message="No applicable glyphs found. Please select the glyph scope and run the script again.", OKButton=None)

	def noFontOpenErrorMsg(self, sender=None):
		Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)

	def glyphsForCurrentScope(self, thisFont):
		scopeGlyphs = self.pref("scopeGlyphs")

		if scopeGlyphs == 0:
			# selected glyphs
			return [layer.parent for layer in thisFont.selectedLayers]
		elif scopeGlyphs == 1:
			# exporting glyphs
			return [g for g in thisFont.glyphs if g.export]
		elif scopeGlyphs == 2:
			# all glyphs
			return thisFont.glyphs

		return ()

	def extractAttributes(self, sender=None):
		try:
			thisFont = Glyphs.font
			if thisFont and thisFont.selectedLayers:
				currentLayer = thisFont.selectedLayers[0]

				currentPaths = [p for p in currentLayer.paths if p.selected]
				currentPath = None
				if currentPaths:
					currentPath = currentPaths[0]
				elif currentLayer.paths:
					currentPath = currentLayer.paths[0]
				else:
					Message(
						title="⚠️ No path selected",
						message="No path found for extracting attributes. Open a layer containing paths, select a specific path, and try again.",
						OKButton=None
					)

				if currentPath:
					lineCaps = []

					lineCapStart = currentPath.attributeForKey_("lineCapStart")
					if lineCapStart is not None:
						lineCaps.append(lineCapStart)

					lineCapEnd = currentPath.attributeForKey_("lineCapEnd")
					if lineCapEnd is not None:
						lineCaps.append(lineCapEnd)

					self.setPref("lineCaps", ", ".join([str(x) for x in set(lineCaps)]))

					strokeWidth = currentPath.attributeForKey_("strokeWidth")
					self.setPref("strokeWidth", strokeWidth)

					strokeHeight = currentPath.attributeForKey_("strokeHeight")
					self.setPref("strokeHeight", strokeHeight)

					strokePos = currentPath.attributeForKey_("strokePos")
					strokePosPrefValue = None
					for key in strokePositions.keys():
						value = strokePositions[key]
						if strokePos == value:
							strokePosPrefValue = sortedStrokePositionNames.index(key)
					self.setPref("strokePos", strokePosPrefValue)

			self.LoadPreferences()
		except Exception as e:  # noqa: F841
			# brings macro window to front and clears its log:
			Glyphs.showMacroWindow()
			print("\n⚠️ The ‘Batch-Set Path Attributes’ script encountered an error:\n")
			import traceback
			print(traceback.format_exc())

	def removeAttributes(self, sender=None):
		# clear macro window log:
		Glyphs.clearLog()

		# update settings to the latest user input:
		if not self.SavePreferences():
			print("Note: 'Batch-Set Path Attributes' could not write preferences.")

		thisFont = Glyphs.font  # frontmost font
		if thisFont is None:
			self.noFontOpenErrorMsg()
		else:
			print("Batch-Set Path Attributes Report for %s" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
			else:
				print("⚠️ The font file has not been saved yet.")
			print()

			scopeMaster = self.pref("scopeMaster")

			glyphs = self.glyphsForCurrentScope(thisFont)
			currentFontMasterID = thisFont.selectedFontMaster.id
			print("🔠 Clearing attributes in %i glyph%s...\n" % (
				len(glyphs),
				"" if len(glyphs) == 1 else "s",
			))

			if not glyphs:
				self.glyphScopeErrorMsg()
			else:
				for thisGlyph in glyphs:
					print("🙅‍♂️ Deleting attributes for: %s" % thisGlyph.name)
					for thisLayer in thisGlyph.layers:
						# scopeMaster: 0 = current master, 1 = all masters
						if scopeMaster == 1 or (scopeMaster == 0 and thisLayer.associatedMasterId == currentFontMasterID):
							if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
								for thisPath in thisLayer.paths:
									for attribute in allAttributeNames:
										thisPath.removeAttributeForKey_(attribute)

		# Final report:
		Glyphs.showNotification(
			"%s: Done" % (thisFont.familyName),
			"Finished removing path attributes. Details in Macro Window",
		)
		print("\nDone.")

	def BatchSetPathAttributesMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Batch-Set Path Attributes' could not write preferences.")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				self.noFontOpenErrorMsg()
			else:
				print("Batch-Set Path Attributes Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				scopeMaster = self.pref("scopeMaster")
				lineCaps = str(self.pref("lineCaps")).split(",")
				if lineCaps:
					lineCaps = [intOrNone(cap.strip()) for cap in lineCaps]
					if len(lineCaps) < 2:
						lineCaps = (lineCaps[0], lineCaps[0])
					elif len(lineCaps) > 2:
						lineCaps = lineCaps[:2]
				else:
					lineCaps = (None, None)

				strokeWidth = self.prefInt("strokeWidth")
				strokeHeight = self.pref("strokeHeight")
				strokePos = self.pref("strokePos")
				try:
					strokePosKey = sortedStrokePositionNames[strokePos]
					strokePos = strokePositions[strokePosKey]
				except:
					strokePos = None

				glyphs = self.glyphsForCurrentScope(thisFont)
				currentFontMasterID = thisFont.selectedFontMaster.id
				print("🔠 Setting attributes for %i glyph%s...\n" % (
					len(glyphs),
					"" if len(glyphs) == 1 else "s",
				))

				if not glyphs:
					self.glyphScopeErrorMsg()
				else:
					for thisGlyph in glyphs:
						print("💁‍♀️ Setting attributes for: %s" % thisGlyph.name)
						for thisLayer in thisGlyph.layers:
							# scopeMaster: 0 = current master, 1 = all masters
							if scopeMaster == 1 or (scopeMaster == 0 and thisLayer.associatedMasterId == currentFontMasterID):
								if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
									for thisPath in thisLayer.paths:
										# line caps for start and end:
										for capValue, startOrEnd in zip(lineCaps, ("lineCapStart", "lineCapEnd")):
											if capValue is None:
												thisPath.removeAttributeForKey_(startOrEnd)
											else:
												thisPath.setAttribute_forKey_(capValue, startOrEnd)

										# stroke width, height, pos:
										thisPath.setAttribute_forKey_(strokeWidth, "strokeWidth")

										if strokeHeight:  # default is None
											thisPath.setAttribute_forKey_(strokeHeight, "strokeHeight")
										else:
											thisPath.removeAttributeForKey_("strokeHeight")

										if strokePos is None:  # default is None
											thisPath.removeAttributeForKey_("strokePos")
										else:
											thisPath.setAttribute_forKey_(strokePos, "strokePos")

			# Final report:
			Glyphs.showNotification(
				"%s: Done" % (thisFont.familyName),
				"Batch-Set Path Attributes is finished. Details in Macro Window",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Batch-Set Path Attributes Error: %s" % e)
			import traceback
			print(traceback.format_exc())


BatchSetPathAttributes()
