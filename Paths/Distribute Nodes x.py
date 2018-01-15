#MenuTitle: Distribute Nodes horizontally
# -*- coding: utf-8 -*-
__doc__="""
Distributes the selected nodes horizontally.
"""



Font = Glyphs.font
selectedLayer = Font.selectedLayers[0]

try:
	try:
		# until v2.1:
		selection = selectedLayer.selection()
	except:
		# since v2.2:
		selection = selectedLayer.selection
	
	selectionXList = [ n.x for n in selection ]
	leftMostX, rightMostX = min( selectionXList ), max( selectionXList )
	diffX = abs(leftMostX-rightMostX)
	
	Font.disableUpdateInterface()

	increment = diffX / float( len(selection) - 1 )
	sortedSelection = sorted( selection, key=lambda n: n.x)
	for thisNodeIndex in range( len(selection) - 1 ):
		sortedSelection[thisNodeIndex].x = leftMostX + ( thisNodeIndex * increment )
			
	Font.enableUpdateInterface()
	
except Exception, e:
	if selection == ():
		print "Cannot distribute nodes: nothing selected in frontmost layer."
	else:
		print "Error. Cannot distribute nodes:", selection
		print e
