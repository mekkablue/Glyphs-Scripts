# MenuTitle: Reverse CPAL Colors for Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Will reverse the color indexes for each CPAL Color Palette layer. E.g., for three colors, it will turn indexes 0,1,2 into 2,1,0.
"""

from GlyphsApp import Glyphs


def process(thisGlyph):
	indexes = []
	for colorLayer in thisGlyph.layers:
		colorIndex = colorLayer.attributeForKey_("colorPalette")
		if colorLayer.isSpecialLayer and colorIndex is not None:
			indexes.append(colorIndex)
	for colorLayer in thisGlyph.layers:
		colorIndex = colorLayer.attributeForKey_("colorPalette")
		if colorLayer.isSpecialLayer and colorIndex is not None:
			colorLayer.setAttribute_forKey_(indexes.pop(), "colorPalette")


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
	thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
	try:
		for thisLayer in selectedLayers:
			thisGlyph = thisLayer.parent
			print(f"Reversing colors in {thisGlyph.name}")
			thisGlyph.beginUndo()  # begin undo grouping
			process(thisGlyph)
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
