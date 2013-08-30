#MenuTitle: Retract BCPs
"""Retracts all BCPs (off-curve points) in selected glyphs, so all curves will be turned into straight lines."""

import GlyphsApp

Font = Glyphs.font
Doc  = Glyphs.currentDocument
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		for x in reversed( range( len( thisPath.nodes ))):
			thisNode = thisPath.nodes[x]
			if thisNode.type == GSOFFCURVE:
				del thisPath.nodes[x]
			else:
				thisNode.type = GSLINE
		
		thisPath.checkConnections()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisLayer.setDisableUpdates()
	thisLayer.parent.beginUndo()
	process( thisLayer )
	thisLayer.parent.endUndo()
	thisLayer.setEnableUpdates()
