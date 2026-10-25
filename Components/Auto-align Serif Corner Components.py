# MenuTitle: Auto-align Serif Corner Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Sets the alignment (left or right) of serif corner components (_corner.*) in the selected glyphs, depending on the orientation of the serif, the segment next to the corner’s node, and the horizontal scale of the corner component.
"""

from GlyphsApp import Glyphs, GSOFFCURVE

TOLERANCE = 0.01  # coordinate differences below this count as zero
ALIGNLEFT = 0  # alignment values stored in hint.options of corner components
ALIGNRIGHT = 1


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


def cornerLayerAndPath(font, cornerComponentName):
	"""Returns the layer (of the selected master) and the one open path of a corner component, or (None, None)."""
	if not cornerComponentName.startswith("_corner."):
		return None, None
	glyph = font.glyphs[cornerComponentName]
	if glyph is None:
		return None, None
	layer = glyph.layers[font.selectedFontMaster.id]
	if layer is None or len(layer.paths) != 1:
		return None, None
	path = layer.paths[0]
	if path.closed or len(path.nodes) < 2:
		return None, None
	return layer, path


def orientationOfSerif(font, cornerComponentName):
	"""
	Returns -1 for a left serif (starts above the origin, ends right of the origin),
	1 for a right serif (starts right of the origin, ends above the origin),
	and 0 if the glyph is not a corner component or the orientation cannot be determined.
	The origin is the position of the anchor "origin" in the corner component, or (0, 0) if it has none.
	"""
	layer, path = cornerLayerAndPath(font, cornerComponentName)
	if path is None:
		return 0

	originAnchor = layer.anchors["origin"]
	originX, originY = (originAnchor.x, originAnchor.y) if originAnchor else (0, 0)
	startNode, endNode = path.nodes[0], path.nodes[-1]
	startAbove = startNode.y - originY > TOLERANCE
	startRight = startNode.x - originX > TOLERANCE
	endAbove = endNode.y - originY > TOLERANCE
	endRight = endNode.x - originX > TOLERANCE

	if startAbove and endRight and not (startRight and endAbove):
		return -1
	if startRight and endAbove and not (startAbove and endRight):
		return 1
	return 0


def isVerticalSerif(font, cornerComponentName):
	"""True if the corner component starts with a vertical segment, i.e., it hangs on a vertical segment of the outline."""
	layer, path = cornerLayerAndPath(font, cornerComponentName)
	if path is None:
		return False
	vector = neighborVector(path.nodes[0], 1)
	return vector is not None and isVertical(vector)


def orientationOnNode(node, vertical=False):
	"""
	Returns on which side of the node the horizontal segment is: -1 for before the node, 1 for after.
	Without a horizontal segment, the same for an adjacent vertical segment.
	With vertical=True, the vertical segment is looked for first, and the horizontal one is the fallback.
	Returns 0 if there is no orthogonal segment, if both sides are orthogonal in the same way, or for anything else.
	"""
	if node is None or node.type == GSOFFCURVE:
		return 0
	before = neighborVector(node, -1)
	after = neighborVector(node, 1)
	orthogonalChecks = (isVertical, isHorizontal) if vertical else (isHorizontal, isVertical)
	for isOrthogonal in orthogonalChecks:
		beforeMatches = before is not None and isOrthogonal(before)
		afterMatches = after is not None and isOrthogonal(after)
		if beforeMatches and afterMatches:
			return 0
		if beforeMatches:
			return -1
		if afterMatches:
			return 1
	return 0


def isRightAngle(node):
	"""True if one segment next to the node is horizontal and the other one vertical."""
	before = neighborVector(node, -1)
	after = neighborVector(node, 1)
	if before is None or after is None:
		return False
	return (isHorizontal(before) and isVertical(after)) or (isVertical(before) and isHorizontal(after))


def alignmentForHint(font, hint):
	"""Returns ALIGNLEFT or ALIGNRIGHT for a corner component hint, or None if it cannot be determined."""
	serifOrientation = orientationOfSerif(font, hint.name)
	sideOfSegment = orientationOnNode(hint.originNode, vertical=isVerticalSerif(font, hint.name))
	if not serifOrientation or not sideOfSegment:
		return None
	if isRightAngle(hint.originNode):
		return ALIGNLEFT  # the alignment makes no visible difference at a right angle, so it stays at the default
	# Calibrated on a reference font with correctly placed serifs. The corner component runs from its
	# vertical to its horizontal arm if it is a left serif (-1), and the other way around if it is a right
	# serif (1). It is aligned left if that matches the direction of the outline at the node, i.e., if the
	# horizontal segment is after the node for a left serif, and right if it runs against it.
	# The horizontal scale is not needed: mirroring does not change the order of the arms.
	if serifOrientation * sideOfSegment > 0:
		return ALIGNRIGHT
	return ALIGNLEFT


font = Glyphs.font
if font and font.selectedLayers:
	Glyphs.clearLog()
	print("Auto-align Serif Corner Components Report for %s\n" % font.familyName)
	changeCount = 0
	glyphs = []
	for selectedLayer in font.selectedLayers:
		if selectedLayer.parent not in glyphs:
			glyphs.append(selectedLayer.parent)

	for glyph in glyphs:
		print("🔠 %s" % glyph.name)
		for layer in glyph.layers:
			if not (layer.isMasterLayer or layer.isSpecialLayer):
				continue
			for hint in layer.hints:
				if not (hint.isCorner and hint.name.startswith("_corner.")):
					continue
				alignment = alignmentForHint(font, hint)
				if alignment is None:
					print("\t⚠️ %s: could not determine the alignment of %s" % (layer.name, hint.name))
				elif hint.options != alignment:
					print("\t✅ %s: %s alignment %s → %s" % (layer.name, hint.name, hint.options, alignment))
					hint.options = alignment
					changeCount += 1

	Glyphs.showNotification("Auto-align Serif Corner Components", "Changed %i corner components. Details in Macro Window." % changeCount)
else:
	print("⚠️ Open a font and select glyphs.")
