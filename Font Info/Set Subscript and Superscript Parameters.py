# MenuTitle: Set Subscript and Superscript Parameters
__doc__ = """
Measures your superior and inferior figures and derives subscript/superscript X/Y offset/size parameters.
"""

import math

import vanilla
from mekkablue import mekkaObject, UpdateButton, SteppingEditText, integerFormatter, makeWindowResizable
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


class CalculateSubscriptAndSuperscriptParameters(mekkaObject):
	prefDict = {
		"subscriptCheck": 1,
		"subscriptSample": "oneinferior",
		"subscriptReference": "one",
		"superscriptCheck": 1,
		"superscriptSample": "onesuperior",
		"superscriptReference": "one",
		"roundValues": 0,
		"roundBy": 10,
		"xSizeEqualsYSize": 0,
		"syncWithFirstMaster": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 440
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set Subscript and Superscript Parameters",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Calculate custom parameters in Font Info > Masters", sizeStyle="small", selectable=True)

		for prefix, title in (("sub", "Subscript"), ("super", "Superscript")):
			sampleName = "oneinferior" if prefix == "sub" else "onesuperior"
			tooltip = (
				f"If enabled, will calculate: {prefix}scriptXOffsetName, {prefix}scriptYOffsetName, {prefix}scriptXSizeName, {prefix}scriptYSizeName. "
				f"The {prefix}script glyph (on the left) will be measured in relation to the reference glyph on the right; "
				"offset and size scale will be computed from their differences."
			)
			check = vanilla.CheckBox("auto", title, value=True, callback=self.SavePreferences, sizeStyle="small")
			sample = vanilla.EditText("auto", sampleName, callback=self.SavePreferences, sizeStyle="small")
			referenceText = vanilla.TextBox("auto", "in relation to", sizeStyle="small", selectable=True)
			reference = vanilla.EditText("auto", "one", callback=self.SavePreferences, sizeStyle="small")
			reset = UpdateButton("auto", callback=self.resetValues)
			for element in (check, sample, referenceText, reference):
				element.setToolTip(tooltip)
			reset.setToolTip(f"Resets the {prefix}script reference glyphs to {sampleName} vs. one.")
			setattr(self.w, f"{prefix}scriptCheck", check)
			setattr(self.w, f"{prefix}scriptSample", sample)
			setattr(self.w, f"{prefix}scriptReferenceText", referenceText)
			setattr(self.w, f"{prefix}scriptReference", reference)
			setattr(self.w, f"{prefix}scriptReset", reset)

		tooltip = "If enabled, will round all calculated values by the given amount. Recommended: 5 or 10."
		self.w.roundValues = vanilla.CheckBox("auto", "Round all values by", value=False, callback=self.SavePreferences, sizeStyle="small")
		roundByFormatter = integerFormatter(1)
		self.w.roundBy = SteppingEditText("auto", "10", callback=self.SavePreferences, sizeStyle="small", formatter=roundByFormatter)
		self.w.xSizeEqualsYSize = vanilla.CheckBox("auto", "xSize=ySize", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.roundValues.setToolTip(tooltip)
		self.w.roundBy.setToolTip(tooltip)
		self.w.xSizeEqualsYSize.setToolTip("If enabled, will set the horizontal scale to the same value as the vertical scale, ensuring a proportional scale. Especially useful for italics.")

		self.w.syncWithFirstMaster = vanilla.CheckBox("auto", "Sync all values with first master", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.syncWithFirstMaster.setToolTip("If enabled, will insert the same values in all masters.")

		# Status line and Run Button:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.runButton = vanilla.Button("auto", "Insert", callback=self.CalculateSubscriptAndSuperscriptParametersMain)
		self.w.runButton.setToolTip("Measures the reference glyphs and inserts the calculated subscript and superscript parameters in the masters.")
		self.w.setDefaultButton(self.w.runButton)

		# the status line takes the leftover width, the button stays as wide as its title needs:
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# the fixed-size round field, its checkbox and the reset buttons hug their content; the glyph name fields stretch
		self.w.roundValues.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.roundValues.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		for field in (self.w.subscriptSample, self.w.subscriptReference, self.w.superscriptSample, self.w.superscriptReference):
			field.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# the 'in relation to' labels hug their text and resist compression
		for referenceText in (self.w.subscriptReferenceText, self.w.superscriptReferenceText):
			nsLabel = referenceText.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		for check in (self.w.subscriptCheck, self.w.superscriptCheck):
			nsCheck = check.getNSButton()
			nsCheck.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsCheck.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		def equalWidth(view1, view2):
			return {"view1": view1, "attribute1": "width", "view2": view2, "attribute2": "width"}

		def centerY(view1, view2):
			return {"view1": view1, "attribute1": "centerY", "view2": view2, "attribute2": "centerY"}

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[subscriptCheck]-gap-[subscriptSample(>=70)]-gap-[subscriptReferenceText]-gap-[subscriptReference(>=70)]-gap-[subscriptReset(20)]-inset-|",
				"H:|-inset-[superscriptCheck]-gap-[superscriptSample(>=70)]-gap-[superscriptReferenceText]-gap-[superscriptReference(>=70)]-gap-[superscriptReset(20)]-inset-|",
				"H:|-inset-[roundValues]-gap-[roundBy(50)]-gap-[xSizeEqualsYSize]-(>=inset)-|",
				"H:|-inset-[syncWithFirstMaster]-(>=inset)-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-row-[subscriptSample]-row-[superscriptSample]-row-[roundBy]-checkRow-[syncWithFirstMaster]-inset-[runButton]-inset-|",
				centerY(self.w.status, self.w.runButton),
				equalWidth(self.w.superscriptCheck, self.w.subscriptCheck),
				equalWidth(self.w.superscriptReferenceText, self.w.subscriptReferenceText),
				equalWidth(self.w.subscriptReference, self.w.subscriptSample),
				equalWidth(self.w.superscriptSample, self.w.subscriptSample),
				equalWidth(self.w.superscriptReference, self.w.subscriptSample),
				centerY(self.w.subscriptCheck, self.w.subscriptSample),
				centerY(self.w.subscriptReferenceText, self.w.subscriptSample),
				centerY(self.w.subscriptReference, self.w.subscriptSample),
				centerY(self.w.subscriptReset, self.w.subscriptSample),
				centerY(self.w.superscriptCheck, self.w.superscriptSample),
				centerY(self.w.superscriptReferenceText, self.w.superscriptSample),
				centerY(self.w.superscriptReference, self.w.superscriptSample),
				centerY(self.w.superscriptReset, self.w.superscriptSample),
				centerY(self.w.roundValues, self.w.roundBy),
				centerY(self.w.xSizeEqualsYSize, self.w.roundBy),
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		makeWindowResizable(self.w)  # resizable horizontally only, the height stays what the content needs

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()

	def resetValues(self, sender=None):
		if sender == self.w.subscriptReset:
			self.setPref("subscriptSample", "oneinferior")
			self.setPref("subscriptReference", "one")
		if sender == self.w.superscriptReset:
			self.setPref("superscriptSample", "onesuperior")
			self.setPref("superscriptReference", "one")
		self.LoadPreferences()

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.w.superscriptCheck.get() or self.w.subscriptCheck.get())
		self.w.roundBy.enable(self.w.roundValues.get())

	def roundByFactor(self, number, roundFactor):
		if roundFactor > 1:
			remainder = (number % roundFactor)
			floor = number // roundFactor
			roundUpOrDown = int(round(1.0 * remainder / roundFactor))  # 0 or 1
			number = (floor + roundUpOrDown) * roundFactor
		return int(number)

	def italicOffset(self, y, italicAngle=0.0, pivotalY=0.0):
		yOffset = y - pivotalY  # calculate vertical offset
		italicAngle = math.radians(italicAngle)  # convert to radians
		tangens = math.tan(italicAngle)  # math.tan needs radians
		horizontalDeviance = tangens * yOffset  # vertical distance from pivotal point
		return int(horizontalDeviance)

	def CalculateSubscriptAndSuperscriptParametersMain(self, sender=None):
		currentItemName = None
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			masterCount = 0
			if thisFont is None:
				self.setStatus("⚠️ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				self.setStatus("🛠️ Processing…")
				print("Calculate Subscript and Superscript Parameters Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				syncWithFirstMaster = self.pref("syncWithFirstMaster")
				xSizeEqualsYSize = self.pref("xSizeEqualsYSize")
				if self.pref("roundValues"):
					roundFactor = max(1, self.prefInt("roundBy"))
					print("\nRounding all values by %i" % roundFactor)
				else:
					roundFactor = 1

				for prefix in ("sub", "super"):
					check = self.pref("%sscriptCheck" % prefix)
					sample = self.pref("%sscriptSample" % prefix)
					reference = self.pref("%sscriptReference" % prefix)

					xOffsetName = "%sscriptXOffset" % prefix
					yOffsetName = "%sscriptYOffset" % prefix
					xSizeName = "%sscriptXSize" % prefix
					ySizeName = "%sscriptYSize" % prefix

					upm = thisFont.upm
					sampleGlyph = thisFont.glyphs[sample]
					referenceGlyph = thisFont.glyphs[reference]

					if not sampleGlyph:
						print("❌ Sample glyph ‘%s’ not in font. Aborting %sscript calculation." % (sample, prefix))
					elif not referenceGlyph:
						print("❌ Reference glyph ‘%s’ not in font. Aborting %sscript calculation." % (reference, prefix))
					else:
						for i, thisMaster in enumerate(thisFont.masters):
							currentItemName = f"{thisMaster.name} ({prefix}script)"
							self.setStatus(f"🔠 {currentItemName}")
							masterCount += 1
							if i == 0 or not syncWithFirstMaster:
								sampleLayer = sampleGlyph.layers[thisMaster.id]
								sampleBottom = sampleLayer.bounds.origin.y
								sampleLeft = sampleLayer.bounds.origin.x
								sampleWidth = sampleLayer.bounds.size.width
								sampleHeight = sampleLayer.bounds.size.height

								referenceLayer = referenceGlyph.layers[thisMaster.id]
								referenceBottom = referenceLayer.bounds.origin.y
								referenceLeft = referenceLayer.bounds.origin.x
								referenceWidth = referenceLayer.bounds.size.width
								referenceHeight = referenceLayer.bounds.size.height

								italicAngle = thisMaster.italicAngle
								ySize = upm * sampleHeight / referenceHeight
								xSize = ySize if xSizeEqualsYSize else upm * sampleWidth / referenceWidth
								yOffset = sampleBottom - referenceBottom
								xOffset = self.italicOffset(yOffset, italicAngle=italicAngle) if italicAngle != 0.0 else 0

							thisMaster.customParameters[xOffsetName] = self.roundByFactor(int(xOffset), roundFactor)
							thisMaster.customParameters[yOffsetName] = self.roundByFactor(int(yOffset), roundFactor)
							thisMaster.customParameters[xSizeName] = self.roundByFactor(int(xSize), roundFactor)
							thisMaster.customParameters[ySizeName] = self.roundByFactor(int(ySize), roundFactor)

							print("\n✅ Master %s:" % thisMaster.name)
							print("  🔢 %s: %i" % (xOffsetName, xOffset))
							print("  🔢 %s: %i" % (yOffsetName, yOffset))
							print("  🔢 %s: %i" % (xSizeName, xSize))
							print("  🔢 %s: %i" % (ySizeName, ySize))

				print("\nDone.")

			# Final report:
			if thisFont is not None:
				if masterCount:
					self.setStatus(f"✅ Set parameters in {masterCount} master/script combination{'' if masterCount == 1 else 's'}.")
				else:
					self.setStatus("⚠️ Nothing calculated. Details in Macro Window.")
				Glyphs.showNotification(
					"%s: Done" % (thisFont.familyName),
					"Calculate Subscript and Superscript Parameters is finished. Details in Macro Window",
				)
			print("\nDone.")

		except Exception as e:
			self.setStatus(f"❌ Error at {currentItemName}. Details in Macro Window." if currentItemName else "❌ Error. Details in Macro Window.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Calculate Subscript and Superscript Parameters Error: %s" % e)
			import traceback
			print(traceback.format_exc())


CalculateSubscriptAndSuperscriptParameters()
