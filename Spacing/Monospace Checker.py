# MenuTitle: Monospace Checker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Checks if all glyph widths in the frontmost font are actually monospaced. Reports in Macro Window and opens a tab with affected layers.
"""

import vanilla
from GlyphsApp import Glyphs, GSControlLayer, Message
from mekkablue import mekkaObject


class MonospaceChecker(mekkaObject):
	prefDict = {
		"defaultGlyphName": "A",
		"tolerance": 0.0,
		"reportZeroWidths": 0,
		"includeNonExporting": 0,
		"setMonospaceFlag": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 270
		windowHeight = 220
		windowWidthResize = 200  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Monospace Checker",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 12, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, lineHeight * 2), u"New tab with glyphs that do not match the width of the default glyph in each master:", sizeStyle='small', selectable=True)
		linePos += lineHeight * 2

		self.w.defaultGlyphNameText = vanilla.TextBox((inset, linePos, 85, 14), u"Default Glyph:", sizeStyle='small', selectable=True)
		self.w.defaultGlyphName = vanilla.EditText((inset + 85, linePos - 3, -inset, 19), "A", callback=self.SavePreferences, sizeStyle='small')
		self.w.defaultGlyphName.getNSTextField().setToolTip_(u"For each master, will measure the width of this glyph, and compare all other widths to it.")
		linePos += lineHeight

		self.w.toleranceText = vanilla.TextBox((inset, linePos, 105, 14), u"Tolerance in units:", sizeStyle='small', selectable=True)
		self.w.tolerance = vanilla.EditText((inset + 105, linePos - 3, -inset, 19), "0.0", callback=self.SavePreferences, sizeStyle='small')
		self.w.tolerance.getNSTextField().setToolTip_(u"Allow deviations up to this value. 1 unit may be acceptable. If you are not sure, keep it at zero.")
		linePos += lineHeight

		self.w.reportZeroWidths = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Report Zero Widths in Macro Window", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportZeroWidths.getNSButton().setToolTip_(u"In the Macro Window (and only there), will also report glyphs that have zero width. Usually you can ignore those.")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Include Non-Exporting Glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_(u"If disabled, will ignore non-exporting glyphs. If you are unsure, leave it off.")
		linePos += lineHeight

		self.w.setMonospaceFlag = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Set ‘isFixedPitch’ flag in Font Info", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.setMonospaceFlag.getNSButton().setToolTip_(u"Will set the isFixedPitch parameter in Font Info > Font. The parameter sets the isFixedPitch flag in the post table. Indicates whether the font is monospaced. Software can use this information to make sure that all glyphs are rendered with the same amount of pixels horizontally at any given PPM size.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Check", sizeStyle='regular', callback=self.MonospaceCheckerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def MonospaceCheckerMain(self, sender):
		try:
			# brings macro window to front and clears its log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			else:
				print("Monospace Checker Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

			defaultGlyphName = self.pref("defaultGlyphName").strip()
			defaultGlyph = thisFont.glyphs[defaultGlyphName]
			tolerance = self.prefFloat("tolerance")
			includeNonExporting = self.pref("includeNonExporting")
			reportZeroWidths = self.pref("reportZeroWidths")

			if not defaultGlyph:
				Message(
					title="Glyph Not Found",
					message="Could not find a glyph named '%s' in the frontmost font (%s). Aborting." % (defaultGlyphName, thisFont.familyName),
					OKButton="Oops",
				)
			else:
				affectedLayers = []
				deviatingWidthCount = 0
				for thisMaster in thisFont.masters:
					masterID = thisMaster.id
					defaultWidth = defaultGlyph.layers[masterID].width
					print("\nⓂ️ Master %s, default width: %.1f" % (thisMaster.name, defaultWidth))
					for thisGlyph in thisFont.glyphs:
						if thisGlyph.export or includeNonExporting:
							for thisLayer in thisGlyph.layers:
								if thisLayer.associatedMasterId == masterID and (thisLayer.isMasterLayer or thisLayer.isSpecialLayer):
									thisWidth = thisLayer.width
									if thisWidth == 0.0:
										if reportZeroWidths:
											print("ℹ️ %s, layer '%s': zero width" % (thisGlyph.name, thisLayer.name))
									elif not (defaultWidth - tolerance) <= thisWidth <= (defaultWidth + tolerance):
										affectedLayers.append(thisLayer)
										deviatingWidthCount += 1
										print("⛔️ %s, layer '%s': %.1f" % (thisGlyph.name, thisLayer.name, thisWidth))

					# add a newline:
					if affectedLayers:
						newLine = GSControlLayer.newline()
						affectedLayers.append(newLine)

			if affectedLayers:
				# Floating notification:
				Glyphs.showNotification(
					u"Inconsistent widths in %s" % (thisFont.familyName),
					u"Found %i width deviation%s. Details in Macro Window." % (
						deviatingWidthCount,
						"" if deviatingWidthCount == 1 else "s",
					),
				)
				# opens new Edit tab:
				newTab = thisFont.newTab()
				newTab.layers = affectedLayers
			else:
				# Floating notification:
				Glyphs.showNotification(
					u"🥇 %s has consistent widths" % (thisFont.familyName),
					u"All glyph widths are monospaced. Congrats!",
				)

			if self.pref("setMonospaceFlag"):
				print("\nℹ️ Font Info > Font > Custom Parameters:")
				if thisFont.customParameters["isFixedPitch"]:
					print("👍🏻 isFixedPitch parameter already set. OK.")
				else:
					if thisFont.customParameters["isFixedPitch"] is None:
						print("⚠️✅ isFixedPitch parameter was missing, now set. OK.")
					else:
						print("😱✅ isFixedPitch parameter was turned off, now set. OK.")
					thisFont.customParameters["isFixedPitch"] = True

			# self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Monospace Checker Error: %s" % e)
			import traceback
			print(traceback.format_exc())


MonospaceChecker()
