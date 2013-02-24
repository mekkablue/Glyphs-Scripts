#MenuTitle: Delete duplicate components
"""Looks for duplicate components (same component, same x/y values) and keeps only one of them."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedLayers = Doc.selectedLayers()


def getAttr( thisLayer, compNumber ):
	return [thisLayer.components[compNumber].componentName, thisLayer.components[compNumber].x, thisLayer.components[compNumber].y]


def scanForDuplicates( thisLayer, compNumber ):
	if compNumber == len( thisLayer.components ) - 1:
		return []
	else:
		indexList = scanForDuplicates( thisLayer, compNumber + 1 )
		currAttr = getAttr( thisLayer, compNumber )
		
		for i in range( compNumber + 1, len( thisLayer.components ) ):
			if currAttr == getAttr( thisLayer, i ):
				indexList.append(i)
		
		return sorted( set( indexList ) )


def process( thisLayer ):
	if len( thisLayer.components ) != 0:
		thisLayer.parent.undoManager().beginUndoGrouping()
	
		indexesToBeDeleted = scanForDuplicates( thisLayer, 0 )
		for indexToBeDeleted in indexesToBeDeleted[::-1]:
			del thisLayer.components[indexToBeDeleted]
		print len( indexesToBeDeleted )
	
		thisLayer.parent.undoManager().endUndoGrouping()
	else:
		# no components in this layer
		print "n/a" 


Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print "Components deleted in %s:" % thisLayer.parent.name,
	process( thisLayer )

Font.enableUpdateInterface()
