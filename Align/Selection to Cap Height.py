#MenuTitle: Align Selection to Cap Height
"""Align selected paths (and parts of paths) in the frontmost layer to the Cap Height."""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
myCapHeight = Doc.selectedFontMaster().capHeight
selectedLayer = Doc.selectedLayers()[0]

try:
	selection = selectedLayer.selection()
	highestY = max( ( n.y for n in selection ) )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.y += ( myCapHeight - highestY )

	Font.enableUpdateInterface()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
