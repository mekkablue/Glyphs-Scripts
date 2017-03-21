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
		if thisLayer.layerId != thisLayer.associatedMasterId: # not the master layer
			thisLayerName = thisLayer.name
			thisLayerShouldBeRemoved = True
			if thisLayerName: # always delete unnamed layers
				for parentheses in searchTerms:
					opening = parentheses[0]
					closing = parentheses[1]
					
					# check if ONE of them is at the END of the layer name, like:
					# Bold [160], Bold [160[, Bold ]160], Regular {120}
					if thisLayerName.endswith(opening) or thisLayerName.endswith(closing):
						thisLayerShouldBeRemoved = False
						
			if thisLayerShouldBeRemoved:
				count += 1
				del thisGlyph.layers[i]
			
	return count

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyphName = thisGlyph.name

	if str(thisGlyphName)[:7] != "_part.":
		thisGlyph.beginUndo()
		print "%s layers deleted in %s." % ( process( thisGlyph ), thisGlyphName )
		thisGlyph.endUndo()
	else:
		print "Smart layers kept in %s." % ( thisGlyphName )

Font.enableUpdateInterface()
