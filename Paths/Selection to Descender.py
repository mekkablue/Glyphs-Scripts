#MenuTitle: Align Selection to Descender
"""Align selected paths (and parts of paths) in the frontmost layer to the Descender."""

import GlyphsApp

Font = Glyphs.font
myDescender = Font.selectedFontMaster.descender
selectedLayer = Font.selectedLayers[0]

try:
	selection = selectedLayer.selection()
	lowestY = min( ( n.y for n in selection ) )
	
	selectedLayer.setDisableUpdates()
	
	for thisNode in selection:
		thisNode.y -= ( lowestY - myDescender )
	
	selectedLayer.setDisableUpdates()

except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
