#MenuTitle: Move top anchors (no GUI)
"""Moves top anchors in selected glyphs to a specified new y value"""

new_y = 687.0
myAnchor = "top"

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	try:
		thisLayer.anchors[myAnchor].y = new_y
		print "Moved", myAnchor, "in", thisLayer.parent.name, "to", new_y
	except Exception, e:
		pass

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	#print "Processing", thisLayer.parent.name
	process( thisLayer )

Font.enableUpdateInterface()

