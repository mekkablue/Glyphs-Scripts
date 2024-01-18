# MenuTitle: Decompose Components in Background
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import vanilla as vl
from GlyphsApp import Glyphs, GSBackgroundLayer
from mekkaCore import mekkaObject

__doc__ = """
Will backup foregrounds into backgrounds, and decompose backgrounds. Useful for keeping original designs of composites for reference.
"""


class Decompose_Components_in_Background(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"copyToBackgroundFirst": 0,
		"whichMasters": 0,
		"whichGlyphsInWhichFonts": 0,
	}

	windowHeight = 216
	padding = (10, 10, 12)
	buttonHeight = 20
	textHeight = 14
	sizeStyle = 'small'

	glyphsOptions = (
		"Backgrounds of selected glyphs in frontmost font",
		"⚠️ All glyph backgrounds in current font",
		"⚠️ All glyph backgrounds in all masters of ⚠️ all open fonts",
	)
	masterOptions = (
		"On currently selected master only",
		"On all masters",
	)

	def __init__(self):
		x, y, p = self.padding

		self.w = vl.FloatingWindow((370, self.windowHeight), "Decompose Backgrounds")

		# ## Description text
		self.w.descriptionText = vl.TextBox((x, y, -p, self.textHeight), "Decompose components in glyph backgrounds:", sizeStyle='small', selectable=True)
		y += self.textHeight + p

		# ## Option to backup glyphs in the background before decomposition
		self.w.copyToBackgroundFirst = vl.CheckBox((x + 3, y, 240, self.textHeight), "Create backups in background first", sizeStyle=self.sizeStyle, callback=self.SavePreferences)
		self.w.copyToBackgroundFirst.getNSButton().setToolTip_("If selected, will copy current foregrounds into backgrounds, overwriting existing background content.")

		self.w.verbose = vl.CheckBox((240 + 3, y, -p, self.textHeight), "Verbose output", sizeStyle=self.sizeStyle, callback=self.SavePreferences)
		self.w.verbose.getNSButton().setToolTip_("Will output report for every glyph (slow). Do this only for testing purposes.")
		y += self.textHeight

		# ## Divider
		self.w.div_copyToBackgroundFirst = vl.HorizontalLine((x, y, -p, self.textHeight))
		y += self.textHeight

		# ## Which glyphs in which fonts
		self.w.whichGlyphsInWhichFonts = vl.RadioGroup(
			(x, y, -p, self.buttonHeight * len(self.glyphsOptions)), self.glyphsOptions, sizeStyle=self.sizeStyle, callback=self.glyphsOptionsCallback
		)

		self.w.whichGlyphsInWhichFonts.getNSMatrix().setToolTip_("Which glyphs are affected in which fonts.\n\n⚠️ Careful with the bigger scopes: they affect many glyph backgrounds in one click. Consider saving your .glyphs file first (so you can revert in the worst case).")
		y += self.buttonHeight * len(self.glyphsOptions)

		# ## Divider
		self.w.div_glyphsOptions = vl.HorizontalLine((x, y, -p, self.textHeight))
		y += self.textHeight

		# ## Which masters
		self.w.whichMasters = vl.RadioGroup(
			(x, y, -p, self.buttonHeight * len(self.masterOptions)),
			self.masterOptions,
			sizeStyle=self.sizeStyle,
			callback=self.SavePreferences,
		)
		self.w.whichMasters.getNSMatrix().setToolTip_("Choose which font masters shall be affected.")

		y += self.buttonHeight * len(self.masterOptions)

		# ## Action button
		self.w.decomposeButton = vl.Button((-p - 120, -self.buttonHeight - p, -p, self.buttonHeight), "Decompose", sizeStyle="regular", callback=self.decomposeButtonCallback)

		self.w.setDefaultButton(self.w.decomposeButton)

		if not self.LoadPreferences():
			print("Note: 'Decompose Backgrounds' could not load preferences. Will resort to defaults")

		self.w.open()
		self.w.makeKey()

	def glyphsOptionsCallback(self, sender):
		allFontsSelected = sender.get() == 2
		self.w.whichMasters.enable(not allFontsSelected)
		self.SavePreferences()

	def decomposeButtonCallback(self, sender):
		Glyphs.clearLog()

		# collect user settings:
		copyToBackgroundFirst = self.prefBool("copyToBackgroundFirst")
		workOnAllFonts = self.pref("whichGlyphsInWhichFonts")
		workOnAllGlyphs = workOnAllFonts or self.pref("whichMasters")
		verbose = self.pref("verbose")

		# determine affected fonts
		if workOnAllFonts:
			selectedFonts = Glyphs.fonts
		else:
			selectedFonts = (Glyphs.font, )

		print("Decompose Components in Background:")
		for thisFont in selectedFonts:
			print(f"\n📄 {thisFont.familyName}:")
			fontCount = 0

			# determine affected glyphs
			if workOnAllGlyphs or workOnAllFonts:
				selectedGlyphs = thisFont.glyphs
			else:
				selectedGlyphs = [thisLayer.parent for thisLayer in thisFont.selectedLayers]

			# determine affected masters
			workOnAllMasters = workOnAllFonts or self.w.whichMasters.get() == 1
			if workOnAllMasters:
				selectedMasterIDs = [master.id for master in thisFont.masters]
			else:
				selectedMasterIDs = thisFont.selectedFontMaster.id

			thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
			try:
				for thisGlyph in selectedGlyphs:
					count = 0
					# print("Processing", thisGlyph.name)
					# thisGlyph.beginUndo()  # undo grouping causes crashes
					for thisLayer in thisGlyph.layers:
						if thisLayer is not None and (thisLayer.isMasterLayer or thisLayer.isSpecialLayer) and thisLayer.associatedMasterId in selectedMasterIDs:
							count += self.process(thisLayer, copyToBackgroundFirst=copyToBackgroundFirst)
					fontCount += count
					if verbose:
						print(f"  Decomposed {count} component{'' if count == 1 else 's'}: {thisGlyph.name}")
					# thisGlyph.endUndo()  # undo grouping causes crashes
				print(f"Decomposed {fontCount} components in {len(selectedGlyphs)} glyphs.")

			except Exception as e:
				Glyphs.showMacroWindow()
				import traceback
				print(f"\n⚠️ Script Error:\n\n{traceback.format_exc()}\n\n{e}")
				# raise e

			finally:
				thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

	def process(self, thisLayer, copyToBackgroundFirst=False):
		# Determine foreground and background:
		if isinstance(thisLayer, GSBackgroundLayer):
			background = thisLayer
			foreground = thisLayer.foreground()
		else:
			background = thisLayer.background
			foreground = thisLayer

		# make backup if user asked for it:
		if copyToBackgroundFirst:
			thisLayer.contentToBackgroundCheckSelection_keepOldBackground_(False, False)

		# decompose background:
		compCount = 0
		if background and background.components:
			compCount = len(background.components)
			background.decomposeComponents()

		return compCount


Decompose_Components_in_Background()
