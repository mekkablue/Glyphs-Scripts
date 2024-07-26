# MenuTitle: Adjust Kerning in master
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:  # noqa: F841
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__ = """
Adjusts all kerning values by a specified amount.
"""

import vanilla
from GlyphsApp import Glyphs, GSLTR, GSRTL
from mekkablue import mekkaObject

optionList = ("Multiply by", "Add", "Add Absolute", "Round by", "Limit to")


class AdjustKerning(mekkaObject):
	prefID = "com.mekkablue.AdjustKerning"
	prefDict = {
		"doWhat": 0,
		"howMuch": 20,
		"positive": True,
		"zero": True,
		"negative": True,
	}

	def __init__(self):
		# GUI:
		windowWidth = 260
		windowHeight = 155
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value

		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Adjust Kerning",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 10, 12, 22
		self.w.text_1 = vanilla.TextBox((inset - 1, linePos + 2, -inset, 14), "In the current font master, do this:", sizeStyle='small')

		linePos += lineHeight
		self.w.doWhat = vanilla.PopUpButton((inset, linePos, 100, 17), optionList, callback=self.SavePreferences, sizeStyle='small')
		self.w.howMuch = vanilla.EditText((inset + 100 + 10, linePos - 1, -inset, 19), "10", sizeStyle='small', callback=self.SavePreferences)

		linePos += lineHeight
		self.w.text_2 = vanilla.TextBox((inset - 1, linePos + 4, -inset, 14), "To these kerning pairs:", sizeStyle='small')

		linePos += lineHeight
		self.w.positive = vanilla.CheckBox((inset, linePos, 63, 20), "Positive,", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.zero = vanilla.CheckBox((inset + 65, linePos, 65, 20), "zero, and", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.negative = vanilla.CheckBox((inset + 137, linePos, -inset, 20), "negative pairs", value=True, callback=self.SavePreferences, sizeStyle='small')

		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Adjust", callback=self.AdjustKerningMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def nameForID(self, font, ID):
		try:
			if ID[0] == "@":  # is a group
				return ID
			else:  # is a glyph
				return font.glyphForId_(ID).name
		except Exception as e:
			raise e

	def userChoosesToProcessKerning(self, kernValue):
		try:
			if self.pref("positive") and kernValue > 0:
				return True
			elif self.pref("zero") and kernValue == 0:
				return True
			elif self.pref("negative") and kernValue < 0:
				return True
			else:
				return False
		except Exception as e:
			raise e

	def AdjustKerningMain(self, sender):
		try:
			font = Glyphs.font
			master = font.selectedFontMaster
			masterID = master.id
			value = float(self.pref("howMuch"))

			font.disableUpdateInterface()
			try:
				for i, directionalKerning in enumerate((font.kerningLTR, font.kerningRTL)):
					if not masterID in directionalKerning.keys():
						print(f"No kerning in {('LTR', 'RTL')[i]} direction on master ‘{master.name}’.")
						continue
					
					currentDirection = (GSLTR, GSRTL)[i]
					masterKernDict = directionalKerning[masterID]
					
					if self.pref("doWhat") == 0:
						for leftGlyphID in masterKernDict.keys():
							leftName = self.nameForID(font, leftGlyphID)
							for rightGlyphID in masterKernDict[leftGlyphID].keys():
								originalKerning = masterKernDict[leftGlyphID][rightGlyphID]
								if self.userChoosesToProcessKerning(originalKerning):
									rightName = self.nameForID(font, rightGlyphID)
									font.setKerningForPair(masterID, leftName, rightName, originalKerning * value, direction=currentDirection)

					elif self.pref("doWhat") == 1:
						for leftGlyphID in masterKernDict.keys():
							leftName = self.nameForID(font, leftGlyphID)
							for rightGlyphID in masterKernDict[leftGlyphID].keys():
								originalKerning = masterKernDict[leftGlyphID][rightGlyphID]
								if self.userChoosesToProcessKerning(originalKerning):
									rightName = self.nameForID(font, rightGlyphID)
									font.setKerningForPair(masterID, leftName, rightName, originalKerning + value, direction=currentDirection)

					elif self.pref("doWhat") == 2:
						for leftGlyphID in masterKernDict.keys():
							leftName = self.nameForID(font, leftGlyphID)
							for rightGlyphID in masterKernDict[leftGlyphID].keys():
								originalKerning = masterKernDict[leftGlyphID][rightGlyphID]
								if self.userChoosesToProcessKerning(originalKerning):
									rightName = self.nameForID(font, rightGlyphID)
									if originalKerning < 0:
										factor = -1
									else:
										factor = 1
									font.setKerningForPair(masterID, leftName, rightName, originalKerning + factor * value, direction=currentDirection)

					elif self.pref("doWhat") == 3:
						for leftGlyphID in masterKernDict.keys():
							leftName = self.nameForID(font, leftGlyphID)
							for rightGlyphID in masterKernDict[leftGlyphID].keys():
								originalKerning = masterKernDict[leftGlyphID][rightGlyphID]
								if self.userChoosesToProcessKerning(originalKerning):
									rightName = self.nameForID(font, rightGlyphID)
									font.setKerningForPair(masterID, leftName, rightName, round(originalKerning / value, 0) * value, direction=currentDirection)

					elif self.pref("doWhat") == 4:
						for left in masterKernDict.keys():
							for right in masterKernDict[left].keys():
								originalKerning = masterKernDict[left][right]
								if self.userChoosesToProcessKerning(originalKerning):
									if originalKerning > abs(value):
										masterKernDict[left][right] = abs(value)
									elif originalKerning < -abs(value):
										masterKernDict[left][right] = -abs(value)

			except Exception as e:
				Glyphs.showMacroWindow()
				print("\n⚠️ Script Error:\n")
				import traceback
				print(traceback.format_exc())
				print()
				raise e

			finally:
				font.enableUpdateInterface()  # re-enables UI updates in Font View

			self.SavePreferences()
		except Exception as e:
			raise e


AdjustKerning()
