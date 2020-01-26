#MenuTitle: Add All Color Layers to Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds a duplicate of the fallback layer for each color defined in the Color Palettes parameter, for each selected glyph.
"""

def process( thisGlyph, mID, paletteSize ):
	for i in range(paletteSize):
		newLayer = thisGlyph.layers[mID].copy()
		newLayer.name = "Color %i" % i
		thisGlyph.layers.append(newLayer)

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
selectedGlyphs = [l.parent for l in selectedLayers]
Glyphs.clearLog() # clears log in Macro window

for m in Font.masters:
	mID = m.id
	CPAL = m.customParameters["Color Palettes"]
	if CPAL:
		paletteSize = len(CPAL[0])
		for thisGlyph in selectedGlyphs:
			print("Processing %s" % thisGlyph.name)
			process( thisGlyph, mID, paletteSize )
