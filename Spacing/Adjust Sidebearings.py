# MenuTitle: Adjust Sidebearings
__doc__ = """
Multiply, increase/decrease, limit or round spacing, differentiate between negative and positive SBs.
"""

import vanilla
from mekkablue import mekkaObject, reportFontName, SteppingEditText, decimalFormatter
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)


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
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Adjust Spacing",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Treat sidebearings in frontmost font:", sizeStyle="small", selectable=True)

		formatter = decimalFormatter(fractionDigits=3)
		self.w.choice = vanilla.PopUpButton("auto", choices, callback=self.SavePreferences)
		self.w.value = SteppingEditText("auto", "2", callback=self.SavePreferences, formatter=formatter)

		self.w.treatSBsText1 = vanilla.TextBox("auto", "Apply to", sizeStyle="small", selectable=True)
		self.w.treatPositiveSBs = vanilla.CheckBox("auto", "positive", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.treatNegativeSBs = vanilla.CheckBox("auto", "negative sidebearings", value=False, callback=self.SavePreferences, sizeStyle="small")

		self.w.treatSBsText2 = vanilla.TextBox("auto", "Negative treatment:", sizeStyle="small", selectable=True)
		self.w.negativeChoice = vanilla.PopUpButton("auto", negativeChoices, sizeStyle="small", callback=self.SavePreferences)

		self.w.updateMetricsKeys = vanilla.CheckBox("auto", "Update metrics keys and auto-alignments", value=False, callback=self.SavePreferences, sizeStyle="small")

		self.w.applyToAllMasters = vanilla.CheckBox("auto", "Include ⚠️ ALL masters (otherwise current only)", value=False, callback=self.SavePreferences, sizeStyle="small")

		self.w.applyToAllGlyphs = vanilla.CheckBox("auto", "Include ⚠️ ALL glyphs (otherwise selected only)", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Adjust", callback=self.AdjustSpacingMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and share one width, so the controls behind them line up:
		for label in (self.w.treatSBsText1, self.w.treatSBsText2):
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[choice(125)]-gap-[value]-inset-|",
				"H:|-inset-[treatSBsText1]-gap-[treatPositiveSBs]-gap-[treatNegativeSBs]-(>=inset)-|",
				"H:|-inset-[treatSBsText2]-gap-[negativeChoice]-inset-|",
				"H:|-inset-[updateMetricsKeys]-(>=inset)-|",
				"H:|-inset-[applyToAllMasters]-(>=inset)-|",
				"H:|-inset-[applyToAllGlyphs]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[choice]-gap-[treatPositiveSBs]-row-[negativeChoice]-row-[updateMetricsKeys]-checkRow-[applyToAllMasters]-checkRow-[applyToAllGlyphs]-inset-[runButton]-inset-|",
				{"view1": self.w.value, "attribute1": "centerY", "view2": self.w.choice, "attribute2": "centerY"},
				{"view1": self.w.treatSBsText1, "attribute1": "centerY", "view2": self.w.treatPositiveSBs, "attribute2": "centerY"},
				{"view1": self.w.treatNegativeSBs, "attribute1": "centerY", "view2": self.w.treatPositiveSBs, "attribute2": "centerY"},
				{"view1": self.w.treatSBsText2, "attribute1": "centerY", "view2": self.w.negativeChoice, "attribute2": "centerY"},
				{"view1": self.w.treatSBsText1, "attribute1": "width", "view2": self.w.treatSBsText2, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

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
			elif value == 0 and (choice == 2 or (choice == 0 and negativeChoice != 0)):
				# rounding by zero, or the reciprocal of a zero factor, would divide by zero
				Message(title="Invalid Value", message=f"‘{choices[choice]}’ does not work with a value of 0. Please enter a different value.", OKButton=None)
			else:
				reportName = reportFontName(thisFont)
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
