# MenuTitle: Adjust Sidebearings
__doc__ = """
Multiply, increase/decrease, limit or round spacing, differentiate between negative and positive SBs.
"""

import vanilla
from mekkablue import mekkaObject, reportFontName, SteppingEditText, decimalFormatter, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
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
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Treat sidebearings in frontmost font:", sizeStyle="small", selectable=True)

		formatter = decimalFormatter(fractionDigits=3)
		self.w.choice = vanilla.PopUpButton("auto", choices, callback=self.SavePreferences)
		self.w.choice.setToolTip("The kind of change applied to the sidebearings, using the value on the right.")
		self.w.value = SteppingEditText("auto", "2", callback=self.SavePreferences, formatter=formatter)
		self.w.value.setToolTip("The factor, number of units, rounding step, limit or percentage used by the chosen operation.")

		self.w.treatSBsText1 = vanilla.TextBox("auto", "Apply to", sizeStyle="small", selectable=True)
		self.w.treatPositiveSBs = vanilla.CheckBox("auto", "positive", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.treatPositiveSBs.setToolTip("Adjusts sidebearings that are positive (or zero).")
		self.w.treatNegativeSBs = vanilla.CheckBox("auto", "negative sidebearings", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.treatNegativeSBs.setToolTip("Adjusts sidebearings that are negative.")

		self.w.treatSBsText2 = vanilla.TextBox("auto", "Negative treatment:", sizeStyle="small", selectable=True)
		tooltipText = "How the value is applied to negative sidebearings: the same as for positive ones, reversed, or reversed and halved."
		self.w.treatSBsText2.setToolTip(tooltipText)
		self.w.negativeChoice = vanilla.PopUpButton("auto", negativeChoices, sizeStyle="small", callback=self.SavePreferences)
		self.w.negativeChoice.setToolTip(tooltipText)

		self.w.updateMetricsKeys = vanilla.CheckBox("auto", "Update metrics keys and auto-alignments", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.updateMetricsKeys.setToolTip("After adjusting, re-aligns widths and updates metrics keys of the processed layers.")

		self.w.applyToAllMasters = vanilla.CheckBox("auto", "Include ⚠️ ALL masters (otherwise current only)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.applyToAllMasters.setToolTip("Adjusts the sidebearings on all masters. If off, only the current master is processed.")

		self.w.applyToAllGlyphs = vanilla.CheckBox("auto", "Include ⚠️ ALL glyphs (otherwise selected only)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.applyToAllGlyphs.setToolTip("Adjusts all glyphs of the font. If off, only the selected glyphs are processed.")

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Adjust", callback=self.AdjustSpacingMain)
		self.w.runButton.setToolTip("Applies the adjustment to the sidebearings of the chosen glyphs.")
		self.w.setDefaultButton(self.w.runButton)
		self.w.runButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

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
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[choice]-gap-[treatPositiveSBs]-row-[negativeChoice]-row-[updateMetricsKeys]-checkRow-[applyToAllMasters]-checkRow-[applyToAllGlyphs]-inset-[runButton]-inset-|",
				{"view1": self.w.value, "attribute1": "centerY", "view2": self.w.choice, "attribute2": "centerY"},
				{"view1": self.w.treatSBsText1, "attribute1": "centerY", "view2": self.w.treatPositiveSBs, "attribute2": "centerY"},
				{"view1": self.w.treatNegativeSBs, "attribute1": "centerY", "view2": self.w.treatPositiveSBs, "attribute2": "centerY"},
				{"view1": self.w.treatSBsText2, "attribute1": "centerY", "view2": self.w.negativeChoice, "attribute2": "centerY"},
				{"view1": self.w.treatSBsText1, "attribute1": "width", "view2": self.w.treatSBsText2, "attribute2": "width"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

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
		lastItem = "start"
		try:
			self.setStatus("🛠️ Processing …")
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
				self.setStatus("⚠️ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			elif value == 0 and (choice == 2 or (choice == 0 and negativeChoice != 0)):
				# rounding by zero, or the reciprocal of a zero factor, would divide by zero
				self.setStatus("⚠️ Invalid value.")
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
				changedCount = 0
				self.setStatus(f"🛠️ Processing {len(glyphs)} glyphs …")
				for thisGlyph in glyphs:
					lastItem = thisGlyph.name
					self.setStatus(f"🔠 {thisGlyph.name}")
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
							changedCount += 1
							print(f"🔡 {thisGlyph.name} ({thisLayer.name}): \tLSB {int(oldSBs[0])}→{int(newSBs[0])} \tRSB {int(oldSBs[1])}→{int(newSBs[1])}")

				if updateMetricsKeys:
					for thisGlyph in glyphs:
						lastItem = thisGlyph.name
						self.setStatus(f"🔠 {thisGlyph.name}")
						for thisLayer in thisGlyph.layers:
							if not (thisLayer.isMasterLayer or thisLayer.isSpecialLayer):
								continue
							if not (applyToAllMasters or thisLayer.associatedMasterId == currentMasterID):
								continue

							thisLayer.doAlignWidth()
							thisLayer.syncMetrics()

				if changedCount:
					self.setStatus(f"✅ Adjusted {changedCount} layers.")
				else:
					self.setStatus("⚠️ No sidebearings changed.")
				# self.w.close()  # delete if you want window to stay open

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			self.setStatus(f"❌ Error at {lastItem}. Details in Macro Window.")
			print(f"Adjust Spacing Error: {e}")
			import traceback
			print(traceback.format_exc())


AdjustSpacing()
