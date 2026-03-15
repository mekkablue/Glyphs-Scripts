#MenuTitle: Center Line
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Will create center lines between selected segments and their opposites. Hold down OPTION+SHIFT to put center lines in the background.
"""

from AppKit import NSPoint, NSPointInRect, NSEvent
from GlyphsApp import GSPath, GSPathSegment, GSBackgroundLayer
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

def intersectionsForMeasureRay(segment, layer, t, measureLength):
	"""
	Fires a measuring ray perpendicular to segment at parameter t and returns the
	raw list of intersection NSValue objects with the layer outline.

	The ray points inward (left-hand normal of the segment direction). measureStart
	is offset one unit from the midpoint so the ray does not self-intersect with the
	origin segment. measureEnd extends measureLength units in that direction.
	The list is passed to layer.intersectionsBetweenPoints() and returned as-is;
	the caller is responsible for sorting and interpreting the results.
	"""
	middleOfSegment = segment.pointAtTime_(t)
	normalR = segment.normalAtTime_(t)
	normalL = NSPoint(-normalR.x, -normalR.y)
	# set off a little bit so we don't intersect with the origin segment:
	measureStart = addPoints(middleOfSegment, normalL)
	measureEnd = addPoints(middleOfSegment, scalePoint(normalL, measureLength))
	return layer.intersectionsBetweenPoints(measureEnd, measureStart)


def bestOpposingSegment(layer, original, hits, t, measureLength, rayOrigin=None):
	"""
	Given a list of candidate hit points (sorted by distance from the segment midpoint,
	with hits[0] being the first wall crossing past the ray origin), finds the node list
	of the best opposing segment across those hits. Each hit is resolved via
	segmentNodesAtPoint(); the winner is chosen through three successive filters:

	  0.5. Line-of-sight: for each hit, sample 5 evenly-spaced stops between rayOrigin
	     and the hit. If any stop falls outside the layer's filled bezier shape, that
	     hit is discarded before candidate collection. Skipped when rayOrigin is None.
	  1. Same segment type: keep only candidates with the same node count as original
	     (2 nodes = line, 4 nodes = curve). If none qualify, keep all.
	  2. Opposite direction: keep only candidates whose start is closer to the original's
	     end than to its start, and whose end is closer to the original's start. This
	     ensures the center line runs between geometrically paired endpoints. If none
	     qualify, keep all from step 1.
	  2.5. Reciprocal ray: fire up to three measuring rays from each remaining candidate
	     (at t, max(0.1, t-0.16), and min(0.9, t+0.16)) and keep only those where at
	     least one ray crosses back through the original segment. This confirms the two
	     segments genuinely face each other. If none qualify, returns None immediately —
	     the segment is skipped entirely at the call site.
	  3. Closest diagonal: from the remaining candidates, return the one whose
	     bounding-box diagonal length is closest to that of the original segment.
	     This favours opposing segments of similar size over distant coincidental hits.

	Duplicate-segment artefacts from segmentNodesAtPoint (e.g. 8 nodes that are two
	identical 4-node segments) are collapsed before filtering.
	Returns the winning node list, or None if no candidates were found at any hit.
	"""
	originalType = len(original)

	# (0.5) line-of-sight: discard hits where any stop between rayOrigin and hit
	# falls outside the layer's filled shape
	if rayOrigin is not None:
		bezier = layer.bezierPath
		def hasLineOfSight(hit):
			for k in range(1, 6):
				t_stop = k / 6.0
				stop = NSPoint(
					rayOrigin.x + (hit.x - rayOrigin.x) * t_stop,
					rayOrigin.y + (hit.y - rayOrigin.y) * t_stop,
				)
				if not bezier.containsPoint_(stop):
					return False
			return True
		hits = [h for h in hits if hasLineOfSight(h)]

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

	# (2.5) reciprocal ray: opposing segment's own ray must cross back through original
	def segmentFromNodes(nodes):
		if len(nodes) == 2:
			A, B = nodes
			return GSPathSegment.alloc().initWithLinePoint1_point2_options_(A.position, B.position, 0)
		A, B, C, D = nodes
		return GSPathSegment.alloc().initWithCurvePoint1_point2_point3_point4_options_(
			A.position, B.position, C.position, D.position, 0)

	def rayHitsOriginal(seg, tRay):
		candIntersections = intersectionsForMeasureRay(seg, layer, tRay, measureLength)
		if not candIntersections:
			return False
		candMid = seg.pointAtTime_(tRay)
		candHits = sorted([p.pointValue() for p in candIntersections], key=lambda p: distance(p, candMid))
		for hit in candHits[1:]:
			hitNodes = segmentNodesAtPoint(layer, hit)
			if not hitNodes:
				continue
			if (
				hitNodes[0].position == original[0].position and hitNodes[-1].position == original[-1].position
				or hitNodes[0].position == original[-1].position and hitNodes[-1].position == original[0].position
			):
				return True
		return False

	def hitsOriginal(candidateNodes):
		seg = segmentFromNodes(candidateNodes)
		return any(
			rayHitsOriginal(seg, tRay)
			for tRay in (t, max(0.1, t - 0.16), min(0.9, t + 0.16))
		)

	candidates = [c for c in candidates if hitsOriginal(c)]
	if not candidates:
		return None

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

def relevantSegmentStarts(path, layer):
	"""
	Returns the subset of on-curve start nodes whose segments are worth measuring
	a center line for, based on the structure of the path. The node references
	returned are the live objects from path.nodes, so identity comparison (`in`)
	works directly in the caller loop.

	Rules (applied in order, first match wins):

	  4-segment CCW path — assumed to be a closed stroke shape (two long sides +
	    two short butt ends). Returns the start nodes of the two longer segments
	    only, measured by bounding-box diagonal. This prevents the script from
	    drawing center lines across the stroke butts. CW paths are excluded
	    (GSPath.direction == 1) and always return all segment start nodes.
	    Exception: if any other path in layer lies entirely within path's bounding
	    box (checked via NSRect bounds), the 4-segment rule is skipped and all
	    segment start nodes are returned instead. This handles enclosed shapes
	    that would otherwise be mistaken for plain strokes.

	  All other paths — all segment start nodes are returned so that subsequent
	    filters can decide. (A half-range structural check for even-segment paths
	    is stubbed out below and may be re-enabled later.)
	"""
	segments = path.segments
	segmentCount = len(segments)

	def segDiagonal(seg):
		b = seg.bounds
		return (b.size.width**2 + b.size.height**2)**0.5

	def segType(seg):
		return len(seg)  # 2 = line segment, 4 = curve segment

	pathIsCCW = path.direction == -1

	if segmentCount == 4 and pathIsCCW:
		hasInnerPath = any(
			otherPath is not path
			and NSPointInRect(otherPath.bounds.origin, pathBounds)
			and NSPointInRect(
				NSPoint(
					otherPath.bounds.origin.x + otherPath.bounds.size.width,
					otherPath.bounds.origin.y + otherPath.bounds.size.height,
				),
				pathBounds,
			)
			for otherPath in layer.paths
		)
		if not hasInnerPath:
			diagonals = sorted(range(4), key=lambda i: segDiagonal(segments[i]), reverse=True)
			longerIndices = set(diagonals[:2])
			return [segments[i].objects()[0] for i in range(4) if i in longerIndices]

	# if segmentCount % 2 == 0:
	# 	half = segmentCount // 2
	# 	return [
	# 		segments[i].objects()[0]
	# 		for i in range(half)
	# 		if segType(segments[i]) == segType(segments[i + half])
	# 	]

	return [seg.objects()[0] for seg in segments]


def cleanup(layer, threshold=40):
	"""
	Removes false positives and applies fixes to paths in layer.

	For both rules, line1 is always a standalone single-line path (2 nodes). line2
	is drawn from a shared candidate list that includes both standalone single-line
	paths and line segments extracted from multi-segment paths in the layer.

	Rule 1 — merge overlapping single-line paths:
	  Find pairs where both conditions hold:
	    (a) The midpoint of line1 lies on line2 (nearest point within 1 unit).
	    (b) Their paired endpoints are each less than threshold apart.
	  If line2 is standalone, both are removed and replaced by their centerLine().
	  If line2 is a segment of a multi-segment path, only line1 is deleted (it is
	  already represented by the existing longer path).
	  line2 is tried reversed if the forward endpoint pairing does not satisfy (b).

	Rule 2 — delete redundant single-line paths:
	  For each (line1, line2) pair, delete line1 if:
	    (a) Both endpoints of line1 lie on line2 (line1 is a subset), or
	    (b) One endpoint lies on line2 and the other is less than threshold away
	        from either endpoint of line2 (line1 is a near-subset).

	Rule 3 — snap open path ends to nearby intersections:
	  Collect all interior crossing points in the layer (points where one path
	  crosses another, excluding segment endpoints). For each open path end
	  (nodes[0] of first segment, nodes[-1] of last segment), if an intersection
	  lies within threshold/2 of that end AND the containing segment is at least
	  2.5*threshold long (bounding-box diagonal), move the end to that intersection.
	  For line segments the endpoint is simply repositioned; for curve segments
	  the segment is trimmed via GSPathSegment.divideAtTime_() and the appropriate
	  half's control points are written back to the live nodes.
	"""
	singleLines = [p for p in layer.paths if len(p.nodes) == 2]

	toRemove = set()  # id()s of paths to remove
	toAdd = []        # merged replacement paths

	# line2 candidates: (gsPath, isStandalone)
	# isStandalone=True  → path exists independently and can itself be removed (rule 1 merge)
	# isStandalone=False → path is a temporary copy of a segment from a multi-segment path
	line2Candidates = [(p, True) for p in singleLines]
	for path in layer.paths:
		if len(path.segments) > 1:
			for seg in path.segments:
				if len(seg) == 2:  # line segment only
					line2Candidates.append((pathFromNodes([seg.objects()[0], seg.objects()[-1]]), False))

	for i in range(len(singleLines)):
		line1 = singleLines[i]
		if id(line1) in toRemove:
			continue
		for line2, line2standalone in line2Candidates:
			if line2standalone and (id(line2) == id(line1) or id(line2) in toRemove):
				continue

			# (a) midpoint of line1 must lie on line2
			center1 = NSPoint(
				(line1.nodes[0].position.x + line1.nodes[1].position.x) / 2,
				(line1.nodes[0].position.y + line1.nodes[1].position.y) / 2,
			)
			nearest, _ = line2.nearestPointOnPath_pathTime_(center1, None)
			if distance(nearest, center1) > 1.0:
				continue

			# (b) paired endpoints within threshold — try forward, then reversed
			p1s = line1.nodes[0].position
			p1e = line1.nodes[1].position
			p2s = line2.nodes[0].position
			p2e = line2.nodes[1].position

			if distance(p1s, p2s) < threshold and distance(p1e, p2e) < threshold:
				line2forCenter = line2
			elif distance(p1s, p2e) < threshold and distance(p1e, p2s) < threshold:
				line2forCenter = pathFromNodes(list(line2.nodes), reverse=True)
			else:
				continue

			if line2standalone:
				merged = centerLine(line1, line2forCenter)
				if merged:
					toRemove.add(id(line1))
					toRemove.add(id(line2))
					toAdd.append(merged)
			else:
				# line2 is a segment of a multi-segment path; line1 is redundant, delete it
				toRemove.add(id(line1))
			break  # line1 consumed, move on

	# Rule 2 — delete line1 if it is fully or partially redundant against line2:
	#   (a) both endpoints of line1 lie on line2 → line1 is a subset, delete it
	#   (b) one endpoint lies on line2 and the other is within threshold of an
	#       endpoint of line2 → line1 is a near-subset, delete it
	def onPath(point, path):
		nearest, _ = path.nearestPointOnPath_pathTime_(point, None)
		return distance(nearest, point) <= 1.0

	for line1 in singleLines:
		if id(line1) in toRemove:
			continue
		for line2, line2standalone in line2Candidates:
			if line2standalone and (id(line2) == id(line1) or id(line2) in toRemove):
				continue
			p0 = line1.nodes[0].position
			p1 = line1.nodes[1].position
			end0on = onPath(p0, line2)
			end1on = onPath(p1, line2)
			if end0on and end1on:
				toRemove.add(id(line1))
				break
			if end0on and any(distance(p1, line2.nodes[k].position) < threshold for k in (0, 1)):
				toRemove.add(id(line1))
				break
			if end1on and any(distance(p0, line2.nodes[k].position) < threshold for k in (0, 1)):
				toRemove.add(id(line1))
				break

	for i in range(len(layer.shapes) - 1, -1, -1):
		if id(layer.shapes[i]) in toRemove:
			del layer.shapes[i]
	for path in toAdd:
		layer.paths.append(path)

	# Rule 3 — snap open path ends to nearby intersections
	# Collect all interior crossing points among the remaining paths in the layer.
	# For each segment A–B, fire layer.intersectionsBetweenPoints(A, B) and keep only
	# hits that are strictly between the two endpoints (> 1 unit from each).
	intersectionPoints = []
	for path in layer.paths:
		for seg in path.segments:
			A = seg.objects()[0].position
			B = seg.objects()[-1].position
			for hit in layer.intersectionsBetweenPoints(A, B):
				pt = hit.pointValue()
				if distance(pt, A) > 1.0 and distance(pt, B) > 1.0:
					if not any(distance(pt, ex) < 0.5 for ex in intersectionPoints):
						intersectionPoints.append(pt)

	if intersectionPoints:
		def lerp(p1, p2, t):
			return NSPoint(p1.x + (p2.x - p1.x) * t, p1.y + (p2.y - p1.y) * t)

		for path in layer.paths:
			for isEnd in (True, False):
				segIndex = len(path.segments) - 1 if isEnd else 0
				seg = path.segments[segIndex]
				openNode = path.nodes[-1] if isEnd else path.nodes[0]

				b = seg.bounds
				segLen = (b.size.width**2 + b.size.height**2)**0.5
				if segLen < 2.5 * threshold:
					continue

				openPos = openNode.position
				bestPt = None
				bestDist = threshold / 2
				for pt in intersectionPoints:
					d = distance(pt, openPos)
					if d >= bestDist:
						continue
					# confirm pt lies on this specific segment
					nearest, pathTime = path.nearestPointOnPath_pathTime_(pt, None)
					if distance(nearest, pt) > 1.0:
						continue
					if int(pathTime) != segIndex:
						continue
					bestDist = d
					bestPt = pt

				if bestPt is None:
					continue

				if len(seg) == 2:
					# Line segment: just move the endpoint
					openNode.position = bestPt
				else:
					# Curve segment: trim to the intersection using divideAtTime_
					# (GSPathSegment.divideAtTime_ splits at parameter t and returns
					# two sub-segments; we keep the appropriate half)
					_, pathTime = path.nearestPointOnPath_pathTime_(bestPt, None)
					t = pathTime % 1
					subdiv1, subdiv2 = seg.divideAtTime_(t)
					if isEnd:
						# keep first half — update bcp1, bcp2, end from subdiv1
						seg.objects()[1].position = subdiv1.objects()[1].position
						seg.objects()[2].position = subdiv1.objects()[2].position
						seg.objects()[3].position = subdiv1.objects()[3].position
					else:
						# keep second half — update start, bcp1, bcp2 from subdiv2
						seg.objects()[0].position = subdiv2.objects()[0].position
						seg.objects()[1].position = subdiv2.objects()[1].position
						seg.objects()[2].position = subdiv2.objects()[2].position


def createCenterLinesForSelectedSegments(layer, t=0.5, inBackground=False, selectionMatters=True):
	"""
	Main function. Iterates over every segment in layer and, for each selected segment,
	finds the opposite wall of the glyph outline and inserts a center line between them.

	Algorithm per segment:
	  0. Pre-select relevant segment start nodes via relevantSegmentStarts() to skip
	     structural false positives (e.g. stroke butts, mismatched opposite segments).
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
		preselectedNodes = relevantSegmentStarts(path, layer)
		for i, node in enumerate(path.nodes):
			if node not in preselectedNodes:
				continue
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
			intersections = intersectionsForMeasureRay(segment, layer, t, measureLength)
			middleOfSegment = segment.pointAtTime_(t)

			if intersections and len(intersections) > 2:
				hits = sorted(
					[i.pointValue() for i in intersections],
					key=lambda intersection: distance(intersection, middleOfSegment)
					)
				bestHit = bestOpposingSegment(layer, original=segmentNodes, hits=hits[1:], t=t, measureLength=measureLength, rayOrigin=hits[0])
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
	cleanup(layer=shadowLayer, threshold=40)
	shadowLayer.cleanUpPaths()
	if not inBackground and shadowLayer.paths:
		layer.selection = None
	if inBackground and shadowLayer.paths:
		background = layer.background
		if isinstance(background, GSBackgroundLayer):
			background.clear()

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
