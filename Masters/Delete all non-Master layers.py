#MenuTitle: Delete all non-Master layers
# -*- coding: utf-8 -*-
__doc__="""
Goes through selected glyphs and deletes all glyph layers which are not a Master, Bracket or Brace layer.
"""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers
searchTerms = [ "[]", "{}" ]

def process( thisGlyph ):
	count = 0
	
	numberOfLayers = len( thisGlyph.layers )
	for i in range( numberOfLayers )[::-1]:
		thisLayer = thisGlyph.layers[i]
		if thisLayer.layerId != thisLayer.associatedMasterId:
			thisLayerName = thisLayer.name
			thisLayerShouldBeRemoved = True
			if thisLayerName:
				for parentheses in searchTerms:
					if (thisLayerName.find( parentheses[0] or thisLayerName.find( parentheses[1]) and (thisLayerName.endswith( parentheses[0] or thisLayerName.endswith( parentheses[1]) ):
						thisLayerShouldBeRemoved = False
			if thisLayerShouldBeRemoved:
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
