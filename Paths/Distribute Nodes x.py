#MenuTitle: Distribute Nodes horizontally
"""Distributes the selected nodes horizontally."""

import GlyphsApp

Font = Glyphs.font
selectedLayer = Font.selectedLayers[0]

try:
	selection = selectedLayer.selection()
	selectionXList = [ n.x for n in selection ]
	leftMostX, rightMostX = min( selectionXList ), max( selectionXList )
	diffX = abs(leftMostX-rightMostX)
	
	selectedLayer.setDisableUpdates()
	
	increment = diffX // ( len( selection ) - 1 )
	sortedSelection = sorted( selection, key=lambda n: n.x)
	for thisNodeIndex in range( len( selection ) ):
		sortedSelection[thisNodeIndex].x = leftMostX + ( thisNodeIndex * increment )
	
	selectedLayer.setEnableUpdates()
	
except Exception, e:
	if selection == ():
		print "Cannot distribute nodes: nothing selected in frontmost layer."
	else:
		print "Error. Cannot distribute nodes:", selection
		print e
