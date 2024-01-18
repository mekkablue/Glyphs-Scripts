# MenuTitle: Adjust Sidebearings
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Multiply, increase/decrease, limit or round spacing, differentiate between negative and positive SBs.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject


choices = (
	"Multiply by",
	"Add units",
	"Round by",
	"Limit to",
	"Add percent",
)

negativeChoices = (
	"Same as positive",
	"Reverse",
	"Reverse 50%",
)


class AdjustSpacing(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"choice": 0,
		"value": 5,
		"negativeChoice": 0,
		"treatPositiveSBs": 1,
		"treatNegativeSBs": 1,
		"applyToAllMasters": 0,
		"applyToAllGlyphs": 1,
		"updateMetricsKeys": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 310
		windowHeight = 225
		windowWidthResize = 200  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Adjust Spacing",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Treat sidebearings in frontmost font:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.choice = vanilla.PopUpButton((inset, linePos, 125, 21), choices, sizeStyle="regular", callback=self.SavePreferences)
		self.w.value = vanilla.EditText((inset + 130, linePos - 1, -inset, 21), "2", callback=self.SavePreferences, sizeStyle="regular")
		linePos += lineHeight + 3

		self.w.treatSBsText1 = vanilla.TextBox((inset, linePos + 2, 55, 14), "Apply to", sizeStyle="small", selectable=True)
		self.w.treatPositiveSBs = vanilla.CheckBox((inset + 55, linePos - 1, 60, 20), "positive", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.treatNegativeSBs = vanilla.CheckBox((inset + 120, linePos - 1, -inset, 20), "negative sidebearings", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.treatSBsText2 = vanilla.TextBox((inset, linePos + 2, 110, 14), "Negative treatment:", sizeStyle="small", selectable=True)
		self.w.negativeChoice = vanilla.PopUpButton((inset + 110, linePos, -inset, 17), negativeChoices, sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		self.w.updateMetricsKeys = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Update metrics keys and auto-alignments", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.applyToAllMasters = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include ⚠️ ALL masters (otherwise current only)", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.applyToAllGlyphs = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include ⚠️ ALL glyphs (otherwise selected only)", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Adjust", sizeStyle="regular", callback=self.AdjustSpacingMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.pref("treatPositiveSBs") or self.pref("treatNegativeSBs"))
		self.w.negativeChoice.enable(self.pref("choice") != 3 and self.pref("treatNegativeSBs"))

	def treatSB(self, choice, SB, value, negativeValue, treatPositiveSBs=True, treatNegativeSBs=True):
		if SB >= 0 and treatPositiveSBs:
			if choice == 0:
				# Multiply by
				SB *= value
			elif choice == 1:
				# Add units
				SB += value
			elif choice == 2:
				# Round by
				SB = round(SB / value) * value
			elif choice == 3:
				# Limit to
				SB = min(SB, abs(value))
			elif choice == 4:
				# Add percent
				SB *= (1 + value / 100)
		elif SB < 0 and treatNegativeSBs:
			if choice == 0:
				# Multiply by
				SB *= negativeValue
			elif choice == 1:
				# Add
				SB += negativeValue
			elif choice == 2:
				# Round by
				SB = round(SB / value) * value
			elif choice == 3:
				# Limit to
				SB = max(SB, -abs(negativeValue))
			elif choice == 4:
				# Add percent
				SB *= (1 + negativeValue / 100)
		return SB

	def AdjustSpacingMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			choice = self.pref("choice")
			value = self.prefFloat("value")
			negativeChoice = self.pref("negativeChoice")
			treatPositiveSBs = self.prefBool("treatPositiveSBs")
			treatNegativeSBs = self.prefBool("treatNegativeSBs")
			applyToAllMasters = self.prefBool("applyToAllMasters")
			applyToAllGlyphs = self.prefBool("applyToAllGlyphs")
			updateMetricsKeys = self.prefBool("updateMetricsKeys")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Adjust Spacing Report for {reportName}")
				print()

				if applyToAllGlyphs:
					glyphs = thisFont.glyphs
				else:
					glyphs = [layer.parent for layer in thisFont.selectedLayers]

				negativeValue = value
				if negativeChoice == 1:
					if choice == 0:  # multiply
						negativeValue = 1 / value
					else:
						negativeValue = -value
				elif negativeChoice == 2:
					if choice == 0:  # multiply
						negativeValue = 1 / value * 2
					else:
						negativeValue = -value / 2

				currentMasterID = thisFont.selectedFontMaster.id
				for thisGlyph in glyphs:
					for thisLayer in thisGlyph.layers:
						oldSBs = (thisLayer.LSB, thisLayer.RSB)

						if not (thisLayer.isMasterLayer or thisLayer.isSpecialLayer):
							continue
						if not (applyToAllMasters or thisLayer.associatedMasterId == currentMasterID):
							continue
						if thisLayer.hasAlignedWidth():
							continue

						thisLayer.LSB = self.treatSB(choice, thisLayer.LSB, value, negativeValue, treatPositiveSBs, treatNegativeSBs)
						thisLayer.RSB = self.treatSB(choice, thisLayer.RSB, value, negativeValue, treatPositiveSBs, treatNegativeSBs)
						newSBs = (thisLayer.LSB, thisLayer.RSB)
						if oldSBs != newSBs:
							print(f"🔡 {thisGlyph.name} ({thisLayer.name}): \tLSB {int(oldSBs[0])}→{int(newSBs[0])} \tRSB {int(oldSBs[1])}→{int(newSBs[1])}")

				if updateMetricsKeys:
					for thisGlyph in glyphs:
						for thisLayer in thisGlyph.layers:
							if not (thisLayer.isMasterLayer or thisLayer.isSpecialLayer):
								continue
							if not (applyToAllMasters or thisLayer.associatedMasterId == currentMasterID):
								continue

							thisLayer.doAlignWidth()
							thisLayer.syncMetrics()

				# self.w.close()  # delete if you want window to stay open

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Adjust Spacing Error: {e}")
			import traceback
			print(traceback.format_exc())


AdjustSpacing()
