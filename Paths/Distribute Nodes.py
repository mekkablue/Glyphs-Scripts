#MenuTitle: Distribute Nodes
"""Distributes the selected nodes horizontally or vertically, depending on the bounding box."""

import GlyphsApp

Font = Glyphs.font
selectedLayer = Font.selectedLayers[0]

try:
	selection = selectedLayer.selection()
	selectionXList = [ n.x for n in selection ]
	selectionYList = [ n.y for n in selection ]
	leftMostX, rightMostX = min( selectionXList ), max( selectionXList )
	lowestY, highestY = min( selectionYList ), max( selectionYList )
	diffX = abs(leftMostX-rightMostX)
	diffY = abs(lowestY-highestY)
	
	selectedLayer.setDisableUpdates()
	
	if diffX > diffY:
		increment = diffX // ( len( selection ) - 1 )
		sortedSelection = sorted( selection, key=lambda n: n.x)
		for thisNodeIndex in range( len( selection ) ):
			sortedSelection[thisNodeIndex].x = leftMostX + ( thisNodeIndex * increment )
	else:
		increment = diffY // ( len( selection ) - 1 )
		sortedSelection = sorted( selection, key=lambda n: n.y)
		for thisNodeIndex in range( len( selection ) ):
			sortedSelection[thisNodeIndex].y = lowestY + ( thisNodeIndex * increment )
	
	selectedLayer.setEnableUpdates()

except Exception, e:
	if selection == ():
		print "Cannot distribute nodes: nothing selected in frontmost layer."
	else:
		print "Error. Cannot distribute nodes:", selection
		print e
