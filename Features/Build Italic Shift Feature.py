# MenuTitle: Build Italic Shift Feature
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates and inserts GPOS feature code for shifting glyphs, e.g., parentheses and punctuation for the case feature.
"""

import vanilla
from GlyphsApp import Glyphs, GSFeature
from mekkaCore import italicize


def updatedCode(oldCode, beginSig, endSig, newCode):
	"""Replaces text in oldCode with newCode, but only between beginSig and endSig."""
	beginOffset = oldCode.find(beginSig)
	endOffset = oldCode.find(endSig) + len(endSig)
	newCode = oldCode[:beginOffset] + beginSig + newCode + "\n" + endSig + oldCode[endOffset:]
	return newCode


def createOTFeature(featureName="case", featureCode="# empty feature code", targetFont=Glyphs.font, codeSig="SHIFTED-GLYPHS"):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	featureName: name of the feature (str),
	featureCode: the AFDKO feature code (str),
	targetFont: the GSFont object receiving the feature,
	codeSig: the code signature (str) used as delimiters.
	"""

	beginSig = "# BEGIN " + codeSig + "\n"
	endSig = "# END " + codeSig + "\n"

	if featureName in [f.name for f in targetFont.features]:
		# feature already exists:
		targetFeature = targetFont.features[featureName]
		targetFeature.automatic = 0

		# FEATURE:
		if beginSig in targetFeature.code:
			targetFeature.code = updatedCode(targetFeature.code, beginSig, endSig, featureCode)
		else:
			targetFeature.code += "\n" + beginSig + featureCode + "\n" + endSig

		# NOTES:
		if beginSig in targetFeature.notes:
			targetFeature.notes = updatedCode(targetFeature.notes, beginSig, endSig, featureCode)
		else:
			targetFeature.notes += "\n" + beginSig + featureCode + "\n" + endSig

		return "Updated existing OT feature '%s'." % featureName
	else:
		# create feature with new code:
		newFeature = GSFeature()
		newFeature.name = featureName
		newCode = beginSig + featureCode + "\n" + endSig
		newFeature.code = newCode
		newFeature.notes = newCode
		targetFont.features.append(newFeature)
		return "Created new OT feature '%s'" % featureName


class ItalicShiftFeature(object):
	prefDict = {
		"edit_1a": "case",
		"edit_1b": "100",
		"edit_1c": "exclamdown questiondown",
		"edit_2a": "case",
		"edit_2b": "50",
		"edit_2c": "parenleft parenright braceleft braceright bracketleft bracketright",
		"edit_3a": "",
		"edit_3b": "",
		"edit_3c": "",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 440
		windowHeight = 160
		windowWidthResize = 600  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Italic Shift Feature",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 15
		lineStep = 22
		lineheight = 12
		self.w.text_1 = vanilla.TextBox((inset - 1, lineheight + 2, -inset, 14), "Insert GPOS lookup for shifting punctuation in italic angle of 1st master:", sizeStyle='small')

		lineheight += lineStep
		self.w.edit_1a = vanilla.EditText((inset, lineheight, 70, 19), "case", sizeStyle='small', placeholder="smcp,c2sc", callback=self.SavePreferences)
		self.w.edit_1b = vanilla.EditText((75 + inset, lineheight, 55, 19), "100", sizeStyle='small', placeholder="80", callback=self.SavePreferences)
		self.w.edit_1c = vanilla.EditText((75 + 75, lineheight, -inset, 19), "exclamdown questiondown", sizeStyle='small', placeholder="parenleft parenright bracketleft bracketright", callback=self.SavePreferences)

		lineheight += lineStep
		self.w.edit_2a = vanilla.EditText((inset, lineheight, 70, 19), "case", sizeStyle='small', placeholder="smcp,c2sc", callback=self.SavePreferences)
		self.w.edit_2b = vanilla.EditText((75 + inset, lineheight, 55, 19), "50", sizeStyle='small', placeholder="80", callback=self.SavePreferences)
		self.w.edit_2c = vanilla.EditText((75 + 75, lineheight, -inset, 19), "parenleft parenright braceleft braceright bracketleft bracketright", sizeStyle='small', placeholder="parenleft parenright bracketleft bracketright", callback=self.SavePreferences)

		lineheight += lineStep
		self.w.edit_3a = vanilla.EditText((inset, lineheight, 70, 19), "", sizeStyle='small', placeholder="smcp,c2sc", callback=self.SavePreferences)
		self.w.edit_3b = vanilla.EditText((75 + inset, lineheight, 55, 19), "", sizeStyle='small', placeholder="80", callback=self.SavePreferences)
		self.w.edit_3c = vanilla.EditText((75 + 75, lineheight, -inset, 19), "", sizeStyle='small', placeholder="parenleft parenright bracketleft bracketright", callback=self.SavePreferences)

		# Run Button:
		self.w.copyButton = vanilla.Button((-180 - inset, -20 - inset, -inset - 90, -inset), "Copy Code", sizeStyle='regular', callback=self.ItalicShiftFeatureMain)
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Insert", sizeStyle='regular', callback=self.ItalicShiftFeatureMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def ItalicShiftFeatureMain(self, sender):
		try:
			thisFont = Glyphs.font  # frontmost font
			firstMaster = thisFont.masters[0]
			italicAngle = firstMaster.italicAngle
			features = {}

			for lookupIndex in (1, 2, 3):
				otFeature = self.pref("edit_%ia" % lookupIndex)
				verticalShift = self.pref("edit_%ib" % lookupIndex)
				glyphNames = self.pref("edit_%ic" % lookupIndex)

				if otFeature and len(otFeature) > 3 and glyphNames:
					if verticalShift:
						verticalShift = int(verticalShift)
						if verticalShift != 0:
							otCode = "\tpos [%s] <%i %i 0 0>;\n" % (glyphNames, italicize(pivotalY=verticalShift, italicAngle=italicAngle), verticalShift)

							if otFeature in features:
								features[otFeature] += otCode
							else:
								features[otFeature] = otCode

			for otFeature in features.keys():
				lookupName = "italicShift_%s" % otFeature
				otCode = "lookup %s {\n" % lookupName
				otCode += features[otFeature]
				otCode += "} %s;" % lookupName
				createOTFeature(
					featureName=otFeature,
					codeSig="ITALIC-SHIFT-%s" % otFeature.upper(),
					targetFont=thisFont,
					featureCode=otCode,
				)

			self.SavePreferences()

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Italic Shift Feature Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ItalicShiftFeature()
