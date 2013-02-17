#MenuTitle: Move top anchors
"""Moves top anchors to specified y value"""

new_y = 687.0
myAnchor = "top"

import GlyphsApp

Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
FontMaster = Doc.selectedFontMaster()
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	try:
		thisLayer.anchors[myAnchor].y = new_y
		print "Moved", myAnchor, "in", thisLayer.parent.name, "to", str(int(new_y))
		
	except Exception, e:
		pass
	else:
		pass

Font.willChangeValueForKey_("glyphs")

for thisLayer in selectedLayers:
	#print "Processing", thisLayer.parent.name
	process( thisLayer )

Font.didChangeValueForKey_("glyphs")

