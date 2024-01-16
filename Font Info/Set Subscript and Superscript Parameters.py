# MenuTitle: Set Subscript and Superscript Parameters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Measures your superior and inferior figures and derives subscript/superscript X/Y offset/size parameters.
"""

import vanilla
import math
from GlyphsApp import Glyphs, Message


class CalculateSubscriptAndSuperscriptParameters(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 170
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set Subscript and Superscript Parameters",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName="com.mekkablue.CalculateSubscriptAndSuperscriptParameters.mainwindow"  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Calculate custom parameters in Font Info > Masters:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.subscriptCheck = vanilla.CheckBox((inset, linePos, 80, 20), "Subscript:", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.subscriptSample = vanilla.EditText((inset + 85, linePos, -inset - 175, 19), "oneinferior", callback=self.SavePreferences, sizeStyle='small')
		self.w.subscriptReferenceText = vanilla.TextBox((-inset - 170, linePos + 3, -inset - 95, 14), "in relation to:", sizeStyle='small', selectable=True)
		self.w.subscriptReference = vanilla.EditText((-inset - 95, linePos, -inset - 25, 19), "one", callback=self.SavePreferences, sizeStyle='small')
		self.w.subscriptReset = vanilla.SquareButton((-inset - 20, linePos + 0.5, -inset, 18), "↺", sizeStyle='small', callback=self.resetValues)
		# tooltips:
		tooltip = "If enabled, will calculate: subscriptXOffsetName, subscriptYOffsetName, subscriptXSizeName, subscriptYSizeName. The subscript glyph (on the left) will be measured in relation to the reference glyph on the right; offset and size scale will be computed from their differences."
		self.w.subscriptSample.getNSTextField().setToolTip_(tooltip)
		self.w.subscriptReference.getNSTextField().setToolTip_(tooltip)
		self.w.subscriptCheck.getNSButton().setToolTip_(tooltip)
		self.w.subscriptReferenceText.getNSTextField().setToolTip_(tooltip)
		self.w.subscriptReset.getNSButton().setToolTip_("Resets the subscript reference glyphs to oneinferior vs. one.")
		linePos += lineHeight

		self.w.superscriptCheck = vanilla.CheckBox((inset, linePos, 80, 20), "Superscript:", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.superscriptSample = vanilla.EditText((inset + 85, linePos, -inset - 175, 19), "onesuperior", callback=self.SavePreferences, sizeStyle='small')
		self.w.superscriptReferenceText = vanilla.TextBox((-inset - 170, linePos + 3, -inset - 95, 14), "in relation to:", sizeStyle='small', selectable=True)
		self.w.superscriptReference = vanilla.EditText((-inset - 95, linePos, -inset - 25, 19), "one", callback=self.SavePreferences, sizeStyle='small')
		self.w.superscriptReset = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.resetValues)
		# tooltips:
		tooltip = "If enabled, will calculate: superscriptXOffsetName, superscriptYOffsetName, superscriptXSizeName, superscriptYSizeName. The superscript glyph (on the left) will be measured in relation to the reference glyph on the right; offset and size scale will be computed from their differences."
		self.w.superscriptSample.getNSTextField().setToolTip_(tooltip)
		self.w.superscriptReference.getNSTextField().setToolTip_(tooltip)
		self.w.superscriptCheck.getNSButton().setToolTip_(tooltip)
		self.w.superscriptReferenceText.getNSTextField().setToolTip_(tooltip)
		self.w.superscriptReset.getNSButton().setToolTip_("Resets the superscript reference glyphs to onesuperior vs. one.")
		linePos += lineHeight

		self.w.roundValues = vanilla.CheckBox((inset, linePos, 130, 20), "Round all values by:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.roundBy = vanilla.EditText((inset + 130, linePos, 50, 19), "10", callback=self.SavePreferences, sizeStyle='small')
		self.w.xSizeEqualsYSize = vanilla.CheckBox((inset + 200, linePos, -inset, 20), "xSize=ySize", value=False, callback=self.SavePreferences, sizeStyle='small')
		# tooltips:
		tooltip = "If enabled, will round all calculated values by the given amount. Recommended: 5 or 10."
		self.w.roundValues.getNSButton().setToolTip_(tooltip)
		self.w.roundBy.getNSTextField().setToolTip_(tooltip)
		self.w.xSizeEqualsYSize.getNSButton().setToolTip_("If enabled, will set the horizontal scale to the same value as the vertical scale, ensuring a proportional scale. Especially useful for italics.")
		linePos += lineHeight

		self.w.syncWithFirstMaster = vanilla.CheckBox((inset, linePos, -inset, 20), "Sync all values with first master", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.syncWithFirstMaster.getNSButton().setToolTip_("If enabled, will insert the same values in all masters.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Insert", sizeStyle='regular', callback=self.CalculateSubscriptAndSuperscriptParametersMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Calculate Subscript and Superscript Parameters' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()

	def resetValues(self, sender=None):
		if sender == self.w.subscriptReset:
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptSample"] = "oneinferior"
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptReference"] = "one"
		if sender == self.w.superscriptReset:
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptSample"] = "onesuperior"
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptReference"] = "one"
		self.LoadPreferences()

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.w.superscriptCheck.get() or self.w.subscriptCheck.get())
		self.w.roundBy.enable(self.w.roundValues.get())

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptCheck"] = self.w.subscriptCheck.get()
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptSample"] = self.w.subscriptSample.get()
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptReference"] = self.w.subscriptReference.get()
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptCheck"] = self.w.superscriptCheck.get()
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptSample"] = self.w.superscriptSample.get()
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptReference"] = self.w.superscriptReference.get()
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.roundValues"] = self.w.roundValues.get()
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.roundBy"] = self.w.roundBy.get()
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.xSizeEqualsYSize"] = self.w.xSizeEqualsYSize.get()
			Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.syncWithFirstMaster"] = self.w.syncWithFirstMaster.get()

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptCheck", 1)
			Glyphs.registerDefault("com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptSample", "oneinferior")
			Glyphs.registerDefault("com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptReference", "one")
			Glyphs.registerDefault("com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptCheck", 1)
			Glyphs.registerDefault("com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptSample", "onesuperior")
			Glyphs.registerDefault("com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptReference", "one")
			Glyphs.registerDefault("com.mekkablue.CalculateSubscriptAndSuperscriptParameters.roundValues", 0)
			Glyphs.registerDefault("com.mekkablue.CalculateSubscriptAndSuperscriptParameters.roundBy", 10)
			Glyphs.registerDefault("com.mekkablue.CalculateSubscriptAndSuperscriptParameters.xSizeEqualsYSize", 0)
			Glyphs.registerDefault("com.mekkablue.CalculateSubscriptAndSuperscriptParameters.syncWithFirstMaster", 0)

			# load previously written prefs:
			self.w.subscriptCheck.set(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptCheck"])
			self.w.subscriptSample.set(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptSample"])
			self.w.subscriptReference.set(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.subscriptReference"])
			self.w.superscriptCheck.set(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptCheck"])
			self.w.superscriptSample.set(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptSample"])
			self.w.superscriptReference.set(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.superscriptReference"])
			self.w.roundValues.set(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.roundValues"])
			self.w.roundBy.set(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.roundBy"])
			self.w.xSizeEqualsYSize.set(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.xSizeEqualsYSize"])
			self.w.syncWithFirstMaster.set(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.syncWithFirstMaster"])

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

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
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Calculate Subscript and Superscript Parameters' could not write preferences.")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Calculate Subscript and Superscript Parameters Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				syncWithFirstMaster = Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.syncWithFirstMaster"]
				xSizeEqualsYSize = Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.xSizeEqualsYSize"]
				if Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.roundValues"]:
					roundFactor = max(1, int(Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.roundBy"]))
					print("\nRounding all values by %i" % roundFactor)
				else:
					roundFactor = 1

				for prefix in ("sub", "super"):
					check = Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.%sscriptCheck" % prefix]
					sample = Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.%sscriptSample" % prefix]
					reference = Glyphs.defaults["com.mekkablue.CalculateSubscriptAndSuperscriptParameters.%sscriptReference" % prefix]

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
			Glyphs.showNotification(
				"%s: Done" % (thisFont.familyName),
				"Calculate Subscript and Superscript Parameters is finished. Details in Macro Window",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Calculate Subscript and Superscript Parameters Error: %s" % e)
			import traceback
			print(traceback.format_exc())


CalculateSubscriptAndSuperscriptParameters()
