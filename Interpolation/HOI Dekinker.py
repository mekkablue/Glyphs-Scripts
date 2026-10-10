# MenuTitle: HOI Dekinker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Goes through each axis and finds kinks of green (smooth) curve nodes halfway between neighboring key layers (masters and brace layers) along that axis. For every kink larger than the threshold, it adds an HOI intermediate point in the lower layer of the span. Nodes that already have HOI attributes are skipped and assumed to be fine. Processes the selected glyphs, or the whole font if no glyph is selected. Reports in the Macro Window, selects the nodes with HOI attributes in the affected glyphs and opens a tab with them. Requires Glyphs 4.
"""

from GlyphsApp import Glyphs, GSSMOOTH, GSOFFCURVE, Message
from Foundation import NSPoint

THRESHOLD = 0.92  # in units
verbose = False  # if True, also report glyphs without changes


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


def tripletPositions(node):
	return (node.prevNode.position, node.position, node.nextNode.position)


def setIntermediatePoint(node, axisTag, point):
	existing = node.attributes["hoi"]
	hoi = {tag: dict(values) for tag, values in existing.items()} if existing else {}
	hoi.setdefault(axisTag, {})
	hoi[axisTag]["ip"] = (point.x, point.y)
	node.attributes["hoi"] = hoi


def dekinkGlyph(glyph, axes, stats):
	"""
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
					if lowerNode.type == GSOFFCURVE or lowerNode.connection != GSSMOOTH:
						continue
					if not lowerPath.closed and nodeIndex in (0, lastIndex):
						continue
					if lowerNode.attributes["hoi"]:
						stats["nodesWithHOI"] += 1
						continue
					upperNode = upperPath.nodes[nodeIndex]
					point = intermediatePoint(tripletPositions(lowerNode), tripletPositions(upperNode), kinkIndex=1, threshold=THRESHOLD)
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


if Glyphs.versionNumber < 4:
	Message(title="HOI Dekinker", message="This script requires Glyphs 4 or later.", OKButton=None)
else:
	font = Glyphs.font
	if not font:
		Message(title="HOI Dekinker", message="No font open.", OKButton=None)
	else:
		Glyphs.clearLog()
		Glyphs.showMacroWindow()
		print("Report for HOI Dekinker\n")
		print(f"Font: {font.familyName}")
		print(f"Axes: {', '.join(axis.axisTag for axis in font.axes)}")
		print(f"Threshold: {THRESHOLD}u\n")
		glyphs = []
		for layer in font.selectedLayers:
			if layer.parent not in glyphs:
				glyphs.append(layer.parent)
		wholeFont = not glyphs
		if wholeFont:
			glyphs = list(font.glyphs)
			print(f"No glyphs selected, processing all {len(glyphs)} glyphs in the font.\n")
		total, skippedSpans, changedGlyphNames = 0, 0, []
		stats = {"spans": 0, "nodesWithHOI": 0}
		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				count, skipped = dekinkGlyph(glyph, font.axes, stats)
				total += count
				skippedSpans += skipped
				if count:
					changedGlyphNames.append(glyph.name)
				elif verbose:
					print(f"\t☑️ {glyph.name}: no kinks above threshold")
		finally:
			font.enableUpdateInterface()
		print(f"\nSummary: added {total} intermediate point{'s' if total != 1 else ''} in {len(changedGlyphNames)} of {len(glyphs)} glyph{'s' if len(glyphs) != 1 else ''}.")
		if changedGlyphNames:
			print(f"Changed glyphs: {', '.join(changedGlyphNames)}")
		if skippedSpans:
			print(f"⚠️ Skipped {skippedSpans} incompatible span{'s' if skippedSpans != 1 else ''}.")
		if changedGlyphNames:
			# select only the nodes with HOI attributes in all layers of the affected glyphs:
			for glyphName in changedGlyphNames:
				for layer in font.glyphs[glyphName].layers:
					layer.clearSelection()
					for path in layer.paths:
						for node in path.nodes:
							if node.attributes["hoi"]:
								node.selected = True
			font.newTab("/" + "/".join(changedGlyphNames))
		if total:
			Glyphs.showNotification("HOI Dekinker", f"Added {total} HOI intermediate points. Details in Macro Window.")
		else:
			if wholeFont:
				scope = f"In all {len(glyphs)} glyphs in font ‘{font.familyName}’"
			else:
				scope = f"In the {len(glyphs)} selected glyph{'s' if len(glyphs) != 1 else ''} of {len(font.glyphs)} total glyphs in font ‘{font.familyName}’"
			if not stats["spans"]:
				message = f"{scope}, no pair of neighboring key layers (masters or brace layers) was found along any axis, so there was nothing to check."
			else:
				message = f"{scope}, there were no kinks larger than the threshold {THRESHOLD}u."
				if stats["nodesWithHOI"]:
					message += f"\n\n{stats['nodesWithHOI']} smooth node{'s' if stats['nodesWithHOI'] != 1 else ''} already had HOI attributes and were skipped."
				if skippedSpans:
					message += f"\n\n{skippedSpans} span{'s' if skippedSpans != 1 else ''} with incompatible layers {'were' if skippedSpans != 1 else 'was'} skipped. Details in Macro Window."
			Message(title="HOI Dekinker", message=message, OKButton=None)
