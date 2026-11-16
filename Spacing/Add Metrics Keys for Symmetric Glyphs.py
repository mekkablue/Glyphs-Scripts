# MenuTitle: Add Metrics Keys for Symmetric Glyphs
__doc__ = """
Will add RSB =| if the RSB is the same as the LSB in all masters.
"""

import vanilla
from mekkablue import mekkaObject, SteppingEditText, decimalFormatter
from GlyphsApp import Glyphs, Message
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut


class AddMetricsKeysforSymmetricGlyphs(mekkaObject):
	prefDict = {
		"tolerance": 2,
		"updateMetrics": 1,
		"allGlyphs": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 310
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add Metrics Keys for Symmetric Shapes",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Insert ‘=|’ in RSB if LSB and RSB are the same", sizeStyle='small')

		formatter = decimalFormatter(0, fractionDigits=2)
		self.w.toleranceText = vanilla.TextBox("auto", "Tolerance", sizeStyle='small')
		self.w.tolerance = SteppingEditText("auto", "2", callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		self.w.toleranceUnitsText = vanilla.TextBox("auto", "units", sizeStyle='small')

		self.w.updateMetrics = vanilla.CheckBox("auto", "Update metrics of affected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')

		self.w.allGlyphs = vanilla.CheckBox("auto", "⚠️ Apply to ALL glyphs in font (ignore selection)", value=False, callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Insert", callback=self.AddMetricsKeysforSymmetricGlyphsMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[toleranceText]-gap-[tolerance(50)]-gap-[toleranceUnitsText]-(>=inset)-|",
				"H:|-inset-[updateMetrics]-(>=inset)-|",
				"H:|-inset-[allGlyphs]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[tolerance]-row-[updateMetrics]-checkRow-[allGlyphs]-inset-[runButton]-inset-|",
				{"view1": self.w.toleranceText, "attribute1": "centerY", "view2": self.w.tolerance, "attribute2": "centerY"},
				{"view1": self.w.toleranceUnitsText, "attribute1": "centerY", "view2": self.w.tolerance, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def glyphIsEmpty(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
				if Glyphs.versionNumber >= 3:
					# GLYPHS 3
					if thisLayer.shapes:
						return False
				else:
					# GLYPHS 2
					if thisLayer.paths:
						return False
					if thisLayer.components:
						return False
		return True

	def layerIsSymmetric(self, thisLayer, tolerance=1.0):
		minSB = thisLayer.LSB - abs(tolerance)
		maxSB = minSB + 2 * abs(tolerance)
		if minSB <= thisLayer.RSB <= maxSB:
			return True
		return False

	def AddMetricsKeysforSymmetricGlyphsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			count = 0
			tabText = ""

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Add Metrics Keys for Symmetric Shapes Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				tolerance = self.prefFloat("tolerance")
				updateMetrics = self.pref("updateMetrics")
				allGlyphs = self.pref("allGlyphs")

				if allGlyphs:
					glyphs = thisFont.glyphs
				else:
					glyphs = [layer.parent for layer in thisFont.selectedLayers]

				for thisGlyph in glyphs:
					if thisGlyph.leftMetricsKey == "=|":
						print("🔠 %s: skipped because LSB is ‘=|’" % thisGlyph.name)
					elif thisGlyph.rightMetricsKey == "=|":
						print("🔠 %s: skipped because RSB already is ‘=|’" % thisGlyph.name)
					elif self.glyphIsEmpty(thisGlyph):
						print("🔠 %s: skipped because glyph is empty" % thisGlyph.name)
					else:
						symmetricity = [self.layerIsSymmetric(layer, tolerance) for layer in thisGlyph.layers if layer.isMasterLayer or layer.isSpecialLayer]
						if all(symmetricity):
							count += 1
							tabText += "/%s" % thisGlyph.name
							thisGlyph.rightMetricsKey = "=|"
							reportAddition = ""
							if updateMetrics:
								reportAddition = " and updated metrics"
								for thisLayer in thisGlyph.layers:
									if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
										thisLayer.updateMetrics()
										thisLayer.syncMetrics()
							print("✅ RSB=|%s: %s" % (reportAddition, thisGlyph.name))

				self.w.close()  # delete if you want window to stay open

				# Final report:
				if tabText:
					thisFont.newTab(tabText)
				Glyphs.showNotification(
					"%s: Done" % (thisFont.familyName),
					"Added RSB=| in %i glyph%s. Details in Macro Window" % (
						count,
						"" if count == 1 else "s",
					),
				)
				print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Add Metrics Keys for Symmetric Shapes Error: %s" % e)
			import traceback
			print(traceback.format_exc())


AddMetricsKeysforSymmetricGlyphs()
