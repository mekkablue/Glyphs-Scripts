#MenuTitle: Turn offcurve points oncurve
"""Turns BCPs into regular line points."""

Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	thisLayer.undoManager().beginUndoGrouping()

	for thisPath in thisLayer.paths:
		for x in reversed( range( len( thisPath.nodes ))):
			thisNode = thisPath.nodes[x]
			if thisNode.type != 1:
				thisNode.type = 1

	thisLayer.undoManager().endUndoGrouping()

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print "Processing", thisLayer.parent.name
	process( thisLayer )

Font.enableUpdateInterface()

