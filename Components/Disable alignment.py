#MenuTitle: Disable alignment for selected glyphs
# -*- coding: utf-8 -*-
"""Disables automatic alignment for all components in all selected glyphs."""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	for thisComp in thisLayer.components:
		thisComp.setDisableAlignment_( True )

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Disabling automatic alignment in", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
