#MenuTitle: Delete all non-Master layers
# -*- coding: utf-8 -*-
__doc__="""
Goes through selected glyphs and deletes all glyph layers which are not a Master or a Bracket layer.
"""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisGlyph ):
	count = 0
	
	numberOfLayers = len( thisGlyph.layers )
	for i in range( numberOfLayers )[::-1]:
		thisLayer = thisGlyph.layers[i]
		if thisLayer.layerId != thisLayer.associatedMasterId:
			thisLayerName = thisLayer.name
			# delete layer if it has no name or is a bracket layer ("Name [xxx]")
			if not thisLayerName or thisLayerName.find("[") == -1 or not thisLayerName.endswith("]"):
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
