#MenuTitle: Enable Alignment for Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Enables automatic alignment for all components in all selected glyphs.
"""

import GlyphsApp

thisFont = Glyphs.font # frontmost font
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisLayer ):
	for thisComp in thisLayer.components:
		thisComp.setDisableAlignment_( False )
			
thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Enabling auto-alignment in", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	for thisVeryLayer in thisGlyph.layers:
		process( thisVeryLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
