#MenuTitle: Reset Image Transformations
# -*- coding: utf-8 -*-
"""Resets all placed images to 100% scale and 0/0 position."""

import GlyphsApp
Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	thisImage = thisLayer.backgroundImage()
	thisImage.setTransformStruct_( (1.0, 0.0, 0.0, 1.0, 0.0, 0.0) )

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Resetting image in", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
