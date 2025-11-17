#MenuTitle: New Tabs with Palette Colors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens new tabs, one each for all layers pertaining to a color index (CPAL/COLR).
"""

def countColors(font):
	colors = []
	palettes = font.customParameters["Color Palettes"]
	if not palettes:
		return None
	palette = palettes[0]
	return len(palette)

def newTabWithColorIndex(font, requestedIndex=0, includeInactive=False, colorKey="colorPalette"):
	layers = []
	for glyph in font.glyphs:
		if not glyph.export and not includeInactive:
			continue
		for layer in glyph.layers:
			if not layer.attributes:
				continue
			if not colorKey in layer.attributes.keys():
				continue
			paletteIndex = layer.attributes[colorKey]
			if paletteIndex == requestedIndex:
				layers.append(layer)
	tab = font.newTab()
	tab.layers = layers
	return len(layers)

Glyphs.clearLog() # clears log of Macro window
affectedLayers = 0
thisFont = Glyphs.font # frontmost font
for colorIndex in range(countColors(thisFont)):
	affectedLayers += newTabWithColorIndex(thisFont, requestedIndex=colorIndex)


# open a new tab with the affected layers:
if affectedLayers == 0:
	Message(
		title = "Nothing Found",
		message = f"Could not find any glyphs with CPAL layers in font ‘{thisFont.familyName}’.",
		OKButton = None
	)
	
