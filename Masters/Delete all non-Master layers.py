#MenuTitle: Delete all non-Master layers
# -*- coding: utf-8 -*-
"""Goes through selected glyphs and deletes all glyph layers which are not a Master."""

import GlyphsApp

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers
selection = selectedLayers[0].selection()

def process( thisGlyph ):
	count = 0
	
	numberOfLayers = len( thisGlyph.layers )
	for i in range( numberOfLayers )[::-1]:
		thisLayer = thisGlyph.layers[i]
		if thisLayer.layerId != thisLayer.associatedMasterId:
			count += 1
			del thisGlyph.layers[i]
			
	return count

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent

	thisGlyph.beginUndo()
	print "%s layers deleted in %s." % ( process( thisGlyph ), thisGlyph.name )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
