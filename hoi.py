"""
HOI (higher order interpolation) dekinking helpers, shared by HOI Dekinker and Kink Finder.
"""

from GlyphsApp import GSSMOOTH, GSOFFCURVE
from Foundation import NSPoint

def interpolatePoint(pointA, pointB, factor=0.5):
	return NSPoint(
		pointA.x + (pointB.x - pointA.x) * factor,
		pointA.y + (pointB.y - pointA.y) * factor,
	)


def distanceBetweenPoints(pointA, pointB):
	return ((pointB.x - pointA.x)**2 + (pointB.y - pointA.y)**2)**0.5


def normalProjection(point, lineStart, lineEnd):
	"""Returns the foot of the perpendicular from point onto the infinite line through lineStart and lineEnd."""
	dx = lineEnd.x - lineStart.x
	dy = lineEnd.y - lineStart.y
	lengthSquared = dx * dx + dy * dy
	if lengthSquared == 0:
		# degenerate line: both points coincide
		return NSPoint(lineStart.x, lineStart.y)
	t = ((point.x - lineStart.x) * dx + (point.y - lineStart.y) * dy) / lengthSquared
	return NSPoint(lineStart.x + t * dx, lineStart.y + t * dy)


def intermediatePoint(pointsA, pointsB, kinkIndex=1, threshold=1.0):
	"""
	Interpolates the three points of pointsA and pointsB at 50%, then projects the point at
	kinkIndex onto the line through the two other interpolated points.
	Returns the projected NSPoint, or None if it is closer than threshold to the interpolated point.
	"""
	if len(pointsA) != 3 or len(pointsB) != 3 or kinkIndex not in (0, 1, 2):
		return None

	middlePoints = [interpolatePoint(pointA, pointB, 0.5) for pointA, pointB in zip(pointsA, pointsB)]
	kinkPoint = middlePoints[kinkIndex]
	lineStart, lineEnd = (point for index, point in enumerate(middlePoints) if index != kinkIndex)

	projectedPoint = normalProjection(kinkPoint, lineStart, lineEnd)
	if distanceBetweenPoints(kinkPoint, projectedPoint) < threshold:
		return None
	return projectedPoint


def layerCoordinates(font, layer):
	"""Returns {axisId: value} of a master layer or brace layer, or None if the layer is not a key layer."""
	master = layer.master
	if layer.layerId == layer.associatedMasterId:
		return {axis.axisId: master.axisValueValueForId_(axis.axisId) for axis in font.axes}
	if layer.attributes and layer.attributes["coordinates"]:
		coordinates = {axis.axisId: master.axisValueValueForId_(axis.axisId) for axis in font.axes}
		for axisId, value in layer.attributes["coordinates"].items():
			coordinates[str(axisId)] = float(value)
		return coordinates
	return None


def keyLayersOf(glyph):
	font = glyph.parent
	keyLayers = []
	for layer in glyph.layers:
		coordinates = layerCoordinates(font, layer)
		if coordinates is not None:
			keyLayers.append((layer, coordinates))
	return keyLayers


def spansForAxis(keyLayers, axisId):
	"""Returns (lowerLayer, upperLayer) pairs of neighboring key layers that differ only in the given axis."""
	groups = {}
	for layer, coordinates in keyLayers:
		otherValues = tuple(sorted((key, value) for key, value in coordinates.items() if key != axisId))
		groups.setdefault(otherValues, []).append((coordinates[axisId], layer))
	spans = []
	for members in groups.values():
		members.sort(key=lambda member: member[0])
		for (lowerValue, lowerLayer), (upperValue, upperLayer) in zip(members, members[1:]):
			if upperValue > lowerValue:
				spans.append((lowerLayer, upperLayer))
	return spans


def layersAreCompatible(firstLayer, secondLayer):
	if len(firstLayer.paths) != len(secondLayer.paths):
		return False
	for firstPath, secondPath in zip(firstLayer.paths, secondLayer.paths):
		if len(firstPath.nodes) != len(secondPath.nodes) or firstPath.closed != secondPath.closed:
			return False
		for firstNode, secondNode in zip(firstPath.nodes, secondPath.nodes):
			if firstNode.type != secondNode.type:
				return False
	return True


