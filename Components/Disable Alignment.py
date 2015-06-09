#MenuTitle: Disable Alignment for Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Disables automatic alignment for all components in all selected glyphs.
"""

import GlyphsApp

thisFont = Glyphs.font
selectedLayers = thisFont.selectedLayers

def process( thisLayer ):
	for thisComp in thisLayer.components:
		thisComp.setDisableAlignment_( True )

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Disabling auto-alignment in", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
