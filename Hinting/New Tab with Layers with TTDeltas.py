#MenuTitle: New Tab with Layers with TTDeltas
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens new tab with layers with deltas.
"""
font = Glyphs.font
layersWithDelta = []
for thisGlyph in font.glyphs:
	for thisLayer in thisGlyph.layers:
		for thisHint in thisLayer.hints:
			if thisHint.type == TTDELTA:
				if thisLayer not in layersWithDelta:
					layersWithDelta.append(thisLayer)
font.newTab(layersWithDelta)