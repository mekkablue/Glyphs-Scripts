#MenuTitle: Align Selection to x-Height
"""Align selected paths (and parts of paths) in the frontmost layer to the x-Height."""

import GlyphsApp

Doc = Glyphs.currentDocument
myXHeight = Doc.selectedFontMaster().xHeight
selectedLayer = Doc.selectedLayers()[0]

try:
	selection = selectedLayer.selection()
	highestY = max( ( n.y for n in selection ) )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.y += ( myXHeight - highestY )

	Font.enableUpdateInterface()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
