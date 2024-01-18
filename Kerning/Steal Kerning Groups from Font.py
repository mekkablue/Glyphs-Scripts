# MenuTitle: Steal Kerning Groups
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Copies kerning groups from one font to another.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject


def menuForFonts(fonts):
	menu = []
	for i, font in enumerate(fonts):
		menu.append(f"{i + 1}. {font.familyName} ({font.filepath.lastPathComponent()})")
	return menu


class StealKerningGroupsfromFont(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"sourceFont": 0,
		"targetFont": 0,
		"allGroups": 1,
		"overwriteExisting": 1,
		"resetGroupsInTarget": 0,
	}

	currentFonts = Glyphs.fonts

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 210
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Steal Kerning Groups",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Copy kerning groups from Source Font to Target Font:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		indent = 75
		self.w.targetFontText = vanilla.TextBox((inset, linePos + 2, indent, 14), "Target font:", sizeStyle="small", selectable=True)
		self.w.targetFont = vanilla.PopUpButton((inset + indent, linePos, -inset, 17), (), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font that receives the kerning groups."
		self.w.targetFont.getNSPopUpButton().setToolTip_(tooltip)
		self.w.targetFontText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.sourceFontText = vanilla.TextBox((inset, linePos + 2, indent, 14), "Source font:", sizeStyle="small", selectable=True)
		self.w.sourceFont = vanilla.PopUpButton((inset + indent, linePos, -inset, 17), (), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font from which the kerning groups are taken."
		self.w.sourceFont.getNSPopUpButton().setToolTip_(tooltip)
		self.w.sourceFontText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.allGroups = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Copy ⚠️ ALL groups (i.e., ignore selection in source font)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allGroups.getNSButton().setToolTip_("If unchecked, will only transfer groups of glyphs selected in source font.")
		linePos += lineHeight

		self.w.overwriteExisting = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Overwrite existing groups in target font", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwriteExisting.getNSButton().setToolTip_("If unchecked, will keep existing groups in the target font, and only set groups when the glyph does not have any yet.")
		linePos += lineHeight

		self.w.resetGroupsInTarget = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "⚠️ Reset groups in target font before copying", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.resetGroupsInTarget.getNSButton().setToolTip_("Will delete ALL kerning groups in target font prior to transfering the source font’s groups.")
		linePos += lineHeight

		self.w.status = vanilla.TextBox((inset, -18 - inset, -150 - inset, 14), "", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.updateButton = vanilla.Button((-150 - inset, -20 - inset, -80 - inset, -inset), "Update", sizeStyle="regular", callback=self.updateUI)
		self.w.updateButton.getNSButton().setToolTip_("Will update all the menus and buttons of this window. Click here if you opened or closed a font since you invoked the script, or after you changed the source font.")

		# Run Button:
		self.w.runButton = vanilla.Button((-70 - inset, -20 - inset, -inset, -inset), "Steal", sizeStyle="regular", callback=self.StealKerningGroupsfromFontMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.currentFonts = Glyphs.fonts
		menu = menuForFonts(self.currentFonts)
		if menu:
			self.w.sourceFont.setItems(menu)
			self.w.sourceFont.set(self.pref("sourceFont"))
			self.w.targetFont.setItems(menu)
			self.w.targetFont.set(self.pref("targetFont"))
		sourceFont = self.currentFonts[self.w.sourceFont.get()]
		self.w.runButton.enable(self.pref("sourceFont") != self.pref("targetFont"))

	def StealKerningGroupsfromFontMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if len(self.currentFonts) < 2:
				Message(title="Not Enough Fonts", message="The script requires at least two fonts.", OKButton=None)
				return

			print("Steal Kerning Groups Report:")
			sourceFont = self.currentFonts[self.pref("sourceFont")]
			targetFont = self.currentFonts[self.pref("targetFont")]
			for font, sourceOrTarget in zip((sourceFont, targetFont), ("Source", "Target")):
				filePath = font.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{font.familyName}\n⚠️ The font file has not been saved yet."
				print(f"{sourceOrTarget}: {reportName}")
			print()

			if self.pref("resetGroupsInTarget"):
				print("Deleting kerning groups in target font:")
				for glyph in targetFont.glyphs:
					msg = f"🧟 {glyph.name}"
					self.w.status.set(msg)
					if glyph.leftKerningGroup:
						msg += f" ◀️ {glyph.leftKerningGroup}"
						glyph.leftKerningGroup = None
					if glyph.rightKerningGroup:
						msg += f" ▶️ {glyph.rightKerningGroup}"
						glyph.rightKerningGroup = None
					print(msg)
				print()

			if self.pref("allGroups"):
				glyphNames = [g.name for g in sourceFont.glyphs]
			else:
				glyphNames = [layer.parent.name for layer in sourceFont.selectedLayers]

			overwriteExisting = self.prefBool("overwriteExisting")
			for glyphName in glyphNames:
				sourceGlyph = sourceFont.glyphs[glyphName]
				targetGlyph = targetFont.glyphs[glyphName]
				if not targetGlyph:
					print(f"🚫 Skipping {glyphName}, not in target font.")
					continue
				msg = f"🔤 {glyphName}"
				self.w.status.set(msg)
				if sourceGlyph.leftKerningGroup and overwriteExisting or not targetGlyph.leftKerningGroup:
					targetGlyph.leftKerningGroup = sourceGlyph.leftKerningGroup
					msg += f" ◀️ {targetGlyph.leftKerningGroup}"
				if sourceGlyph.rightKerningGroup and overwriteExisting or not targetGlyph.rightKerningGroup:
					targetGlyph.rightKerningGroup = sourceGlyph.rightKerningGroup
					msg += f" ▶️ {targetGlyph.rightKerningGroup}"
				print(msg)

			# self.w.close()  # delete if you want window to stay open
			self.w.status.set("✅ Done. Details in Macro Window.")
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Steal Kerning Groups from Font Error: {e}")
			import traceback
			print(traceback.format_exc())


StealKerningGroupsfromFont()
