# MenuTitle: Auto-align Serif Corner Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Aligns serif corner components (left or right serifs) to the horizontal or vertical segment next to their origin node.
"""

from GlyphsApp import Glyphs, GSOFFCURVE

TOLERANCE = 0.01  # coordinate differences below this count as zero


def neighborVector(node, step):
	"""
	Vector from node to its nearest differing neighbor on its path: backwards for step=-1, forwards for step=1.
	Skips up to two coincident neighbors (e.g., retracted handles). Returns None if there is none, e.g., beyond the end of an open path.
	"""
	path = node.parent
	nodes = list(path.nodes)
	index = nodes.index(node)
	for distance in (1, 2, 3):
		neighborIndex = index + step * distance
		if path.closed:
			neighborIndex %= len(nodes)
		elif not 0 <= neighborIndex < len(nodes):
			return None
		neighbor = nodes[neighborIndex]
		vector = (neighbor.x - node.x, neighbor.y - node.y)
		if abs(vector[0]) > TOLERANCE or abs(vector[1]) > TOLERANCE:
			return vector
	return None


def isHorizontal(vector):
	return abs(vector[1]) < TOLERANCE


def isVertical(vector):
	return abs(vector[0]) < TOLERANCE


def direction(vector):
	"""Dominant direction of a vector as "left", "right", "up", "down", or None if it is diagonal or None."""
	if vector is None:
		return None
	dx, dy = vector
	if abs(dx) > abs(dy):
		return "right" if dx > 0 else "left"
	if abs(dy) > abs(dx):
		return "up" if dy > 0 else "down"
	return None


def orientationOfSerif(font, cornerComponentName):
	"""
	Returns -1 for a left serif (starts above the origin, going down, ends right of the origin, going right),
	1 for a right serif (starts left of the origin, going right, ends above the origin, going up),
	and 0 if the glyph is not a corner component or the orientation cannot be determined.
	"""
	if not cornerComponentName.startswith("_corner."):
		return 0
	glyph = font.glyphs[cornerComponentName]
	if glyph is None:
		return 0
	layer = glyph.layers[font.selectedFontMaster.id]
	if layer is None or len(layer.paths) != 1:
		return 0
	path = layer.paths[0]
	if path.closed or len(path.nodes) < 2:
		return 0

	startNode, endNode = path.nodes[0], path.nodes[-1]
	startDirection = direction(neighborVector(startNode, 1))
	endVector = neighborVector(endNode, -1)  # points back along the path, so flip it
	endDirection = direction((-endVector[0], -endVector[1])) if endVector else None

	if startDirection == "down" and endDirection == "right" and startNode.y > 0 and endNode.x > 0:
		return -1
	if startDirection == "right" and endDirection == "up" and startNode.x < 0 and endNode.y > 0:
		return 1
	return 0


def orientationOnNode(node):
	"""
	Returns on which side of the node the horizontal segment is: -1 for before the node, 1 for after.
	Without a horizontal segment, the same for an adjacent vertical segment.
	Returns 0 if there is no orthogonal segment, if both sides are orthogonal in the same way, or for anything else.
	"""
	if node is None or node.type == GSOFFCURVE:
		return 0
	before = neighborVector(node, -1)
	after = neighborVector(node, 1)
	for isOrthogonal in (isHorizontal, isVertical):
		beforeMatches = before is not None and isOrthogonal(before)
		afterMatches = after is not None and isOrthogonal(after)
		if beforeMatches and afterMatches:
			return 0
		if beforeMatches:
			return -1
		if afterMatches:
			return 1
	return 0
