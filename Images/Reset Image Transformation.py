from __future__ import print_function
#MenuTitle: Reset Image Transformations
# -*- coding: utf-8 -*-
__doc__="""
Resets all placed images to 100% scale and 0/0 position.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	thisImage = thisLayer.backgroundImage
	if thisImage:
		thisImage.transform = ((1.0, 0.0, 0.0, 1.0, 0.0, 0.0))

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print("Resetting image in", thisGlyph.name)
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
