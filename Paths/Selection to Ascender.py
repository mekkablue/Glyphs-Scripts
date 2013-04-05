#MenuTitle: Align Selection to Ascender
"""Align selected paths (and parts of paths) in the frontmost layer to the Ascender."""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
myAscender = Doc.selectedFontMaster().ascender
selectedLayer = Doc.selectedLayers()[0]

try:
	selection = selectedLayer.selection()
	highestY = max( ( n.y for n in selection ) )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.y += ( myAscender - highestY )

	Font.enableUpdateInterface()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
