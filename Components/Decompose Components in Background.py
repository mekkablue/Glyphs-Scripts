# MenuTitle: Decompose Components in Background
__doc__ = """
Will backup foregrounds into backgrounds, and decompose backgrounds. Useful for keeping original designs of composites for reference.
"""

import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, GSBackgroundLayer, Message
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut


class Decompose_Components_in_Background(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"copyToBackgroundFirst": 0,
		"verbose": 0,
		"whichMasters": 0,
		"whichGlyphsInWhichFonts": 0,
	}

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
		windowWidth = 370
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Decompose Backgrounds",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15

		# ## Description text
		self.w.descriptionText = vanilla.TextBox("auto", "Decompose components in glyph backgrounds:", sizeStyle="small", selectable=True)

		# ## Option to backup glyphs in the background before decomposition
		self.w.copyToBackgroundFirst = vanilla.CheckBox("auto", "Create backups in background first", sizeStyle="small", callback=self.SavePreferences)
		self.w.copyToBackgroundFirst.setToolTip("If selected, will copy current foregrounds into backgrounds, overwriting existing background content.")

		self.w.verbose = vanilla.CheckBox("auto", "Verbose output", sizeStyle="small", callback=self.SavePreferences)
		self.w.verbose.setToolTip("Will output report for every glyph (slow). Do this only for testing purposes.")

		# ## Divider
		self.w.div_copyToBackgroundFirst = vanilla.HorizontalLine("auto")

		# ## Which glyphs in which fonts
		self.w.whichGlyphsInWhichFonts = vanilla.VerticalRadioGroup("auto", self.glyphsOptions, sizeStyle="small", callback=self.glyphsOptionsCallback)
		self.w.whichGlyphsInWhichFonts.setToolTip("Which glyphs are affected in which fonts.\n\n⚠️ Careful with the bigger scopes: they affect many glyph backgrounds in one click. Consider saving your .glyphs file first (so you can revert in the worst case).")

		# ## Divider
		self.w.div_glyphsOptions = vanilla.HorizontalLine("auto")

		# ## Which masters
		self.w.whichMasters = vanilla.VerticalRadioGroup("auto", self.masterOptions, sizeStyle="small", callback=self.SavePreferences)
		self.w.whichMasters.setToolTip("Choose which font masters shall be affected.")

		# ## Action button
		self.w.decomposeButton = vanilla.Button("auto", "Decompose", callback=self.decomposeButtonCallback)
		self.w.setDefaultButton(self.w.decomposeButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[copyToBackgroundFirst]-gap-[verbose]-(>=inset)-|",
				"H:|-inset-[div_copyToBackgroundFirst]-inset-|",
				"H:|-inset-[whichGlyphsInWhichFonts]-(>=inset)-|",
				"H:|-inset-[div_glyphsOptions]-inset-|",
				"H:|-inset-[whichMasters]-(>=inset)-|",
				"H:|-(>=inset)-[decomposeButton(>=120)]-inset-|",
				"V:|-gap-[descriptionText]-row-[copyToBackgroundFirst]-gap-[div_copyToBackgroundFirst(1)]-gap-[whichGlyphsInWhichFonts]-gap-[div_glyphsOptions(1)]-gap-[whichMasters]-inset-[decomposeButton]-inset-|",
				{"view1": self.w.verbose, "attribute1": "centerY", "view2": self.w.copyToBackgroundFirst, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		# the scope ‘all open fonts’ always works on all masters:
		allFontsSelected = self.w.whichGlyphsInWhichFonts.get() == 2
		self.w.whichMasters.enable(not allFontsSelected)

	def glyphsOptionsCallback(self, sender):
		self.SavePreferences()

	def decomposeButtonCallback(self, sender):
		Glyphs.clearLog()

		# update settings to the latest user input:
		self.SavePreferences()

		if not Glyphs.font:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		# collect user settings:
		copyToBackgroundFirst = self.prefBool("copyToBackgroundFirst")
		whichGlyphsInWhichFonts = self.prefInt("whichGlyphsInWhichFonts")
		workOnAllGlyphs = whichGlyphsInWhichFonts > 0
		workOnAllFonts = whichGlyphsInWhichFonts == 2
		verbose = self.prefBool("verbose")

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
			if workOnAllGlyphs:
				selectedGlyphs = thisFont.glyphs
			else:
				selectedGlyphs = [thisLayer.parent for thisLayer in thisFont.selectedLayers]

			# determine affected masters
			workOnAllMasters = workOnAllFonts or self.prefInt("whichMasters") == 1
			if workOnAllMasters:
				selectedMasterIDs = [master.id for master in thisFont.masters]
			else:
				selectedMasterIDs = (thisFont.selectedFontMaster.id, )

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
			# foreground = thisLayer.foreground()
		else:
			background = thisLayer.background
			# foreground = thisLayer

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
