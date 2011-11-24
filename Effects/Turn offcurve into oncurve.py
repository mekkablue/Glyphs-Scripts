#MenuTitle: Turn offcurve points oncurve
"""Turns BCPs into regular line points."""

Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
selectedLayers = Doc.selectedLayers()
GSOFFCURVE = 65

def process( thisLayer ):
	#thisLayer.undoManager().disableUndoRegistration()

	for thisPath in thisLayer.paths:
		for x in reversed( range( len( thisPath.nodes ))):
			thisNode = thisPath.nodes[x]
			if thisNode.type != 1:
				thisNode.type = 1

	#thisLayer.undoManager().enableUndoRegistration()

Font.willChangeValueForKey_("glyphs")

for thisLayer in selectedLayers:
	print "Processing", thisLayer.parent.name
	process( thisLayer )

Font.didChangeValueForKey_("glyphs")

