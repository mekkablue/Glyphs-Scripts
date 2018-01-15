#MenuTitle: Distribute Nodes
# -*- coding: utf-8 -*-
__doc__="""
Distributes the selected nodes horizontally or vertically, depending on the bounding box.
"""



Font = Glyphs.font
Doc = Glyphs.currentDocument
selectedLayer = Font.selectedLayers[0]

try:
	try:
		# until v2.1:
		selection = selectedLayer.selection()
	except:
		# since v2.2:
		selection = selectedLayer.selection
	
	selectionXList = [ n.x for n in selection ]
	selectionYList = [ n.y for n in selection ]
	leftMostX, rightMostX = min( selectionXList ), max( selectionXList )
	lowestY, highestY = min( selectionYList ), max( selectionYList )
	diffX = abs(leftMostX-rightMostX)
	diffY = abs(lowestY-highestY)
	
	Font.disableUpdateInterface()

	if diffX > diffY:
		increment = diffX / float( len(selection) - 1 )
		sortedSelection = sorted( selection, key=lambda n: n.x)
		for thisNodeIndex in range( len(selection) - 1 ):
			sortedSelection[thisNodeIndex].x = leftMostX + ( thisNodeIndex * increment )
	else:
		increment = diffY / float( len(selection) - 1 )
		sortedSelection = sorted( selection, key=lambda n: n.y)
		for thisNodeIndex in range( len(selection) - 1 ):
			sortedSelection[thisNodeIndex].y = lowestY + ( thisNodeIndex * increment )
			
	Font.enableUpdateInterface()
	
except Exception, e:
	if selection == ():
		print "Cannot distribute nodes: nothing selected in frontmost layer."
	else:
		print "Error. Cannot distribute nodes:", selection
		print e
