# MenuTitle: Realign Stacking Anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
On all layers in combining marks, top/_top, bottom/_bottom, etc. anchor pairs are realigned in their italic angle. Only moves anchors horizontally.
"""

from Foundation import NSPoint
import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject
from mekkablue.geometry import italicize


class RealignStackingAnchors(mekkaObject):
	prefDict = {
		"whichAnchorPairs": "top, bottom",
		"allGlyphs": 1,
		"limitToCombiningMarks": 1,
		"includeNonExporting": 0,
		"allFonts": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 380
		windowHeight = 230
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Realign Stacking Anchors in Combining Accents",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, lineHeight * 2.5), "Realign stacking anchor pairs to each other (anchors with and without leading underscore, e.g. _top to top) in their respective italic angle, for pairs of these anchors:", sizeStyle='small', selectable=True)
		linePos += int(lineHeight * 2.4)

		self.w.whichAnchorPairs = vanilla.EditText((inset, linePos, -inset, 19), "top, bottom", callback=self.SavePreferences, sizeStyle='small')
		self.w.whichAnchorPairs.getNSTextField(
		).setToolTip_("Comma-separated list of anchor names. With or without underscore does not matter. You only need to specify one of both. Example: ‘top, bottom’.")
		linePos += lineHeight

		self.w.allGlyphs = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "Include all glyphs in font (i.e., ignore selection, recommended)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.allGlyphs.getNSButton().setToolTip_("If checked, will ignore the current glyph selection, and process all glyphs in the font, minus the glyphs that are excluded by the following two settings.")
		linePos += lineHeight

		self.w.limitToCombiningMarks = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "Limit to combining marks (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.limitToCombiningMarks.getNSButton().setToolTip_("If checked, among the processed glyphs, will process only glyphs that are categorised as combining marks. Usually this is where you want the realignment if stacking anchors. Uncheck if your accents are not correctly categorised.")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "Include non-exporting glyphs (recommended)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_("If checked, will also process glyphs that are set to not export. Otherwise only exporting glyphs.")
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "⚠️ Apply to ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allFonts.getNSButton().setToolTip_("If checked, will apply to ALL fonts currently open in Glyphs. You have been warned.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Realign", callback=self.RealignStackingAnchorsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def RealignStackingAnchorsMain(self, sender):
		try:
			Glyphs.clearLog()  # clears macro window log
			print("Realign Stacking Anchors:")

			# update settings to the latest user input:
			self.SavePreferences()

			whichAnchorPairs = self.pref("whichAnchorPairs")
			anchorPairs = [a.strip() for a in whichAnchorPairs.split(",")]
			allGlyphs = self.pref("allGlyphs")
			limitToCombiningMarks = self.pref("limitToCombiningMarks")
			includeNonExporting = self.pref("includeNonExporting")
			allFonts = self.pref("allFonts")
			movedAnchorCount = 0
			glyphCount = 0

			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			for thisFont in theseFonts:
				fontNameForReport = thisFont.familyName
				if thisFont.filepath:
					fontNameForReport = thisFont.filepath.lastPathComponent()
				print("\n📄 %s" % fontNameForReport)

				if not allGlyphs:
					if includeNonExporting:
						glyphs = [layer.parent for layer in thisFont.selectedLayers]
					else:
						glyphs = [layer.parent for layer in thisFont.selectedLayers if layer.parent.export]
				else:
					if includeNonExporting:
						glyphs = thisFont.glyphs
					else:
						glyphs = [g for g in thisFont.glyphs if g.export]

				if limitToCombiningMarks:
					glyphs = [g for g in glyphs if g.category == "Mark" and g.subCategory == "Nonspacing"]

				glyphCount += len(glyphs)
				print("🔢 Processing %i glyph%s..." % (
					len(glyphs),
					"" if len(glyphs) == 1 else "s",
				))

				for thisGlyph in glyphs:
					for thisLayer in thisGlyph.layers:
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:

							# Nomenclature:
							#  top: default anchor
							# _top: underscore Anchor
							for defaultAnchorName in anchorPairs:

								# sanitize user entry:
								# get the default anchor name by getting rid of leading underscores
								while defaultAnchorName[0] == "_" and len(defaultAnchorName) > 1:
									defaultAnchorName = defaultAnchorName[1:]

								# derive underscore anchor from default anchor
								underscoreAnchorName = "_%s" % defaultAnchorName
								underscoreAnchor = thisLayer.anchors[underscoreAnchorName]

								# only proceed if there are both anchors:
								if underscoreAnchor:
									defaultAnchor = thisLayer.anchors[defaultAnchorName]
									if defaultAnchor:
										# record original position:
										oldPosition = defaultAnchor.position

										# determine italic angle and move the anchor accordingly:
										if Glyphs.versionNumber >= 3:
											# GLYPHS 3
											italicAngle = thisLayer.italicAngle
										else:
											# GLYPHS 2
											italicAngle = thisLayer.associatedFontMaster().italicAngle
										straightPosition = NSPoint(underscoreAnchor.position.x, defaultAnchor.position.y)
										if italicAngle:
											defaultAnchor.position = italicize(straightPosition, italicAngle, underscoreAnchor.position.y)
										else:
											defaultAnchor.position = straightPosition

										# compare new position to original position, and report if moved:
										if defaultAnchor.position != oldPosition:
											print("↔️ Moved %s in 🔠 %s, layer ‘%s’" % (defaultAnchorName, thisGlyph.name, thisLayer.name))
											movedAnchorCount += 1

			self.w.close()  # delete if you want window to stay open

			# wrap up and report:
			report = "Moved %i anchor%s in %i glyph%s%s." % (
				movedAnchorCount,
				"" if movedAnchorCount == 1 else "s",
				glyphCount,
				"" if glyphCount == 1 else "s",
				" in %i fonts" % len(theseFonts) if len(theseFonts) > 1 else "",
			)
			print("\n%s\nDone." % report)
			Message(
				title="Realigned Anchors",
				message="%s Detailed report in Macro Window." % report,
				OKButton=None,
			)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Realign Stacking Anchors in Combining Accents Error: %s" % e)
			import traceback
			print(traceback.format_exc())


RealignStackingAnchors()
