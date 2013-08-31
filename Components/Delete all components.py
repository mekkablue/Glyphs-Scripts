#MenuTitle: Delete all components
"""Deletes all components in selected glyphs."""

import GlyphsApp

Font  = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	thisLayer.components = None

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	process( thisLayer )
