#MenuTitle: Disable alignment for selected glyphs
# -*- coding: utf-8 -*-
"""Disables automatic alignment for all components in all selected glyphs."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
FontMaster = Doc.selectedFontMaster()
selectedLayers = Doc.selectedLayers()
selection = selectedLayers[0].selection()

def process( thisLayer ):
	for thisComp in thisLayer.components:
		thisComp.setDisableAlignment_(True)

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Disabling automatic alignment in", thisGlyph.name
	thisGlyph.undoManager().beginUndoGrouping()
	process( thisLayer )
	thisGlyph.undoManager().endUndoGrouping()

Font.enableUpdateInterface()
