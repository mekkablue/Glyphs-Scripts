#MenuTitle: Decompose all corners
# -*- coding: utf-8 -*-
__doc__="""
Decomposes all corners.
"""

import GlyphsApp

thisFont = Glyphs.font
selectedLayers = thisFont.selectedLayers

def process( thisLayer ):
	thisLayer.decomposeCorners()
	print "-- Decomposed all corners"

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()
