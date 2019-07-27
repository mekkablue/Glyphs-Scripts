#MenuTitle: Remove Short Segments
# -*- coding: utf-8 -*-
__doc__="""
Deletes single-unit segments.
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		for i in range(len(thisPath.nodes))[::-1]:
			thisNode = thisPath.nodes[i]
			prevNode = thisNode.prevNode
			if prevNode.type != OFFCURVE and thisNode.type != OFFCURVE:
				xDistance = thisNode.x-prevNode.x
				yDistance = thisNode.y-prevNode.y
				if abs(xDistance) < 1.0 and abs(yDistance) < 1.0:
					thisPath.removeNodeCheckKeepShape_( thisNode )

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing %s" % thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