def tripletPositions(path, nodeIndex):
	"""
	Returns the positions of the three points that should be collinear around the node at nodeIndex.
	Usually that is the previous node, the node and the next node. In the special case
	offcurve-smooth-smooth-offcurve, it is the offcurve on the far side of the neighboring smooth node,
	the node, and the offcurve on its own side, so both smooth nodes get projected onto the line through the two offcurves.
	"""
	nodes = path.nodes

	def nodeAt(offset):
		index = nodeIndex + offset
		if path.closed:
			return nodes[index % len(nodes)]
		return nodes[index] if 0 <= index < len(nodes) else None

	node, prevNode, nextNode = nodes[nodeIndex], nodeAt(-1), nodeAt(1)
	if prevNode.type != GSOFFCURVE and nextNode.type == GSOFFCURVE and prevNode.connection == GSSMOOTH:
		farHandle = nodeAt(-2)
		if farHandle is not None and farHandle.type == GSOFFCURVE:
			return (farHandle.position, node.position, nextNode.position)
	elif nextNode.type != GSOFFCURVE and prevNode.type == GSOFFCURVE and nextNode.connection == GSSMOOTH:
		farHandle = nodeAt(2)
		if farHandle is not None and farHandle.type == GSOFFCURVE:
			return (prevNode.position, node.position, farHandle.position)
	return (prevNode.position, node.position, nextNode.position)


def setIntermediatePoint(node, axisTag, point):
	existing = node.attributes["hoi"]
	hoi = {tag: dict(values) for tag, values in existing.items()} if existing else {}
	hoi.setdefault(axisTag, {})
	hoi[axisTag]["ip"] = (point.x, point.y)
	node.attributes["hoi"] = hoi


def dekinkGlyph(glyph, axes, stats, threshold=0.92, nodeFilter=None):
	"""
	Adds HOI intermediate points to kinky smooth nodes of the glyph.
	nodeFilter: optional set of (pathIndex, nodeIndex) tuples; if given, only these nodes are considered.
	Returns (number of added points, number of skipped incompatible spans).
	Also counts the spans found and the nodes skipped because they already have HOI in the stats dict.
	"""
	count = 0
	skipped = 0
	keyLayers = keyLayersOf(glyph)
	for axis in axes:
		for lowerLayer, upperLayer in spansForAxis(keyLayers, axis.axisId):
			stats["spans"] += 1
			if not layersAreCompatible(lowerLayer, upperLayer):
				print(f"\t⚠️ {glyph.name}: {lowerLayer.name} and {upperLayer.name} are incompatible, skipping {axis.axisTag} span")
				skipped += 1
				continue
			for pathIndex, lowerPath in enumerate(lowerLayer.paths):
				upperPath = upperLayer.paths[pathIndex]
				lastIndex = len(lowerPath.nodes) - 1
				for nodeIndex, lowerNode in enumerate(lowerPath.nodes):
					if nodeFilter is not None and (pathIndex, nodeIndex) not in nodeFilter:
						continue
					if lowerNode.type == GSOFFCURVE or lowerNode.connection != GSSMOOTH:
						continue
					if not lowerPath.closed and nodeIndex in (0, lastIndex):
						continue
					if lowerNode.attributes["hoi"]:
						stats["nodesWithHOI"] += 1
						continue
					upperNode = upperPath.nodes[nodeIndex]
					point = intermediatePoint(tripletPositions(lowerPath, nodeIndex), tripletPositions(upperPath, nodeIndex), kinkIndex=1, threshold=threshold)
					if point is None:
						continue
					setIntermediatePoint(lowerNode, axis.axisTag, point)
					count += 1
					kinkSize = distanceBetweenPoints(interpolatePoint(lowerNode.position, upperNode.position), point)
					print(
						f"\t✅ {glyph.name}, {axis.axisTag}, {lowerLayer.name} → {upperLayer.name}, "
						f"path {pathIndex}, node {nodeIndex}: kink {kinkSize:.2f}u, ip ({point.x:.1f}, {point.y:.1f})"
					)
	return count, skipped


def selectHOINodes(font, glyphNames):
	"""Selects only the nodes with HOI attributes in all layers of the given glyphs."""
	for glyphName in glyphNames:
		for layer in font.glyphs[glyphName].layers:
			layer.clearSelection()
			for path in layer.paths:
				for node in path.nodes:
					if node.attributes["hoi"]:
						node.selected = True
