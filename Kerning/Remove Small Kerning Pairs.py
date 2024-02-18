# MenuTitle: Remove Small Kerning Pairs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Specify a kerning value, and every kerning in the current master smaller than that will be removed.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


def nameForID(Font, ID):
	"""Return the name of a group or glyph for a given kerning ID."""
	try:
		if ID[0] == "@":  # is a group
			return ID
		else:  # is a glyph
			return Font.glyphForId_(ID).name
	except Exception as e:
		raise e


class DeleteSmallKerningPairs(mekkaObject):
	prefDict = {
		"howMuch": "10",
		"positive": True,
		"zero": False,
		"negative": True,
		"glyphToGlyph": True,
		"glyphToClass": True,
		"classToClass": True,
		"keepWindow": True,
	}

	def __init__(self):
		# Window 'self.w':
		offset = 10
		line = 20

		windowWidth = 325
		windowHeight = 2 * offset + 8 * line
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove Small Kerning Pairs",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		self.w.text_1 = vanilla.TextBox((15 - 1, offset + 2, -15, line), "In the current font master, delete all pairs smaller than:", sizeStyle='small')
		self.w.howMuch = vanilla.EditText((15 - 1, offset + line + 1, -15, line), "10", sizeStyle='small', callback=self.SavePreferences)

		self.w.text_2 = vanilla.TextBox((15 - 1, offset * 2 + line * 2 + 2, -15, line), "Only delete:", sizeStyle='small')
		self.w.positive = vanilla.CheckBox((25, offset * 2 + line * 3, -15, line), "Positive,", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.zero = vanilla.CheckBox((90, offset * 2 + line * 3, -15, line), "zero, and", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.negative = vanilla.CheckBox((162, offset * 2 + line * 3, -15, line), "negative pairs", value=True, callback=self.SavePreferences, sizeStyle='small')

		self.w.glyphToGlyph = vanilla.CheckBox((25, offset * 2 + line * 4, -15, line), "Glyph-glyph", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.glyphToClass = vanilla.CheckBox((115, offset * 2 + line * 4, -15, line), "Glyph-class", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.classToClass = vanilla.CheckBox((205, offset * 2 + line * 4, -15, line), "Class-class", value=True, callback=self.SavePreferences, sizeStyle='small')

		self.w.keepWindow = vanilla.CheckBox((25, offset * 2 + line * 5, -15, line), "Keep window open", value=True, callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - 15, -20 - 15, -15, -15), "Remove", callback=self.DeleteSmallKerningPairsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def DeleteSmallKerningPairsMain(self, sender):
		try:
			self.SavePreferences()

			# brings macro window:
			Glyphs.showMacroWindow()

			# read the user entry:
			shouldRemovePositive = self.prefBool("positive")
			shouldRemoveZero = self.prefBool("zero")
			shouldRemoveNegative = self.prefBool("negative")
			shouldRemoveGlyphToGlyph = self.prefBool("glyphToGlyph")
			shouldRemoveGlyphToClass = self.prefBool("glyphToClass")
			shouldRemoveClassToClass = self.prefBool("classToClass")
			keepWindowOpen = self.prefBool("keepWindow")
			try:
				# convert to positive decimal number:
				maxKernValue = abs(float(self.w.howMuch.get()))
			except:
				# bad entry, default to 0 (could be left empty for zero pairs only):
				maxKernValue = 0.0

			# set the variables:
			thisFont = Glyphs.font  # frontmost font
			thisFontMaster = thisFont.selectedFontMaster  # active master
			thisFontMasterID = thisFontMaster.id  # active master ID
			thisFontMasterKernDict = thisFont.kerning[thisFontMasterID]  # kerning dictionary

			if ((shouldRemovePositive or shouldRemoveNegative) and maxKernValue) or shouldRemoveZero:
				willRemove = "kernings smaller than %i" % maxKernValue
				if shouldRemoveZero and ((not maxKernValue) or (not shouldRemoveNegative and not shouldRemovePositive)):
					willRemove = "zero kernings"
				print("Deleting %s in %s %s..." % (willRemove, thisFont.familyName, thisFontMaster.name))

				# collect pairs to be removed:
				kernpairsToBeRemoved = []
				countZero = 0
				countPositive = 0
				countNegative = 0
				for leftGlyphID in thisFontMasterKernDict.keys():
					for rightGlyphID in thisFontMasterKernDict[leftGlyphID].keys():

						countClasses = 0
						if leftGlyphID.startswith("@"):
							countClasses += 1
						if rightGlyphID.startswith("@"):
							countClasses += 1

						if (shouldRemoveGlyphToGlyph and countClasses == 0) or \
							(shouldRemoveGlyphToClass and countClasses == 1) or \
							(shouldRemoveClassToClass and countClasses == 2):

							kerningValue = thisFontMasterKernDict[leftGlyphID][rightGlyphID]
							leftName = nameForID(thisFont, leftGlyphID)
							rightName = nameForID(thisFont, rightGlyphID)

							if shouldRemoveZero and kerningValue == 0.0:
								kernpairsToBeRemoved.append((leftName, rightName))
								countZero += 1
							elif shouldRemovePositive and 0.0 < kerningValue < maxKernValue:
								kernpairsToBeRemoved.append((leftName, rightName))
								countPositive += 1
							elif shouldRemoveNegative and 0.0 > kerningValue > -maxKernValue:
								kernpairsToBeRemoved.append((leftName, rightName))
								countNegative += 1

				# remove the pairs:
				for thisKernPair in kernpairsToBeRemoved:
					leftSide = thisKernPair[0]
					rightSide = thisKernPair[1]
					thisFont.removeKerningForPair(thisFontMasterID, leftSide, rightSide)
				print("   Removed %i kerning pairs:" % len(kernpairsToBeRemoved))
				print("   %i negative pairs" % countNegative)
				print("   %i zero pairs" % countZero)
				print("   %i positive pairs" % countPositive)
				print("Done.")
			else:
				print("Note: No kerning removed, because no options were picked.")

			if not keepWindowOpen:
				self.w.close()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Delete Small Kerning Pairs Error: %s" % e)


# clear macro window log:
Glyphs.clearLog()

# execute GUI:
DeleteSmallKerningPairs()
