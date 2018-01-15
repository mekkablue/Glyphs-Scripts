#MenuTitle: Copy Unicode-Sorted Glyph Name List
# -*- coding: utf-8 -*-
__doc__="""
Creates a glyph list of all encoded glyphs, in Unicode order, and puts in your clipboard for pasting.
"""


from AppKit import NSPasteboard

thisFont = Glyphs.font # frontmost font
listOfEncodedGlyphs = [ g for g in thisFont.glyphs if g.unicode ]
listOfSortedGlyphNames = [ g.name for g in sorted( listOfEncodedGlyphs, key = lambda glyph: glyph.unicode ) ]
copyString = "\n".join( listOfSortedGlyphNames )

def setClipboard( myText ):
	"""
	Sets the contents of the clipboard to myText.
	Returns True if successful, False if unsuccessful.
	"""
	try:
		myClipboard = NSPasteboard.generalPasteboard()
		myClipboard.declareTypes_owner_( [NSStringPboardType], None )
		myClipboard.setString_forType_( myText, NSStringPboardType )
		return True
	except Exception as e:
		return False

if not setClipboard( copyString ):
	print "Warning: could not set clipboard."
