#MenuTitle: Align Selection to Baseline
"""Align selected paths (and parts of paths) in the frontmost layer to the Baseline."""

import GlyphsApp

Font = Glyphs.font
selectedLayer = Font.selectedLayers[0]

try:
	selection = selectedLayer.selection()
	lowestY = min( ( n.y for n in selection ) )
	
	selectedLayer.setDisableUpdates()
	
	for thisNode in selection:
		thisNode.y -= lowestY
	
	selectedLayer.setEnableUpdates()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
