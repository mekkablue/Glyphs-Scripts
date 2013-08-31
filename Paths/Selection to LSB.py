#MenuTitle: Align Selection to LSB
"""Align selected paths (and parts of paths) in the frontmost layer to the LSB."""

import GlyphsApp

Font = Glyphs.font
selectedLayer = Font.selectedLayers[0]

try:
	selection = selectedLayer.selection()
	leftMostX = min( ( n.x for n in selection ) )
	
	selectedLayer.setDisableUpdates()
	
	for thisNode in selection:
		thisNode.x -= leftMostX
	
	selectedLayer.setEnableUpdates()

except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
