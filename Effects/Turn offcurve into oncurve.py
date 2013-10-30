#MenuTitle: Turn offcurve into oncurve points
"""Turns BCPs into regular nodes. Turns all curves into straight lines."""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

GSLINE = 1

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		for x in reversed( range( len( thisPath.nodes ))):
			thisNode = thisPath.nodes[x]
			if thisNode.type != GSLINE:
				thisNode.type = GSLINE
		
		thisPath.checkConnections()

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()

