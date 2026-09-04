# MenuTitle: Dekink Master Layers
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Synchronize node distance proportions for angled smooth connections through all masters (and other compatible layers), thus avoiding interpolation kinks. Select one or more nodes in triplets and run the script. The selected nodes will be moved in all other masters.
"""

from mekkablue import layerGroupsOf
from GlyphsApp import Glyphs, GSNode, GSSMOOTH, Message
from Foundation import NSPoint, NSSize


def vectorFromNodes(firstNode, secondNode):
	return NSSize(secondNode.x - firstNode.x, secondNode.y - firstNode.y)


def vectorLength(vector):
	return (vector.width**2 + vector.height**2)**0.5


def ratioOfVectors(vector, referenceVector):
	"""Length of vector, measured in lengths of referenceVector. None if referenceVector has zero length."""
	referenceLength = vectorLength(referenceVector)
	if not referenceLength:
		return None
	return vectorLength(vector) / referenceLength


def layersAreCompatible(firstLayer, secondLayer):
	"""
	True if both layers have the same path and node structure,
	i.e. if path and node indexes point at the same nodes in both layers.
	"""
	firstPaths, secondPaths = firstLayer.paths, secondLayer.paths
	if len(firstPaths) != len(secondPaths):
		return False
	for firstPath, secondPath in zip(firstPaths, secondPaths):
		firstNodes, secondNodes = firstPath.nodes, secondPath.nodes
		if len(firstNodes) != len(secondNodes):
			return False
		for firstNode, secondNode in zip(firstNodes, secondNodes):
			if firstNode.type != secondNode.type:
				return False
	return True


def compatibleLayers(referenceLayer):
	"""
	All other layers of the same glyph that interpolate with referenceLayer:
	its compatibility run, minus layers whose path and node structure differs.
	"""
	glyph = referenceLayer.parent
	for layerGroup in layerGroupsOf(glyph):
		if referenceLayer.layerId not in layerGroup:
			continue
		otherLayers = (glyph.layers[layerID] for layerID in layerGroup if layerID != referenceLayer.layerId)
		return tuple(layer for layer in otherLayers if layer and layersAreCompatible(referenceLayer, layer))
	return ()


def indexInList(items, item):
	"""Index of item in items, by identity first, by equality only if identity fails."""
	for i, thisItem in enumerate(items):
		if thisItem is item:
			return i
	for i, thisItem in enumerate(items):
		if thisItem == item:
			return i
	return None


def indexOfPath(layer, path):
	return indexInList(tuple(layer.paths), path)


def indexOfNode(path, node):
	return indexInList(tuple(path.nodes), node)


def dekink(targetLayers, pathIndex, nodeIndex, ratio, referenceIndex1, referenceIndex2):
	if pathIndex is None or nodeIndex is None or referenceIndex1 is None or referenceIndex2 is None:
		print("\t❌ Could not determine path or node indexes for a selected node.")
		return False
	try:
		for thisLayer in targetLayers:
			thisPath = thisLayer.paths[pathIndex]
			referenceNodeA = thisPath.nodes[referenceIndex1]
			referenceNodeB = thisPath.nodes[referenceIndex2]
			referenceVector = vectorFromNodes(referenceNodeA, referenceNodeB)
			newPosition = NSPoint(
				referenceNodeA.x + referenceVector.width * ratio,
				referenceNodeA.y + referenceVector.height * ratio,
			)
			thisPath.nodes[nodeIndex].position = newPosition
		return True
	except Exception as e:
		print("\t❌ Error for path index %s, node index %s:\n%s" % (pathIndex, nodeIndex, e))
		import traceback
		print(traceback.format_exc())
		return False


# determine current layer:
font = Glyphs.font
currentLayer = font.selectedLayers[0] if font and font.selectedLayers else None

if not currentLayer:
	Message(title="Dekink Error", message="Please open a font, select nodes of a smooth connection, and run the script again.", OKButton=None)
else:
	print("Dekink Master Layers for %s:" % currentLayer.parent.name)

	# find the nodes the user selected:
	selectedNodes = tuple(n for n in currentLayer.selection if isinstance(n, GSNode))

	# find compatible layers in the same glyph:
	targetLayers = compatibleLayers(currentLayer)

	if not selectedNodes:
		Message(title="Dekink Error", message="Please select one or more nodes of a smooth connection, and run the script again.", OKButton=None)
	elif not targetLayers:
		Message(title="Dekink Error", message="Could not find any other compatible layer in this glyph.", OKButton=None)
	else:
		errorCount = 0
		dekinkCount = 0

		for thisNode in selectedNodes:
			thisPath = thisNode.parent
			pathIndex = indexOfPath(currentLayer, thisPath)
			nodeIndex = indexOfNode(thisPath, thisNode)

			# find the position in the triplet and the ratio between the 3 points:

			if thisNode.connection != GSSMOOTH and thisNode.prevNode.connection == GSSMOOTH:
				# third in the triplet:
				node0 = thisNode.prevNode.prevNode
				node1 = thisNode.prevNode
				node2 = thisNode  # move this node
				vector1 = vectorFromNodes(node0, node1)
				vector2 = vectorFromNodes(node0, node2)
				ratio = ratioOfVectors(vector2, vector1)
				referenceIndex1 = indexOfNode(thisPath, node0)
				referenceIndex2 = indexOfNode(thisPath, node1)

			elif thisNode.connection != GSSMOOTH and thisNode.nextNode.connection == GSSMOOTH:
				# first in the triplet:
				node0 = thisNode  # move this node
				node1 = thisNode.nextNode
				node2 = thisNode.nextNode.nextNode
				vector1 = vectorFromNodes(node2, node1)
				vector2 = vectorFromNodes(node2, node0)
				ratio = ratioOfVectors(vector2, vector1)
				referenceIndex1 = indexOfNode(thisPath, node2)
				referenceIndex2 = indexOfNode(thisPath, node1)

			elif thisNode.connection == GSSMOOTH:
				# middle of the triplet:
				node0 = thisNode.prevNode
				node1 = thisNode  # move this node
				node2 = thisNode.nextNode
				vector1 = vectorFromNodes(node0, node2)
				vector2 = vectorFromNodes(node0, node1)
				ratio = ratioOfVectors(vector2, vector1)
				referenceIndex1 = indexOfNode(thisPath, node0)
				referenceIndex2 = indexOfNode(thisPath, node2)

			else:
				# not part of a smooth connection:
				print("\t⚠️ Node at %s is not part of a smooth connection, skipping." % (thisNode.position, ))
				errorCount += 1
				continue

			if ratio is None:
				print("\t⚠️ Node at %s: cannot measure the triplet, two of its nodes are in the same spot. Skipping." % (thisNode.position, ))
				errorCount += 1
				continue

			if dekink(targetLayers, pathIndex, nodeIndex, ratio, referenceIndex1, referenceIndex2):
				dekinkCount += 1
			else:
				errorCount += 1

		if errorCount:
			Message(
				title="Could Not Dekink All",
				message="Could not dekink %i of %i selected points. See the Macro Window for details." % (errorCount, len(selectedNodes)),
				OKButton=None,
			)
		else:
			Glyphs.showNotification("Dekink Master Layers", "Dekinked %i node%s in %i layer%s." % (dekinkCount, "" if dekinkCount == 1 else "s", len(targetLayers), "" if len(targetLayers) == 1 else "s"))
