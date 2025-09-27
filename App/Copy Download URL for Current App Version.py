# MenuTitle: Copy Download URL for Current App Version
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Puts the download URL of the current Glyphs app version into your clipboard for easy pasting.
"""

from AppKit import NSPasteboard, NSStringPboardType
from GlyphsApp import Glyphs, Message
from mekkablue import setClipboard


appURL = "https://updates.glyphsapp.com/Glyphs%s-%i.zip" % (
	Glyphs.versionString,
	Glyphs.buildNumber,
)

if not setClipboard(appURL):
	print("Warning: could not set clipboard to %s" % ("clipboard text"))
	Message(title="Clipboard Error", message="Could not set the clipboard for whatever reason, so here is the URL:\n%s" % appURL, OKButton=None)
else:
	# Floating notification:
	Glyphs.showNotification(
		"Download link copied",
		"Ready for pasting: %s" % appURL,
	)
