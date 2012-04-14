#MenuTitle: Delete duplicate components
"""Looks for duplicate components (same component, same x/y values) and keeps only one of them."""

import GlyphsApp

Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
FontMaster = Doc.selectedFontMaster()
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def getAttr( thisGlyph, compNumber ):
	return [thisGlyph.components[compNumber].componentName, thisGlyph.components[compNumber].x, thisGlyph.components[compNumber].y]

def scanForDuplicates( thisGlyph, compNumber ):
	# hint: 'thisGlyph' is just the *layer* of the glyph that was passed to the function
	
	if compNumber == len( thisGlyph.components ) - 1:
		return []
	else:
		indexList = scanForDuplicates( thisGlyph, compNumber + 1 )
		currAttr = getAttr( thisGlyph, compNumber )
		
		for i in range( compNumber + 1, len( thisGlyph.components ) ):
			if currAttr == getAttr( thisGlyph, i ):
				indexList.append(i)
		
		return sorted( set( indexList ) )

def process( thisGlyph ):
	thisLayer = thisGlyph.layers[FontMaster.id]
	
	if len( thisLayer.components ) != 0:
		thisGlyph.undoManager().disableUndoRegistration()
	
		indexesToBeDeleted = scanForDuplicates( thisLayer, 0 )
		for indexToBeDeleted in indexesToBeDeleted[::-1]:
			del thisLayer.components[indexToBeDeleted]
		print len( indexesToBeDeleted )
	
		thisGlyph.undoManager().enableUndoRegistration()
	else:
		print "n/a"
	

Font.willChangeValueForKey_("glyphs")

for thisGlyph in selectedGlyphs:
	print "Components deleted in %s:" % thisGlyph.name,
	process( thisGlyph )

Font.didChangeValueForKey_("glyphs")

