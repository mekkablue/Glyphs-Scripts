#MenuTitle: Add All Color Layers to Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds a duplicate of the fallback layer for each color defined in the Color Palettes parameter, for each selected glyph.
"""

def process( thisGlyph, mID, paletteSize ):
	for i in range(paletteSize):
		newLayer = thisGlyph.layers[mID].copy()
		try:
			# GLYPHS 3
			newLayer.setColorPaletteLayer_(1)
			newLayer.setAttribute_forKey_(i, "colorPalette")
		except:
			# GLYPHS 2
			newLayer.name = "Color %i" % i
		thisGlyph.layers.append(newLayer)

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
selectedGlyphs = [l.parent for l in selectedLayers]
Glyphs.clearLog() # clears log in Macro window

CPAL = None
parameterName = "Color Palettes"

for m in thisFont.masters:
	mID = m.id
	CPAL = m.customParameters[parameterName]
		
if not CPAL:
	CPAL = thisFont.customParameters[parameterName]

if CPAL:
	paletteSize = len(CPAL[0])
	for thisGlyph in selectedGlyphs:
		print("Processing %s" % thisGlyph.name)
		process( thisGlyph, mID, paletteSize )
else:
	Message(
		title="No Palette Found",
		message="No ‘Color Palettes’ parameter found in Font Info > Font or Font Info > Masters. Please add the parameter and try again.", 
		OKButton=None,
		)