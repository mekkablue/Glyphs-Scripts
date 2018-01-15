#MenuTitle: Copy Glyph Name List
# -*- coding: utf-8 -*-
__doc__="""
Copies a newline-separated list of glyph names to the clipboard.
"""


from AppKit import NSPasteboard

separator = "\n"
thisFont = Glyphs.font # frontmost font
listOfGlyphNames = [ l.parent.name for l in thisFont.selectedLayers ]
clipboardText = separator.join( listOfGlyphNames )

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

if not setClipboard(clipboardText):
	print "Warning: could not set clipboard to %s" % ( clipboardText )
