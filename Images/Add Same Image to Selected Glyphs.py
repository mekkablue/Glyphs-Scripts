#MenuTitle: Add Same Image to Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Asks you for an image file and inserts it as background image into all selected layers.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	try:
		thisImage = GSBackgroundImage.alloc().initWithPath_(imageFilePath)
		thisLayer.setBackgroundImage_( thisImage )
	except Exception as e:
		if "NoneType" in str(e):
			return "No image found."
		else:
			return "Error: %s." % e
	return "OK."

Font.disableUpdateInterface()

imageFilePath = GetOpenFile(
	message = "Select an image:",
	allowsMultipleSelection = False,
	filetypes = ["jpeg", "png", "tif", "gif", "pdf"]
)

print("Putting %s into:" % imageFilePath)

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	print("-- %s: %s" % ( thisGlyph.name, process( thisLayer ) ))
	thisGlyph.endUndo()

Font.enableUpdateInterface()
