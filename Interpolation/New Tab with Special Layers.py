# MenuTitle: New Tab with Special Layers
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Opens a new Edit tab containing all special (bracket & brace) layers.
"""

from GlyphsApp import Glyphs, Message


Glyphs.clearLog()  # clears log of Macro window
thisFont = Glyphs.font  # frontmost font
affectedLayers = []
for thisGlyph in thisFont.glyphs:  # loop through all glyphs
	for thisLayer in thisGlyph.layers:  # loop through all layers
		# collect affected layers:
		if thisLayer.isSpecialLayer:
			affectedLayers.append(thisLayer)

# open a new tab with the affected layers:
if affectedLayers:
	newTab = thisFont.newTab()
	newTab.layers = affectedLayers
# otherwise send a message:
else:
	Message(title="Nothing Found", message="Could not find any bracket or brace layers in the font.", OKButton=None)
