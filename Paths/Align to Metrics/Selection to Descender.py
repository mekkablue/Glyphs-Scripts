#MenuTitle: Align Selection to Descender
"""Align selected paths (and parts of paths) in the frontmost layer to the Descender."""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
myDescender = Font.selectedFontMaster.descender
selectedLayer = Font.selectedLayers[0]

try:
	selection = selectedLayer.selection()
	lowestY = min( ( n.y for n in selection ) )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.y -= ( lowestY - myDescender )

	Font.enableUpdateInterface()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
