# MenuTitle: Merge CPAL Layers into Master Layer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Takes all CPAL/COLR layers and puts copies of their shapes into the master layer.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


allOptions = (
	"selected CPAL/COLR glyphs in current font",
	"⚠️ ALL CPAL/COLR glyphs in current font",
	"⚠️ ALL CPAL/COLR glyphs in ⚠️ ALL fonts",
)


class MergeCPALLayersIntoMasterLayer(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"overwrite": 1,
		"all": 0,
		"verbose": 0,
		"removeOverlap": 1,
		"removeSmallItems": 1,
		"removeSmallItemsThreshold": 400,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 180
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Merge CPAL Layers into Master Layer",  # window title
			minSize=(windowWidth, windowHeight + 19),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize + 19),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Merge CPAL/COLR shapes into master layers", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.allText = vanilla.TextBox((inset, linePos + 2, 30, 14), "for:", sizeStyle="small", selectable=True)
		self.w.all = vanilla.PopUpButton((inset + 30, linePos, -inset, 17), allOptions, sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight
		
		self.w.removeOverlap = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Remove overlap and tidy up paths", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.removeSmallItems = vanilla.CheckBox((inset, linePos-1, 160, 20), "Remove items smaller than", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.removeSmallItemsThreshold = vanilla.EditText((inset+160, linePos-1, 40, 19), "400", callback=self.SavePreferences, sizeStyle="small")
		self.w.removeSmallItemsText = vanilla.TextBox((inset+205, linePos+2, -inset, 20), "square units", sizeStyle="small")
		linePos += lineHeight
		
		self.w.overwrite = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Overwrite existing master layers", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.verbose = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Verbose reporting in Macro window (slow)", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Merge", callback=self.MergeCPALLayersIntoMasterLayerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def MergeCPALLayersIntoMasterLayerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if not Glyphs.font:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				countGlyphs = 0
				if self.pref("all") > 1: # 0, 1 = current font; 2 = all fonts
					theseFonts = Glyphs.fonts
				else:
					theseFonts = (Glyphs.font, )

				for thisFont in theseFonts:
					filePath = thisFont.filepath
					if filePath:
						reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
					else:
						reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
					print(f"Merge CPAL Layers into Master Layer Report for {reportName}")
					print()

					if self.pref("all") == 0:
						theseGlyphs = [layer.parent for layer in thisFont.selectedLayers]
					else:
						theseGlyphs = thisFont.glyphs

					for thisGlyph in theseGlyphs:
						for m in thisFont.masters:
							# collect shapes from color layers
							collectedShapes = []
							for colorLayer in thisGlyph.layers:
								if not colorLayer.isColorPaletteLayer():
									continue
								if colorLayer.associatedMasterId != m.id:
									continue
								if colorLayer.attributeForKey_("colorPalette") is None:
									continue
								for shape in colorLayer.shapes:
									collectedShapes.append(shape.copy())

							# add to master layer
							if not collectedShapes:
								if self.pref("verbose"):
									print(f"🚫 {thisGlyph.name} Ⓜ️ {m.name}: no color layers, skipping.")
								continue
							masterLayer = thisGlyph.layers[m.id]
							if self.pref("overwrite"):
								masterLayer.shapes = None
							for shape in collectedShapes:
								masterLayer.shapes.append(shape)
							masterLayer.decomposeComponents()
							if self.pref("removeOverlap"):
								masterLayer.removeOverlap()
								masterLayer.cleanUpPaths()
							if self.pref("removeSmallItems"):
								for i in range(len(masterLayer.shapes)-1,-1,-1):
									shape = masterLayer.shapes[i]
									if shape.area() < float(self.pref("removeSmallItemsThreshold")):
										del masterLayer.shapes[i]

							print(f"🌈 {thisGlyph.name}: merged color shapes into Ⓜ️ {m.name}")
							countGlyphs += 1
					print()

				print(f"✅ Done. Merged {countGlyphs} glyph{'' if countGlyphs == 1 else 's'} in {len(theseFonts)} font{'' if len(theseFonts) == 1 else 's'}.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Merge CPAL Layers into Master Layer Error: {e}")
			import traceback
			print(traceback.format_exc())


MergeCPALLayersIntoMasterLayer()
