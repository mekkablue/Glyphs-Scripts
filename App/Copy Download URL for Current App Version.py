#MenuTitle: Copy Download URL for Current App Version
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Puts the download URL of the current Glyphs app version into your clipboard for easy pasting.
"""

from AppKit import NSPasteboard, NSStringPboardType

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

appURL = "https://updates.glyphsapp.com/Glyphs%s-%s.zip" % (
	Glyphs.versionString,
	Glyphs.buildNumber,
)

if not setClipboard(appURL):
	print("Warning: could not set clipboard to %s" % ( "clipboard text" ))
	Message(title="Clipboard Error", message="Could not set the clipboard for whatever reason, so here is the URL:\n%s"%appURL, OKButton=None)
else:
	# Floating notification:
	Glyphs.showNotification( 
		"Download link copied",
		"Ready for pasting: %s"%appURL,
		)
	