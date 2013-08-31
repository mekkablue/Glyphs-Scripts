#MenuTitle: Align Selection to RSB
"""Align selected paths (and parts of paths) in the frontmost layer to the RSB."""

import GlyphsApp

Font = Glyphs.font
selectedLayer = Doc.selectedLayers[0]
layerWidth = selectedLayer.width

try:
	selection = selectedLayer.selection()
	rightMostX = max( ( n.x for n in selection ) )
	
	selectedLayer.setDisableUpdates()
	
	for thisNode in selection:
		thisNode.x += ( layerWidth - rightMostX )
	
	selectedLayer.setEnableUpdates()

except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
