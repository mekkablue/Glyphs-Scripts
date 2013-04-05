#MenuTitle: Align Selection to LSB
"""Align selected paths (and parts of paths) in the frontmost layer to the LSB."""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
selectedLayer = Doc.selectedLayers()[0]

try:
	selection = selectedLayer.selection()
	leftMostX = min( ( n.x for n in selection ) )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.x -= leftMostX

	Font.enableUpdateInterface()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
