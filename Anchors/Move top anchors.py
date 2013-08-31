#MenuTitle: Move top anchors (no GUI)
"""Moves top anchors in selected glyphs to a y value specified in the script file."""

new_y = 610.0
myAnchor = "top"

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	try:
		thisLayer.anchors[myAnchor].y = new_y
		print "Moved", myAnchor, "in", thisLayer.parent.name, "to", new_y
	except Exception, e:
		pass

for thisLayer in selectedLayers:
	#print "Processing", thisLayer.parent.name
	process( thisLayer )

