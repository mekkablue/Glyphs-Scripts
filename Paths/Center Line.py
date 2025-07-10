#MenuTitle: Center Line
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Will create center lines between selected segments and their opposites. Hold down OPTION to put center lines in the background.
"""

from AppKit import NSPoint, NSPointInRect, NSEvent
from GlyphsApp import GSPath, GSPathSegment
from copy import copy

def endPointsOutsideShape(path, layer):
	shape = layer.bezierPath
	for i in (0, -1):
		if not shape.containsPoint_(path.nodes[i].position):
			return True
	return False

def isPathAlreadyThere(path, comparePaths):
	def pathStructure(p):
		return list([n.position for n in p.nodes])
	pathInfo = pathStructure(path)
	for comparePath in comparePaths:
		comparePathInfo = pathStructure(comparePath)
		for i in range(2):
			if pathInfo == comparePathInfo:
				return True
			pathInfo.reverse()
	return False
	
def segmentNodesFromNode(node):
	nodes = None
	if node.type == OFFCURVE:
		if node.prevNode.type == OFFCURVE:
			nodes = [
				node.prevNode.prevNode,
				node.prevNode,
				node,
				node.nextNode,
			]
		else:
			nodes = [
				node.prevNode,
				node,
				node.nextNode,
				node.nextNode.nextNode,
			]
	else:
		if node.nextNode.type == OFFCURVE:
			nodes = [
				node,
				node.nextNode,
				node.nextNode.nextNode,
				node.nextNode.nextNode.nextNode,
			]
		else:
			nodes = [
				node,
				node.nextNode,
			]
	return nodes

def segmentNodesAtPoint(layer, point):
	nodes = [] 
	for path in layer.paths:
		nearest_point, path_time = path.nearestPointOnPath_pathTime_(point, None)
		if distance(nearest_point, point) > 1.0:
			continue
		firstNodeOnSegment = path.nearestNodeWithPathTime_(int(path_time))
		if not firstNodeOnSegment:
			continue
		nodes.append(copy(firstNodeOnSegment))
		nextNode = firstNodeOnSegment.nextNode
		if nextNode is None:
			print("FIRST", firstNodeOnSegment)
			print("NEXT", firstNodeOnSegment.nextNode)
			print("PREV", firstNodeOnSegment.prevNode)
		while nextNode.type == OFFCURVE:
			nodes.append(copy(nextNode))
			nextNode = nextNode.nextNode
		nodes.append(copy(nextNode))
	return nodes

def isSegmentSelected(nodes):
	if nodes[0].selected and nodes[-1].selected:
		return True
	if len(nodes) == 4:
		_, bcp1, bcp2, _ = nodes
		if bcp1.selected or bcp2.selected:
			return True
	return False

def nodesOfSegment(segment):
	nodes = []
	firstNode = segment.objects()[0]
	nodes.append(copy(firstNode))
	if len(segment) == 4:
		nodes.append(copy(firstNode.nextNode))
		nodes.append(copy(firstNode.nextNode.nextNode))
	nodes.append(copy(segment.objects()[-1]))
	return nodes

def pathFromNodes(nodes, reverse=False):
	path = GSPath()
	path.closed = False
	for node in nodes:
		path.nodes.append(copy(node))
	path.nodes[0].type = LINE
	path.nodes[0].connection = CORNER
	path.nodes[-1].connection = CORNER
	if reverse:
		path.reverse()
	return path

def centerLine(path1, path2):
	if len(path1.nodes) != len(path2.nodes):
		return None
	centerLine = GSPath()
	centerLine.closed = False
	for i, node1 in enumerate(path1.nodes):
		node2 = path2.nodes[i]
		centerNode = copy(node1)
		centerNode.x = (node1.x + node2.x) / 2
		centerNode.y = (node1.y + node2.y) / 2
		centerLine.nodes.append(centerNode)
	return centerLine

def createCenterLinesForSelectedSegments(layer, t=0.5, inBackground=False):
	shadowLayer = GSLayer()
	
	treatedSegments = []
	# measureLength = (layer.bounds.size.width**2 + layer.bounds.size.height**2)**0.5 / 2
	measureLength = min(
		layer.bounds.size.width * 0.66,
		layer.bounds.size.height * 0.66,
		(layer.bounds.size.width**2 + layer.bounds.size.height**2)**0.5 / 2,
	)
	for j, path in enumerate(layer.paths):
		for i, node in enumerate(path.nodes):
			segmentNodes = segmentNodesFromNode(node)
			if segmentNodes in treatedSegments:
				continue
			else:
				treatedSegments.append(segmentNodes)

			if not isSegmentSelected(segmentNodes):
				continue
			
			if len(segmentNodes) == 2:
				A, B = segmentNodes
				segment = GSPathSegment.alloc().initWithLinePoint1_point2_options_(
					A.position,
					B.position,
					0,
					)
			elif len(segmentNodes) == 4:
				A, B, C, D = segmentNodes
				segment = GSPathSegment.alloc().initWithCurvePoint1_point2_point3_point4_options_(
					A.position,
					B.position,
					C.position,
					D.position,
					0,
					)
			middleOfSegment = segment.pointAtTime_(t)
			normalR = segment.normalAtTime_(t)
			normalL = NSPoint(-normalR.x, -normalR.y)
			# set off a little bit so we don't intersect with the origin segment:
			measureStart = addPoints(middleOfSegment, normalL) 
			measureEnd = addPoints(middleOfSegment, scalePoint(normalL, measureLength))
			intersections = layer.intersectionsBetweenPoints(
				measureEnd,
				measureStart,
				)
			
			if intersections and len(intersections) > 2:
				hits = sorted(
					[i.pointValue() for i in intersections],
					key=lambda intersection: distance(intersection, middleOfSegment)
					)
				firstHit = hits[1]
				oppositeNodes = segmentNodesAtPoint(layer, firstHit)
				if not oppositeNodes:
					continue
				if not oppositeNodes:
					continue
				oppositePath = pathFromNodes(oppositeNodes, reverse=True)
				selectedPath = pathFromNodes(segmentNodes, reverse=False)
				centerPath = centerLine(selectedPath, oppositePath)
				if not centerPath:
					continue
				if centerPath.nodes[0].position == centerPath.nodes[-1].position:
					continue
				if endPointsOutsideShape(centerPath, layer):
					continue
				if not isPathAlreadyThere(centerPath, shadowLayer.paths):
					shadowLayer.paths.append(centerPath)
				print()

	shadowLayer.connectAllOpenPaths()
	shadowLayer.cleanUpPaths()
	if inBackground:
		layer.background.clear()
	else:
		layer.selection = None
		
	for shadowPath in shadowLayer.paths:
		if inBackground:
			layer.background.paths.append(shadowPath)
		else:
			layer.paths.append(shadowPath)
			shadowPath.selected = True

keysPressed = NSEvent.modifierFlags()
optionKey = 524288
optionKeyPressed = keysPressed & optionKey == optionKey

for selectedLayer in Glyphs.font.selectedLayers:
	createCenterLinesForSelectedSegments(selectedLayer, inBackground=optionKeyPressed)
