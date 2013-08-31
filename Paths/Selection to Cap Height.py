#MenuTitle: Align Selection to Cap Height
"""Align selected paths (and parts of paths) in the frontmost layer to the Cap Height."""

import GlyphsApp

Font = Glyphs.font
myCapHeight = Font.selectedFontMaster.capHeight
selectedLayer = Font.selectedLayers[0]

try:
	selection = selectedLayer.selection()
	highestY = max( ( n.y for n in selection ) )
	
	selectedLayer.setDisableUpdates()
	
	# you could use GSLayer.transform_checkForSelection_(transform, checkForSelection=YES)
	for thisNode in selection:
		thisNode.y += ( myCapHeight - highestY )
	
	selectedLayer.setEnableUpdates()
	

except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
