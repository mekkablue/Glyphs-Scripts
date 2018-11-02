#MenuTitle: Decompose Background
# -*- coding: utf-8 -*-
__doc__="""
Decomposes components in the Background.
"""



thisFont = Glyphs.font # frontmost font

def process( thisLayer ):
	background = thisLayer.background
	if background.components:
		background.decomposeComponents()

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in thisFont.selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
