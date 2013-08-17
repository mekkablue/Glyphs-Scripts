#MenuTitle: Delete All Hints in Font
"""Delete all hints throughout the whole font."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
totalDeletedHints = 0

print "Deleting all hints in %s ..." % Font.familyName

def deleteHintsInLayer( thisLayer ):
	numOfHints = len( thisLayer.hints )
	for x in reversed( range( numOfHints )):
		del thisLayer.hints[x]
	
	return numOfHints

def process( thisGlyph ):
	deletedHintsCount = 0
	
	for l in thisGlyph.layers:
		deletedHintsCount += deleteHintsInLayer( l )
	
	return deletedHintsCount

Font.disableUpdateInterface()

for thisGlyph in Font.glyphs:
	totalDeletedHints += process( thisGlyph )

Font.enableUpdateInterface()

print "Done: removed %i hints." % totalDeletedHints
