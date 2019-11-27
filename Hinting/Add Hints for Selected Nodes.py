#MenuTitle: Add Hints to Selected Nodes
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds hints for the selected nodes. Tries to guess whether it should be H or V. If exactly one node inside a zone is selected, it will add a Ghost Hint.
"""

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
thisLayer = Font.selectedLayers[0]
try:
	# until v2.1:
	selection = thisLayer.selection()
except:
	# since v2.2:
	selection = thisLayer.selection

thisSelection = [ n for n in selection if n.className() == "GSNode" ]
numberOfSelectedNodes = len( thisSelection )

def hintTypeForY( yValue ):
	for thisZone in FontMaster.alignmentZones:
		try:
			# app versions 1.4.4 and later
			zonePosition = float(thisZone.position)
			zoneSize = float(thisZone.size)
		except:
			# app versions before 1.4.4
			zonePosition = thisZone.position()
			zoneSize = thisZone.size()
		if yValue == sorted([zonePosition, zonePosition + zoneSize, yValue])[1]:
			if zoneSize > 0:
				return -1
			elif zoneSize < 0:
				return 1
	return False

if numberOfSelectedNodes == 1:
	# Ghost Hint
	thisNode = thisSelection[0]
	thisNodePosition = thisNode.y
	hintType = hintTypeForY( thisNodePosition )
	if hintType is not False:
		newHint = GSHint()
		newHint.originNode = thisNode
		newHint.type = hintType
		newHint.horizontal = True
		thisLayer.hints.append( newHint )
			
elif numberOfSelectedNodes % 2 == 0:
	# Determine horizontal/vertical hints:
	xCoordinates = sorted( [n.x for n in thisSelection] )
	yCoordinates = sorted( [n.y for n in thisSelection] )
	xDiff = xCoordinates[-1] - xCoordinates[0]
	yDiff = yCoordinates[-1] - yCoordinates[0]
	isHorizontal = yDiff > xDiff
	if isHorizontal:
		sortedListOfNodes = sorted( thisSelection, key=lambda n: n.y )
	else:
		sortedListOfNodes = sorted( thisSelection, key=lambda n: n.x )
	
	# Add Hints:
	for i in range( numberOfSelectedNodes // 2 ):
		firstIndex = ( i + 1 ) * 2 - 2
		secondIndex = ( i + 1 ) * 2 - 1
		firstNode = sortedListOfNodes[ firstIndex ]
		secondNode = sortedListOfNodes[ secondIndex ]
		
		newHint = GSHint()
		newHint.originNode = firstNode
		newHint.targetNode = secondNode
		newHint.type = 0
		newHint.horizontal = isHorizontal
		thisLayer.addHint_( newHint )
else:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("Error: Either 1 node, or an even number of nodes must be selected.")

