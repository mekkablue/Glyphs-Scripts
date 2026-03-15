#MenuTitle: Center Line
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Will create center lines between selected segments and their opposites. Hold down OPTION+SHIFT to put center lines in the background.
"""

from AppKit import NSPoint, NSPointInRect, NSEvent
from GlyphsApp import GSPath, GSPathSegment
from copy import copy

Glyphs.clearLog()

def lineOutsideShape(path, layer, steps=6):
	"""
	Returns True if any of steps+1 sample points along path lies outside
	the filled bezier shape of layer. The first and last samples are the path
	endpoints; the intermediate ones are spaced at equal parameter intervals
	across all segments of the path.

	For each stepIndex in 0..steps:
	  t        = stepIndex * pathSegmentCount / steps
	  segIndex = int(t // 1)  — segment index (clamped at the path end)
	  segT     = t % 1        — parameter within that segment
	  point    = path.segments[segIndex].pointAtTime_(segT)
	"""
	shape = layer.bezierPath
	pathSegmentCount = len(path.segments)
	for stepIndex in range(steps + 1):
		t = stepIndex * pathSegmentCount / steps
		segIndex = int(t // 1)
		segT = t % 1
		if segIndex >= pathSegmentCount:
			segIndex = pathSegmentCount - 1
			segT = 1.0
		point = path.segments[segIndex].pointAtTime_(segT)
		if not shape.containsPoint_(point):
			return True
	return False

def isPathAlreadyThere(path, comparePaths):
	"""
	Checks whether path already exists in comparePaths, to avoid inserting duplicates.
	For single-segment paths: compares each candidate segment by bounds and then by
	isEqualToSegment_, also trying the segment reversed.
	For multi-segment paths: compares the ordered list of node positions, also trying reversed.
	Returns True if a matching path or segment is found.
	"""
	# compare segments if path is only one segment
	if len(path.segments) == 1:
		seg = path.segments[0]
		for comparePath in comparePaths:
			for compareSeg in comparePath.segments:
				if seg.bounds != compareSeg.bounds:
					continue
				if seg.isEqualToSegment_(compareSeg):
					return True
				seg.reverse()
				if seg.isEqualToSegment_(compareSeg):
					seg.reverse()
					return True
		return False
	
	# compare paths
	else:
		print("--> comparing paths")
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
	"""
	Given any node, returns the list of nodes that form the segment it belongs to:
	  - 2 nodes  [on, on]           for a line segment
	  - 4 nodes  [on, bcp, bcp, on] for a curve segment
	Off-curve nodes are resolved to their surrounding on-curve anchors so that
	every segment is represented the same way regardless of which node was passed in.
	Returns None if no segment can be determined (should not happen in a valid path).
	"""
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
	"""
	Searches all paths in layer for a segment that passes through (or very near) point.
	Uses nearestPointOnPath_pathTime_ to project point onto each path; skips if the
	nearest point is more than 1 unit away. For matching paths, walks from the nearest
	node forward through any off-curve handles to collect the complete segment node list.
	Returns a flat list of copied GSNode objects (may contain nodes from multiple paths
	if several paths pass through the same point).
	"""
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

def bestOpposingSegment(layer, original, hits):
	"""
	Given a list of candidate hit points (sorted by distance from the segment midpoint,
	with hits[0] being the first wall crossing past the ray origin), finds the node list
	of the best opposing segment across those hits. Each hit is resolved via
	segmentNodesAtPoint(); the winner is chosen through three successive filters:

	  1. Same segment type: keep only candidates with the same node count as original
	     (2 nodes = line, 4 nodes = curve). If none qualify, keep all.
	  2. Opposite direction: keep only candidates whose start is closer to the original's
	     end than to its start, and whose end is closer to the original's start. This
	     ensures the center line runs between geometrically paired endpoints. If none
	     qualify, keep all from step 1.
	  3. Closest diagonal: from the remaining candidates, return the one whose
	     bounding-box diagonal length is closest to that of the original segment.
	     This favours opposing segments of similar size over distant coincidental hits.

	Duplicate-segment artefacts from segmentNodesAtPoint (e.g. 8 nodes that are two
	identical 4-node segments) are collapsed before filtering.
	Returns the winning node list, or None if no candidates were found at any hit.
	"""
	originalType = len(original)

	candidates = []
	for hit in hits:
		nodes = segmentNodesAtPoint(layer, hit)
		if not nodes:
			continue
		# collapse duplicate-segment artefacts from segmentNodesAtPoint
		if len(nodes) == 8 and nodes[:4] == nodes[4:]:
			nodes = nodes[:4]
		elif len(nodes) == 4 and originalType == 2 and nodes[:2] == nodes[2:]:
			nodes = nodes[:2]
		candidates.append(nodes)

	if not candidates:
		return None

	# (1) same segment type (line: 2 nodes, curve: 4 nodes)
	sameType = [c for c in candidates if len(c) == originalType]
	if sameType:
		candidates = sameType

	if len(candidates) == 1:
		return candidates[0]

	# (2) opposite direction: candidate start near original end, and vice versa
	originalStart = original[0].position
	originalEnd = original[-1].position

	def isOppositeDirection(nodes):
		candStart = nodes[0].position
		candEnd = nodes[-1].position
		return (
			distance(candStart, originalEnd) < distance(candStart, originalStart)
			and distance(candEnd, originalStart) < distance(candEnd, originalEnd)
		)

	oppositeDir = [c for c in candidates if isOppositeDirection(c)]
	if oppositeDir:
		candidates = oppositeDir

	if len(candidates) == 1:
		return candidates[0]

	# (3) closest bounding-box diagonal length to original
	def bboxDiagonal(nodes):
		xs = [n.position.x for n in nodes]
		ys = [n.position.y for n in nodes]
		w = max(xs) - min(xs)
		h = max(ys) - min(ys)
		return (w**2 + h**2)**0.5

	originalDiag = bboxDiagonal(original)
	return min(candidates, key=lambda c: abs(bboxDiagonal(c) - originalDiag))


def isSegmentSelected(nodes):
	"""
	Returns True if the segment represented by nodes is considered selected.
	A segment is selected when:
	  - Both on-curve endpoints (nodes[0] and nodes[-1]) are selected, OR
	  - For a curve segment (4 nodes), either off-curve handle (bcp1 or bcp2) is selected.
	This matches Glyphs' convention where clicking a curve handle selects that segment.
	"""
	if nodes[0].selected and nodes[-1].selected:
		return True
	if len(nodes) == 4:
		_, bcp1, bcp2, _ = nodes
		if bcp1.selected or bcp2.selected:
			return True
	return False

def nodesOfSegment(segment):
	"""
	Extracts copied GSNode objects from a GSPathSegment into a plain list.
	Returns 2 nodes for a line segment or 4 nodes for a curve segment,
	following from the first node through any intermediate off-curve handles
	to the final on-curve endpoint.
	"""
	nodes = []
	firstNode = segment.objects()[0]
	nodes.append(copy(firstNode))
	if len(segment) == 4:
		nodes.append(copy(firstNode.nextNode))
		nodes.append(copy(firstNode.nextNode.nextNode))
	nodes.append(copy(segment.objects()[-1]))
	return nodes

def pathFromNodes(nodes, reverse=False):
	"""
	Builds and returns an open GSPath from a list of nodes (copies are inserted).
	The first node's type is forced to LINE and both endpoints get CORNER connections,
	ensuring a clean open contour regardless of the original node types.
	If reverse=True, the path direction is flipped after construction, so that two
	paths built from opposite segments can be paired node-for-node by centerLine().
	"""
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
	"""
	Builds and returns a new open GSPath whose nodes are the midpoints between
	corresponding nodes of path1 and path2 (must have the same node count).
	Each midpoint node copies its type and connection from the path1 node.
	Returns None if the two paths have different node counts (segments are incompatible).
	"""
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

def createCenterLinesForSelectedSegments(layer, t=0.5, inBackground=False, selectionMatters=True):
	"""
	Main function. Iterates over every segment in layer and, for each selected segment,
	finds the opposite wall of the glyph outline and inserts a center line between them.

	Algorithm per segment:
	  1. Sample the segment at parameter t (default: midpoint) to get a point and normal.
	  2. Cast a ray from the midpoint inward along the inward normal, up to measureLength.
	  3. Collect all intersections of that ray with the layer outline.
	  4. Sort intersections by distance; the second hit (hits[1]) is the closest opposite wall.
	  5. Retrieve the segment nodes at that opposite-wall hit point.
	  6. Build open paths from the selected and opposite segments, then compute their centerLine().
	  7. Discard the result if any sampled point along the center line falls outside the shape or the path is already present.

	Results are appended to layer.paths (and selected) unless inBackground=True, in which
	case they go into layer.background.paths. connectAllOpenPaths() and cleanUpPaths() are
	called on an intermediate shadow layer to merge collinear center lines before insertion.

	Parameters:
	  layer            — the GSLayer to operate on
	  t                — curve parameter (0–1) at which to sample each segment; default 0.5
	  inBackground     — if True, place center lines in the background layer instead
	  selectionMatters — if True (and a selection exists), only process selected segments;
	                     if False, process all segments (used when multiple layers are active)
	"""
	shadowLayer = GSLayer()
	treatedSegments = []
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

			if selectionMatters and not isSegmentSelected(segmentNodes):
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
				bestHit = bestOpposingSegment(layer, original=segmentNodes, hits=hits[1:])
				if not bestHit:
					continue

				oppositePath = pathFromNodes(bestHit, reverse=True)
				selectedPath = pathFromNodes(segmentNodes, reverse=False)
				centerPath = centerLine(selectedPath, oppositePath)

				if not centerPath:
					continue
				if centerPath.nodes[0].position == centerPath.nodes[-1].position:
					continue
				if lineOutsideShape(centerPath, layer):
					continue
				if not isPathAlreadyThere(centerPath, shadowLayer.paths):
					shadowLayer.paths.append(centerPath)
	
	shadowLayer.connectAllOpenPaths()
	shadowLayer.cleanUpPaths()
	if not inBackground and shadowLayer.paths:
		layer.selection = None
		
	for shadowPath in shadowLayer.paths:
		if inBackground:
			if not isPathAlreadyThere(shadowPath, layer.background.paths):
				layer.background.paths.append(shadowPath)
		else:
			if not isPathAlreadyThere(shadowPath, layer.paths):
				layer.paths.append(shadowPath)
				shadowPath.selected = True

keysPressed = NSEvent.modifierFlags()
optionKey = 524288
shiftKey = 131072
optionKeyPressed = keysPressed & optionKey == optionKey
shiftKeyPressed = keysPressed & shiftKey == shiftKey
buildInBackground = optionKeyPressed and shiftKeyPressed

if buildInBackground:
	Glyphs.defaults["showBackground"] = True

selectedLayers = Glyphs.font.selectedLayers
for selectedLayer in selectedLayers:
	selectionMatters = selectedLayer.selection != () and len(selectedLayers) == 1
	createCenterLinesForSelectedSegments(
		selectedLayer,
		inBackground=buildInBackground,
		selectionMatters=selectionMatters,
		)
