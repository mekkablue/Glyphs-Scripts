# MenuTitle: Copy Glyphs from Other Font into Backup Layers
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates backup layers for selected glyphs in target font, and fills them with the respective glyphs in source font.
"""

import vanilla
from GlyphsApp import Glyphs


class CopyGlyphsIntoBackupLayers(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 110
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Copy glyphs into backup layers",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName="com.mekkablue.CopyGlyphsIntoBackupLayers.mainwindow"  # stores last window position and size
		)

		# UI elements:
		self.w.from_text = vanilla.TextBox((15, 12 + 2, 130, 14), "Backup layers from:", sizeStyle='small')
		self.w.from_font = vanilla.PopUpButton((150, 12, -15, 17), self.GetFonts(isSourceFont=True), sizeStyle='small', callback=self.buttonCheck)

		self.w.to_text = vanilla.TextBox((15, 12 + 2 + 25, 130, 14), "Into selected glyphs in:", sizeStyle='small')
		self.w.to_font = vanilla.PopUpButton((150, 12 + 25, -15, 17), self.GetFonts(isSourceFont=False), sizeStyle='small', callback=self.buttonCheck)

		self.w.suffix_text = vanilla.TextBox((15, 12 + 50, 130, 14), "Layer name suffix:", sizeStyle='small')
		self.w.suffix = vanilla.EditText((150, 12 + 50, -90, 15 + 3), "Backup", sizeStyle='small')

		# Run Button:
		self.w.copybutton = vanilla.Button((-80, 12 + 50, -15, 17), "Copy", sizeStyle='small', callback=self.CopyGlyphsIntoBackupLayersMain)
		self.w.setDefaultButton(self.w.copybutton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Copy glyphs into backup layers' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults["com.mekkablue.CopyGlyphsIntoBackupLayers.from_font"] = self.w.from_font.get()
			Glyphs.defaults["com.mekkablue.CopyGlyphsIntoBackupLayers.to_font"] = self.w.to_font.get()
			Glyphs.defaults["com.mekkablue.CopyGlyphsIntoBackupLayers.suffix"] = self.w.suffix.get()
		except:
			return False

		return True

	def LoadPreferences(self):
		try:
			self.w.from_font.set(Glyphs.defaults["com.mekkablue.CopyGlyphsIntoBackupLayers.from_font"])
			self.w.to_font.set(Glyphs.defaults["com.mekkablue.CopyGlyphsIntoBackupLayers.to_font"])
			self.w.suffix.set(Glyphs.defaults["com.mekkablue.CopyGlyphsIntoBackupLayers.suffix"])
		except:
			return False

		return True

	def GetFonts(self, isSourceFont):
		myFontList = ["%s - %s" % (x.font.familyName, x.selectedFontMaster().name) for x in Glyphs.orderedDocuments()]

		if isSourceFont:
			myFontList.reverse()

		return myFontList

	def buttonCheck(self, sender):
		fromFont = self.w.from_font.getItems()[self.w.from_font.get()]
		toFont = self.w.to_font.getItems()[self.w.to_font.get()]

		if fromFont == toFont:
			self.w.copybutton.enable(onOff=False)
		else:
			self.w.copybutton.enable(onOff=True)

	def CopyGlyphsIntoBackupLayersMain(self, sender):
		try:
			fromFont = self.w.from_font.getItems()[self.w.from_font.get()]
			toFont = self.w.to_font.getItems()[self.w.to_font.get()]
			layerSuffix = self.w.suffix.get()

			Doc_source = [x for x in Glyphs.orderedDocuments() if ("%s - %s" % (x.font.familyName, x.selectedFontMaster().name)) == fromFont][0]
			Font_source = Doc_source.font
			Font_target = [x.font for x in Glyphs.orderedDocuments() if ("%s - %s" % (x.font.familyName, x.selectedFontMaster().name)) == toFont][0]

			MasterID_source = Font_source.selectedFontMaster.id
			MasterID_target = Font_target.selectedFontMaster.id

			Glyphs_selected = [layer.parent for layer in Font_target.selectedLayers]

			print("Backing up", len(Glyphs_selected), "glyphs from", Font_source.familyName, "into", Font_target.familyName, ":")

			for targetGlyph in Glyphs_selected:
				glyphName = targetGlyph.name
				try:
					sourceGlyph = Font_source.glyphs[glyphName]
				except:
					sourceGlyph = None
					print("  Error: glyph %s not found in source font %s." % (glyphName, Font_source.familyName))

				if sourceGlyph:
					sourceLayer = sourceGlyph.layers[MasterID_source].copy()
					targetMasterName = targetGlyph.layers[MasterID_target].name

					targetGlyph.layers[MasterID_source] = sourceLayer
					targetGlyph.layers[MasterID_source].setAssociatedMasterId_(MasterID_target)
					targetGlyph.layers[MasterID_source].setName_("%s %s" % (targetMasterName, layerSuffix))

			if not self.SavePreferences(self):
				print("Note: 'Copy glyphs into backup layers' could not write preferences.")

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Script Error: %s" % e)


CopyGlyphsIntoBackupLayers()
