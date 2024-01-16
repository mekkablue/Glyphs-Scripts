# MenuTitle: Cycle CPAL Colors for Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Will increase the color index for each CPAL Color Palette layer, or set to 0 if it exceeds the number of available colors. E.g., for three colors, it will cycle indexes like this: 0→1, 1→2, 2→0.
"""

from GlyphsApp import Glyphs


def process(thisGlyph, maxColor):
	for layer in thisGlyph.layers:
		paletteIndex = layer.attributes["colorPalette"]
		if paletteIndex is not None:
			paletteIndex += 1
			layer.attributes["colorPalette"] = paletteIndex % maxColor


thisFont = Glyphs.font  # frontmost font
thisFontMaster = thisFont.selectedFontMaster  # active master
selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs
Glyphs.clearLog()  # clears log in Macro window

# get the most relevant color palette:
palettes = thisFontMaster.customParameters["Color Palettes"]
if not palettes:
	for thisMaster in thisFont.masters:
		palettes = thisMaster.customParameters["Color Palettes"]
		if palettes:
			break
if not palettes:
	palettes = thisFont.customParameters["Color Palettes"]

if palettes:
	maxColor = len(palettes[0])  # determine number of colors

	thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
	try:
		for thisLayer in selectedLayers:
			thisGlyph = thisLayer.parent
			print(f"Cycling colors in {thisGlyph.name}")
			thisGlyph.beginUndo()  # begin undo grouping
			process(thisGlyph, maxColor)
			thisGlyph.endUndo()  # end undo grouping
	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ Error in script: Cycle CPAL Colors for Selected Glyphs\n")
		import traceback
		print(traceback.format_exc())
		print()
		raise e
	finally:
		thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
