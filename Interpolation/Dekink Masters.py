#MenuTitle: Dekink Master Layers
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Synchronize node distance proportions for angled smooth connections through all masters (and other compatible layers), thus avoiding interpolation kinks. Select one or more nodes in triplets and run the script. The selected nodes will be moved in all other masters.
"""

from Foundation import NSPoint, NSArray, NSSize

def vectorFromNodes(n1, n2):
	return NSSize(n2.x - n1.x, n2.y - n1.y)

def vectorLength(vector):
	return (vector.width**2 + vector.height**2)**0.5

def dekink(originLayer, compatibleLayerIDs, pathIndex, nodeIndex, ratio, refi1=None, refi2=None):
	try:
		if refi1 != None and refi2 != None:
			thisGlyph = originLayer.parent
			for thisID in compatibleLayerIDs:
				thisLayer = thisGlyph.layers[thisID]
				thisPath = thisLayer.paths[pathIndex]
				refNodeA = thisPath.nodes[refi1]
				refNodeB = thisPath.nodes[refi2]
				refVector = vectorFromNodes(refNodeA, refNodeB)
				newPosition = NSPoint(refNodeA.x + refVector.width * ratio, refNodeA.y + refVector.height * ratio)
				thisPath.nodes[nodeIndex].position = newPosition
			return True
		else:
			return False
	except Exception as e:
		print("Error for path index %s, node index %i:\n%s" % (pi, ni, e))
		import traceback
		print(traceback.format_exc())
		return False

# determine current layer:
currentFont = Glyphs.font
currentLayer = currentFont.selectedLayers[0]
currentGlyph = currentLayer.parent

# find compatible layers in the same glyph:
layerIDs = []
instances = [i for i in currentFont.instances if i.type==0]
for subrunArray in currentGlyph.layerGroups_masters_error_(NSArray(instances), NSArray(currentFont.masters), None):
	if subrunArray:
		subrun = tuple(subrunArray[0])
		if currentLayer.layerId in subrun:
			for ID in subrun:
				if ID != currentLayer.layerId:
					layerIDs.append(ID)

# if there are any compatible layers...
if not layerIDs:
	Message(title="Dekink Error", message="Could not find any other layers in this glyph for this interpolation.", OKButton=None)
else:
	if not currentGlyph.mastersCompatible:
		Message(title="Dekink Error", message="Could not find compatible masters.", OKButton=None)
	else:
		errorCount = 0

		# ...find the indices for selected nodes:
		s = [n for n in currentLayer.selection if type(n) == GSNode]
		for n in s:
			pi = currentLayer.indexOfPath_(n.parent)
			ni = n.index

			# find the position in the triplet and the ratio between the 3 points:

			if n.connection != GSSMOOTH and n.prevNode.connection == GSSMOOTH:
				# third in the triplet:
				n0 = n.prevNode.prevNode
				n1 = n.prevNode
				n2 = n # move this node
				vector1 = vectorFromNodes(n0, n1)
				vector2 = vectorFromNodes(n0, n2)
				ratio = vectorLength(vector2) / vectorLength(vector1)
				if not dekink(currentLayer, layerIDs, pi, ni, ratio, refi1=n0.index, refi2=n1.index):
					errorCount += 1

			elif n.connection != GSSMOOTH and n.nextNode.connection == GSSMOOTH:
				# first in the triplet:
				n0 = n # move this node
				n1 = n.nextNode
				n2 = n.nextNode.nextNode
				vector1 = vectorFromNodes(n2, n1)
				vector2 = vectorFromNodes(n2, n0)
				ratio = vectorLength(vector2) / vectorLength(vector1)
				if not dekink(currentLayer, layerIDs, pi, ni, ratio, refi1=n2.index, refi2=n1.index):
					errorCount += 1

			elif n.connection == GSSMOOTH:
				# middle of the triplet:
				n0 = n.prevNode
				n1 = n # move this node
				n2 = n.nextNode
				vector1 = vectorFromNodes(n0, n2)
				vector2 = vectorFromNodes(n0, n1)
				ratio = vectorLength(vector2) / vectorLength(vector1)
				if not dekink(currentLayer, layerIDs, pi, ni, ratio, refi1=n0.index, refi2=n2.index):
					errorCount += 1

		if errorCount:
			Message(title="Could Not Dekink All", message="Could not dekink %i selected points. See the Macro Window for details." % errorCount, OKButton=None)
