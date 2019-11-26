from __future__ import print_function
#MenuTitle: Align Selected Nodes with Background
# -*- coding: utf-8 -*-
__doc__="""
Align selected nodes with the nearest background node unless it is already taken by a previously moved node.
"""

def alignNodeWithNodeInOtherLayer(thisNode, otherLayer, tolerance=5, maxTolerance=80, alreadyTaken=[]):
	while tolerance < maxTolerance:
		nearestNode = otherLayer.nodeAtPoint_excludeNodes_traversComponents_tollerance_( thisNode.position, None, False, tolerance )
		if nearestNode and (thisNode.type == nearestNode.type) and (not nearestNode.position in alreadyTaken):
			thisNode.position = nearestNode.position
			return True
		# else:
		# 	print tolerance
		# 	if nearestNode:
		# 		print "Type:", thisNode.type, nearestNode.type
		# 		print "Pos:", thisNode.position, nearestNode.position
		# 	else:
		# 		print "no Node", otherLayer.paths[0].nodes
		tolerance += 5
	return False

def anchorWithNameFromAnchorList(anchorName, referenceAnchors):
	for thisAnchor in referenceAnchors:
		if thisAnchor.name == anchorName:
			return thisAnchor
	return None

def syncAnchorPositionWithBackground( theseAnchorNames, thisLayer ):
	# collect background anchors
	otherAnchorDict = {}
	for otherAnchor in thisLayer.background.anchorsTraversingComponents():
		otherAnchorDict[otherAnchor.name] = otherAnchor.position
	
	# move anchors in foreground
	if not otherAnchorDict:
		print("Anchors: could not find any anchors in components.")
		return 0
	else:
		count = 0
		for thisAnchorName in theseAnchorNames:
			otherAnchorPosition = otherAnchorDict[thisAnchorName]
			if otherAnchorPosition:
				thisAnchor = thisLayer.anchors[thisAnchorName]
				thisAnchor.position = otherAnchorPosition
				count += 1
		return count
	
def process( thisLayer ):
	backgroundBackup = thisLayer.background.copy()
	for backgroundComponent in thisLayer.background.components:
		thisLayer.background.decomposeComponent_doAnchors_doHints_(backgroundComponent,False,False)
	
	alignedNodeCount = 0
	selectedNodeCount = 0
	appliedPositions = []
	
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			if thisNode.selected:
				selectedNodeCount += 1
				if alignNodeWithNodeInOtherLayer( thisNode, thisLayer.background, alreadyTaken=appliedPositions ):
					alignedNodeCount += 1
					appliedPositions.append( thisNode.position )

	thisLayer.background = backgroundBackup

	anchorsToAlign = []
	numberOfAnchorsMoved = 0
	for thisAnchor in thisLayer.anchors:
		if thisAnchor.selected:
			anchorsToAlign.append(thisAnchor.name)
	if anchorsToAlign:
		numberOfAnchorsMoved = syncAnchorPositionWithBackground( anchorsToAlign, thisLayer )
		
	return selectedNodeCount, alignedNodeCount, numberOfAnchorsMoved

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
selection = selectedLayers[0].selection # node selection in edit mode
Glyphs.clearLog() # clears log in Macro window

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
 
for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo() # begin undo grouping
	selected, aligned, numberOfAnchorsMoved = process( thisLayer )
	print("%s: aligned %i of %i selected nodes" % (thisGlyph.name, aligned, selected))
	print("%s: aligned %i of %i anchors." % (thisGlyph.name, numberOfAnchorsMoved, len(thisLayer.anchors)))
	thisGlyph.endUndo() # end undo grouping

thisFont.enableUpdateInterface() # suppresses UI updates in Font View
 

