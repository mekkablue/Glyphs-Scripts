# MenuTitle: Add Metrics Keys for Symmetric Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Will add RSB =| if the RSB is the same as the LSB in all masters.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject


class AddMetricsKeysforSymmetricGlyphs(mekkaObject):
	prefDict = {
		"tolerance": 2,
		"updateMetrics": 1,
		"allGlyphs": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 160
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add Metrics Keys for Symmetric Shapes",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Insert ‘=|’ in RSB if LSB and RSB are the same", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.toleranceText = vanilla.TextBox((inset, linePos + 3, 65, 14), "Tolerance:", sizeStyle='small', selectable=True)
		self.w.tolerance = vanilla.EditText((inset + 65, linePos, -inset - 50, 19), "2", callback=self.SavePreferences, sizeStyle='small')
		self.w.toleranceUnitsText = vanilla.TextBox((-inset - 45, linePos + 3, -inset, 14), "units", sizeStyle='small', selectable=True)
		linePos += lineHeight + 3

		self.w.updateMetrics = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Update metrics of affected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.allGlyphs = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "⚠️ Apply to ALL glyphs in font (ignore selection)", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Insert", sizeStyle='regular', callback=self.AddMetricsKeysforSymmetricGlyphsMain)
		self.w.setDefaultButton(self.w.runButton)

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
					"" if count == 0 else "s",
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
