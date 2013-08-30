#MenuTitle: Delete All Hints in Font
"""Delete all hints throughout the whole font."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
totalDeletedHints = 0

print "Deleting all hints in %s ..." % Font.familyName

def process( thisGlyph ):
	deletedHintsCount = 0
	
	for l in thisGlyph.layers:
		deletedHintsCount += len( l.hints )
		l.hints = None
	
	return deletedHintsCount

for thisGlyph in Font.glyphs:
	totalDeletedHints += process( thisGlyph )

print "Done: removed %i hints." % totalDeletedHints
