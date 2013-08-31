#MenuTitle: Align Selection to Ascender
"""Align selected paths (and parts of paths) in the frontmost layer to the Ascender."""

import GlyphsApp

Font = Glyphs.font

myAscender = Font.selectedFontMaster.ascender
selectedLayer = Font.selectedLayers[0]

try:
	selection = selectedLayer.selection()
	highestY = max( ( n.y for n in selection ) )
	
	selectedLayer.setDisableUpdates()
	
	for thisNode in selection:
		thisNode.y += ( myAscender - highestY )
	selectedLayer.setEnableUpdates()

except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
