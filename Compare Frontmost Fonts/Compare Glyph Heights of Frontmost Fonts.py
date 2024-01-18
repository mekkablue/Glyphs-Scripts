# MenuTitle: Compare Glyph Heights
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Lists all glyphs that differ from the second font in height beyond a given threshold.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject


class CompareGlyphHeightsOfFrontmostFonts(mekkaObject):
	prefDict = {
		"heights": 0,
		"depths": 0,
		"tolerate": 0,
		"includeNonExporting": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 200
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Compare Glyph Heights of Frontmost Fonts",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 28), "Lists all glyphs that differ in height more than the given threshold. Detailed report in Macro Window.", sizeStyle='small', selectable=True)
		linePos += lineHeight * 2

		self.w.tolerateText = vanilla.TextBox((inset, linePos + 2, 140, 14), "Tolerate difference up to:", sizeStyle='small', selectable=True)
		self.w.tolerate = vanilla.EditText((inset + 140, linePos, -inset, 19), "5", callback=self.SavePreferences, sizeStyle='small')
		self.w.tolerate.getNSTextField().setToolTip_("How much of a difference is OK. Hint: overshoot size is a good idea for this one.")
		linePos += lineHeight

		self.w.heights = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Compare top bounds (‘heights’)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.heights.getNSButton().setToolTip_("Measures and compares the heights of the top edges (bbox maximum).")
		linePos += lineHeight

		self.w.depths = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Compare bottom bounds (‘depths’)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.depths.getNSButton().setToolTip_("Measures and compares the heights of the bottom edges (bbox minimum).")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_("If enabled, also measures glyphs that are set to not export.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Compare", sizeStyle='regular', callback=self.CompareGlyphHeightsOfFrontmostFontsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Compare Glyph Heights of Frontmost Fonts' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self):
		if not self.w.heights.get() and not self.w.depths.get():
			self.w.runButton.enable(False)
		else:
			self.w.runButton.enable(True)

	def CompareGlyphHeightsOfFrontmostFontsMain(self, sender):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print("Note: 'Compare Glyph Heights of Frontmost Fonts' could not write preferences.")

			if len(Glyphs.fonts) < 2:
				Message(title="Compare Error", message="You need to have at least two fonts open for comparing.", OKButton="Ooops")
			else:
				# brings macro window to front and clears its log:
				Glyphs.clearLog()
				# Glyphs.showMacroWindow()

				thisFont = Glyphs.font  # frontmost font
				otherFont = Glyphs.fonts[1]  # second font
				thisFileName = thisFont.filepath.lastPathComponent()
				otherFileName = otherFont.filepath.lastPathComponent()
				print(
					"Compare Glyph Heights of Frontmost Fonts Report for:\n  (1) %s: %s\n      %s\n  (2) %s: %s\n      %s" % (
						thisFont.familyName,
						thisFileName,
						thisFont.filepath,
						otherFont.familyName,
						otherFileName,
						otherFont.filepath,
					)
				)
				print()

				heights = self.pref("heights")
				depths = self.pref("depths")
				tolerate = self.prefFloat("tolerate")
				includeNonExporting = self.pref("includeNonExporting")

				theseIDs = [m.id for m in thisFont.masters]
				otherIDs = [m.id for m in otherFont.masters]
				masterIDs = tuple(zip(theseIDs, otherIDs))
				collectedGlyphNames = []

				if len(theseIDs) != len(otherIDs):
					print("⚠️ Different number of masters in %s and %s" % (thisFont.filepath.lastPathComponent(), otherFont.filepath.lastPathComponent()))

				for thisGlyph in thisFont.glyphs:
					if thisGlyph.export or includeNonExporting:
						print("🔠 Comparing %s" % thisGlyph.name)
						glyphName = thisGlyph.name
						otherGlyph = otherFont.glyphs[glyphName]
						if not otherGlyph:
							print("🚫 %s not in %s" % (glyphName, otherFileName))
							continue
						if not otherGlyph.export:
							print("⚠️ %s not exporting in %s" % (glyphName, otherFileName))
						for idPair in masterIDs:
							thisID, otherID = idPair
							thisLayer = thisGlyph.layers[thisID]
							otherLayer = otherGlyph.layers[otherID]
							if not (thisLayer and otherLayer):
								print("⚠️ Cannot compare layers in %s" % glyphName)
							else:
								if heights:
									thisHeight = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
									otherHeight = otherLayer.bounds.origin.y + otherLayer.bounds.size.height
									if abs(thisHeight - otherHeight) > tolerate:
										print("  ❌ %s heights: (1) %.1f, (2) %.1f" % (glyphName, thisHeight, otherHeight))
										collectedGlyphNames.append(glyphName)
								if depths:
									thisDepth = thisLayer.bounds.origin.y
									otherDepth = otherLayer.bounds.origin.y
									if abs(thisDepth - otherDepth) > tolerate:
										print("  ❌ %s depths: (1) %.1f, (2) %.1f" % (glyphName, thisDepth, otherDepth))
										collectedGlyphNames.append(glyphName)

				if not collectedGlyphNames:
					Message(
						title="No significant differences",
						message="No differences larger than %.1f found between the two frontmost fonts. See the macro window for error messages." % tolerate,
						OKButton="😎 Cool"
					)
				else:
					collectedGlyphNames = tuple(set(collectedGlyphNames))
					tabText = "/" + "/".join(collectedGlyphNames)
					thisFont.newTab(tabText)
					otherFont.newTab(tabText)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Compare Glyph Heights of Frontmost Fonts Error: %s" % e)
			import traceback
			print(traceback.format_exc())


CompareGlyphHeightsOfFrontmostFonts()
