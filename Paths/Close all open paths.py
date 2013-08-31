#MenuTitle: Close all open paths
"""Close all paths in visible layers of selected glyphs."""

import GlyphsApp

selectedLayers = Glyphs.font.selectedLayers

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		if not thisPath.closed:
			thisPath.closed = True

for thisLayer in selectedLayers:
	thisLayer.setDisableUpdates()
	print "Closing paths in", thisLayer.parent.name
	process( thisLayer )
	thisLayer.setEnableUpdates()


