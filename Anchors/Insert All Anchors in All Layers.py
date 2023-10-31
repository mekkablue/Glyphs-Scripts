#MenuTitle: Insert All Anchors in All Layers
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Makes sure all anchors are replicated in all layers in the same relative positions. Good for fixing anchor compatibility.
"""

from Foundation import NSPoint
thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def allAnchorsOfThisGlyph(thisGlyph):
	anchorDict = {}
	for thisLayer in thisGlyph.layers:
		thisWidth = thisLayer.width
		allAnchors = [a for a in thisLayer.anchors]
		for thisAnchor in allAnchors:
			thisAnchorInfo = (thisAnchor.x / max(1, thisWidth), thisAnchor.y)
			if not thisAnchor.name in anchorDict.keys():
				anchorDict[thisAnchor.name] = [thisAnchorInfo]
			else:
				anchorDict[thisAnchor.name].append(thisAnchorInfo)
	return anchorDict

def closestNode(thisAnchor):
	"""Return pathIndex, nodeIndex"""
	layer = thisAnchor.parent()
	for pi, path in enumerate(layer.paths):
		for ni, node in enumerate(path.nodes):
			if node.position == thisAnchor.position:
				return pi, ni
	return None

def closestX(thisAnchor):
	"""Return pathIndex, nodeIndex"""
	layer = thisAnchor.parent()
	for pi, path in enumerate(layer.paths):
		for ni, node in enumerate(path.nodes):
			if node.position.x == thisAnchor.position.x:
				return pi, ni
	return None

def pathNodeIndexForAnchorNameInGlyph(anchorName, glyph):
	for thisLayer in glyph.layers:
		thisAnchor = thisLayer.anchors[anchorName]
		if thisAnchor:
			pathNodeIndex = closestNode(thisAnchor)
			if pathNodeIndex != None:
				return pathNodeIndex, None
				
			pathNodeIndex = closestX(thisAnchor)
			if pathNodeIndex != None:
				return pathNodeIndex, thisAnchor.position.y
	return None, None

def closestNodeInComponent(thisAnchor):
	"""Return componentIndex; pathIndex, nodeIndex"""
	pass

def closestSegment(thisAnchor):
	"""Return pathIndex, segmentIndex, t"""
	pass

def closestSegmentInComponent(thisAnchor):
	"""Return componentIndex; pathIndex, segmentIndex, t"""
	pass

def averagePosition(listOfPositions, thisWidth):
	if thisWidth == 0:
		thisWidth = 1
	numOfValues = len(listOfPositions)
	averageX = sum(p[0] for p in listOfPositions) / numOfValues
	averageY = sum(p[1] for p in listOfPositions) / numOfValues
	return NSPoint(averageX * thisWidth, averageY)

def process(thisGlyph):
	reportString = ""
	allAnchorDict = allAnchorsOfThisGlyph(thisGlyph)

	if allAnchorDict: # skip glyphs without anchors (like space)
		allAnchorNames = allAnchorDict.keys()
		
		pathNodeIndexDict = {}
		for anchorName in allAnchorNames:
			pathNodeIndex, prescribedY = pathNodeIndexForAnchorNameInGlyph(anchorName, thisGlyph)
			if pathNodeIndex != None:
				pathNodeIndexDict[anchorName] = (pathNodeIndex, prescribedY)
		
		for thisLayer in thisGlyph.layers:
			layerAnchorNames = [a.name for a in thisLayer.anchors]

			if len(layerAnchorNames) < len(allAnchorNames):
				anchorsAdded = []
				anchorNamesToBeAdded = [n for n in allAnchorNames if not n in layerAnchorNames]
				thisWidth = thisLayer.width

				for newAnchorName in anchorNamesToBeAdded:
					newAnchorPosition = None
					if newAnchorName in pathNodeIndexDict.keys():
						(pathIndex, nodeIndex), prescribedY = pathNodeIndexDict[newAnchorName]
						if len(thisLayer.paths) > pathIndex:
							path = thisLayer.paths[pathIndex]
							if len(path.nodes) > nodeIndex:
								node = path.nodes[nodeIndex]
								if prescribedY is None:
									newAnchorPosition = node.position
								else:
									newAnchorPosition = NSPoint(node.position.x, prescribedY)
					if newAnchorPosition == None:
						newAnchorPosition = averagePosition(allAnchorDict[newAnchorName], thisWidth)
					newAnchor = GSAnchor()
					newAnchor.name = newAnchorName
					newAnchor.position = newAnchorPosition
					thisLayer.anchors.append(newAnchor)
					anchorsAdded.append(newAnchorName)

				reportString += "  %s: %s\n" % (thisLayer.name, ", ".join(anchorsAdded))

	return reportString

try:
	thisFont.disableUpdateInterface() # suppresses UI updates in Font View
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		print(thisGlyph.name)
		# thisGlyph.beginUndo() # undo grouping causes crashes
		print(process(thisGlyph))
		# thisGlyph.endUndo() # undo grouping causes crashes
	if thisFont.currentTab and thisFont.currentTab.graphicView():
		thisFont.currentTab.graphicView().redraw()
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	print(e)
	print()
	import traceback
	print(traceback.format_exc())
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
