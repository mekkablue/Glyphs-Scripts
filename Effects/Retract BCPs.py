#MenuTitle: Retract BCPs
"""Retracts all BCPs (off-curve points) in selected glyphs, so all curves will be turned into straight lines."""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

GSOFFCURVE = 65
GSLINE = 1

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		for x in reversed( range( len( thisPath.nodes ))):
			thisNode = thisPath.nodes[x]
			if thisNode.type == GSOFFCURVE:
				del thisPath.nodes[x]
			else:
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

