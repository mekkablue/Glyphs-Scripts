#MenuTitle: Delete components out of bounds
"""Looks for components out of bounds."""

import GlyphsApp

Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
FontMaster = Doc.selectedFontMaster()
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

outOfBounds = 3000.0

def getAttr( thisGlyph, compNumber ):
	return [thisGlyph.components[compNumber].componentName, thisGlyph.components[compNumber].x, thisGlyph.components[compNumber].y]

def scanForDuplicates( thisGlyph ):
	# hint: 'thisGlyph' is just the *layer* of the glyph that was passed to the function
	
	complist = [c for c in thisGlyph.components]
	indexesToBeDeleted = []

	for i in range( len( complist )):
		c = complist[i]
		#print i, c.componentName, int(c.x), int(c.y)
		if c.y > outOfBounds or c.y < -outOfBounds or c.x < -outOfBounds or c.x > outOfBounds:
			indexesToBeDeleted.append(i)
	
	return sorted( set( indexesToBeDeleted ) )

def process( thisGlyph ):
	thisLayer = thisGlyph.layers[FontMaster.id]
	
	if len( thisLayer.components ) != 0:
		thisGlyph.undoManager().disableUndoRegistration()
	
		indexesToBeDeleted = scanForDuplicates( thisLayer )
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

