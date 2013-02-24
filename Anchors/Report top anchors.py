#MenuTitle: Report top positions
"""Reports the y positions of the top anchors in selected glyphs."""

import GlyphsApp
myAnchor = "top"

Doc  = Glyphs.currentDocument
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	try:
		myY = thisLayer.anchors[ myAnchor ].y
		print thisLayer.parent.name, "--->", myY
	except Exception, e:
		print thisLayer.parent.name, "has no %s anchor." % myAnchor

for thisLayer in selectedLayers:
	process( thisLayer )
