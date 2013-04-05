#MenuTitle: Close all open paths
"""Close all paths in visible layers of selected glyphs."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		if not thisPath.closed:
			thisPath.closed = True

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print "Closing paths in", thisLayer.parent.name
	process( thisLayer )

Font.enableUpdateInterface()

