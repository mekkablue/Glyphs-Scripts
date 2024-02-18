# MenuTitle: Rename Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Takes a list of oldglyphname=newglyphname pairs and renames glyphs in the font accordingly, much like the Rename Glyphs parameter.
"""

import vanilla
import uuid
from AppKit import NSFont
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class RenameGlyphs(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"renameList": "oldname=newname",
		"allFonts": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 200
		windowWidthResize = 800  # user can resize width by this value
		windowHeightResize = 800  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Rename Glyphs",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		self.w.text_1 = vanilla.TextBox((10, 12 + 2, -10, 14), "Add lines like oldname=newname:", sizeStyle='small')
		self.w.renameList = vanilla.TextEditor((1, 40, -1, -40), "oldname=newname", callback=self.SavePreferences)
		self.w.renameList.getNSTextView().setFont_(NSFont.userFixedPitchFontOfSize_(-1.0))
		self.w.renameList.getNSTextView().turnOffLigatures_(1)
		self.w.renameList.getNSTextView().useStandardLigatures_(0)
		self.w.renameList.selectAll()

		self.w.allFonts = vanilla.CheckBox((10, -35, 100, 20), "⚠️ ALL Fonts", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Run Button:
		self.w.runButton = vanilla.Button((-100, -35, -15, -15), "Rename", sizeStyle='regular', callback=self.RenameGlyphsMain)
		# self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def RenameGlyphsMain(self, sender):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if self.pref("allFonts"):
				theseFonts = Glyphs.fonts
			else:
				theseFonts = [Glyphs.font, ]

			for thisFont in theseFonts:
				for thisLine in self.pref("renameList").splitlines():
					if thisLine.strip():
						glyphNameLeft = thisLine.split("=")[0].strip()
						glyphNameRight = thisLine.split("=")[1].strip()
						glyphLeft = thisFont.glyphs[glyphNameLeft]
						glyphRight = thisFont.glyphs[glyphNameRight]
						if glyphLeft:
							if glyphRight:
								uniqueSuffix = ".%s" % uuid.uuid4().hex
								glyphLeft.name = glyphNameRight + uniqueSuffix
								glyphRight.name = glyphNameLeft
								glyphLeft.name = glyphNameRight

								# swap export status:
								glyphLeftExport = glyphLeft.export
								glyphLeft.export = glyphRight.export
								glyphRight.export = glyphLeftExport
							else:
								glyphLeft.name = glyphNameRight
						else:
							print(f"Warning: {glyphNameLeft} not in font.")

			self.SavePreferences()

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Rename Glyphs Error: {e}")
			import traceback
			print(traceback.format_exc())


RenameGlyphs()
