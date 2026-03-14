# MenuTitle: Positional Harmonize
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Establishes G2 continuity between the current layer and a reference glyph
(default: behDotless-ar.medi) at their connection (clicking) points,
by adjusting the one handle of the current glyph that faces the connection.
On-curve nodes are never moved.

The "other" handle used for the G2 ratio comes from the reference glyph,
shifted into the same coordinate space. Connection nodes need not be smooth.

G2 algorithm: Simon Cozens / mekkablue GreyHarmony.
Clicking points: mekkablue Position Clicker algorithm (LSB ↔ RSB offset matching).
"""

import math
from AppKit import NSPoint
from GlyphsApp import Glyphs, OFFCURVE

# ─────────────────────────── geometry helpers ─────────────────────────────────


def ptDist(p, q):
	return math.hypot(q.x - p.x, q.y - p.y)


def lineIntersection(a1, a2, b1, b2):
	"""Intersection of line a1→a2 with line b1→b2, or None if parallel."""
	dx1, dy1 = a2.x - a1.x, a2.y - a1.y
	dx2, dy2 = b2.x - b1.x, b2.y - b1.y
	denom = dx1 * dy2 - dy1 * dx2
	if abs(denom) < 1e-10:
		return None
	t = ((b1.x - a1.x) * dy2 - (b1.y - a1.y) * dx2) / denom
	return NSPoint(a1.x + t * dx1, a1.y + t * dy1)


class _Shifted:
	"""Read-only position proxy: returns a node's position shifted by dx in x."""
	def __init__(self, node, dx):
		self.position = NSPoint(node.position.x + dx, node.position.y)


# ──────────────────────────── clicking points ─────────────────────────────────


def clickingNodePositions(layer, refLayer):
	"""
	Returns (x, y) int tuples of on-curve nodes in `layer` that are at the
	clicking (connection) point with `refLayer`.

	Arabic positional geometry:
	  - Finals and medials connect at their RSB (x ≈ layer.width).
	  - Initials and medials connect at their LSB (x = 0).
	  - A connection is always LSB (one glyph) ↔ RSB (the other).

	Mirrors Position Clicker: shifts one layer's nodes by the other's width
	to simulate glyph placement, then finds coordinate matches.
	  comesLater (fina/medi): layer is left, refLayer is right →
	    shift refLayer nodes by layer.width; matches land at layer's RSB.
	  comesFirst (init/medi): layer is right, refLayer is left →
	    shift layer nodes by refLayer.width; matches land at layer's LSB.
	"""
	nameParts = layer.parent.name.split(".")
	comesFirst = "medi" in nameParts or "init" in nameParts  # LSB side connects
	comesLater = "medi" in nameParts or "fina" in nameParts  # RSB side connects

	layerWidth = int(round(layer.width))
	refWidth = int(round(refLayer.width))

	layerOnCurves = frozenset(
		(int(round(n.position.x)), int(round(n.position.y)))
		for path in layer.paths for n in path.nodes if n.type != OFFCURVE
	)
	refOnCurves = frozenset(
		(int(round(n.position.x)), int(round(n.position.y)))
		for path in refLayer.paths for n in path.nodes if n.type != OFFCURVE
	)

	result = set()

	if comesLater:
		# layer is left (RSB connects); refLayer is right (LSB connects).
		# Shift refLayer by layerWidth and look for matches in layer.
		for rx, ry in refOnCurves:
			candidate = (rx + layerWidth, ry)
			if candidate in layerOnCurves:
				result.add(candidate)

	if comesFirst:
		# layer is right (LSB connects); refLayer is left (RSB connects).
		# Shift layer by refWidth and look for matches in refLayer.
		for lx, ly in layerOnCurves:
			if (lx + refWidth, ly) in refOnCurves:
				result.add((lx, ly))  # return in layer's original coords

	return list(result)


def findNodeAtPos(layer, x, y):
	"""Return the first on-curve node in layer at int-rounded position (x, y)."""
	for path in layer.paths:
		for node in path.nodes:
			if node.type != OFFCURVE:
				if int(round(node.position.x)) == x and int(round(node.position.y)) == y:
					return node
	return None


def nodesAtPos(path, x, y):
	for i, node in enumerate(path.nodes):
		if int(round(node.position.x)) == x and int(round(node.position.y)) == y:
			yield i, node


# ─────────────────────── G2 harmonization (handle-only) ───────────────────────


def g2AdjustHandles(handleIn, smoothNode, handleOut, outerIn, outerOut, fixSide):
	"""
	Adjusts handles to achieve G2 continuity at smoothNode (Simon Cozens algorithm).

	Node layout:  … outerIn – handleIn – smoothNode – handleOut – outerOut …
	              (off-curve)  (off-curve)  (on-curve)  (off-curve)  (off-curve)

	Any of the five arguments may be a _Shifted proxy (for cross-glyph use).
	Only the node indicated by fixSide is written to; the rest are read-only.

	Algorithm:
	  d    = intersection of line(outerIn → handleIn) and line(outerOut → handleOut)
	  r0   = dist(outerIn, handleIn) / dist(handleIn, d)
	  r1   = dist(d, handleOut)      / dist(handleOut, outerOut)
	  p    = sqrt(r0 * r1)
	  t    = p / (p + 1)
	  ideal = lerp(handleIn, handleOut, t)   ← G2-ideal position for smoothNode
	  delta = ideal − smoothNode              ← applied to the chosen handle

	fixSide : 'in' | 'out'
	"""
	B = outerIn.position
	C = handleIn.position
	D = smoothNode.position  # never moved
	E = handleOut.position
	F = outerOut.position

	d = lineIntersection(B, C, F, E)
	if d is None:
		return

	dBC = ptDist(B, C)
	dCd = ptDist(C, d)
	ddE = ptDist(d, E)
	dEF = ptDist(E, F)

	if dCd < 1e-6 or dEF < 1e-6:
		return

	r0 = dBC / dCd
	r1 = ddE / dEF
	if r0 <= 0 or r1 <= 0:
		return

	p = math.sqrt(r0 * r1)
	t = p / (p + 1.0)

	dx = C.x + t * (E.x - C.x) - D.x
	dy = C.y + t * (E.y - C.y) - D.y

	if fixSide == 'in':
		handleIn.position = NSPoint(C.x + dx, C.y + dy)
	elif fixSide == 'out':
		handleOut.position = NSPoint(E.x + dx, E.y + dy)


def _inwardHandle(node, wantSmallerX):
	"""
	Return the off-curve handle adjacent to node that points inward (toward glyph interior).

	For an RSB clicking node (wantSmallerX=True) the inward handle is the one with smaller x.
	For an LSB clicking node (wantSmallerX=False) the inward handle is the one with larger x.
	When both adjacent nodes are off-curve, the two handles are compared against each other
	(not against the clicking node) to pick the one further toward the interior.
	If only one adjacent node is off-curve, that one is returned regardless of x.
	"""
	prevN = node.prevNode
	nextN = node.nextNode
	prevIsHandle = prevN.type == OFFCURVE
	nextIsHandle = nextN.type == OFFCURVE

	if prevIsHandle and not nextIsHandle:
		return prevN
	if nextIsHandle and not prevIsHandle:
		return nextN
	if prevIsHandle and nextIsHandle:
		# Both sides curved: pick whichever handle is further toward the glyph interior.
		# Compare the two handles against each other, not against the clicking node.
		# For RSB connection (wantSmallerX=True): inward handle has smaller x.
		# For LSB connection (wantSmallerX=False): inward handle has larger x.
		if wantSmallerX:
			return prevN if prevN.position.x <= nextN.position.x else nextN
		else:
			return prevN if prevN.position.x >= nextN.position.x else nextN
	return None  # no adjacent off-curve


def _outerNode(clickingNode, handle):
	"""The node one step further beyond handle, away from clickingNode."""
	if handle is clickingNode.prevNode:
		return handle.prevNode
	return handle.nextNode


def harmonizeAtClickingNode(layerNode, refNode, isComesLater, shiftWidth):
	"""
	Applies G2 harmonization at a cross-glyph clicking point.

	Finds whichever adjacent node is the off-curve handle (regardless of
	prevNode/nextNode order — path direction varies between glyphs). Uses
	x-direction to disambiguate when both sides have handles.

	isComesLater=True  (fina/medi at RSB):
	  - layer's inward handle (x < clicking node) → adjusted
	  - ref's inward handle at LSB (x > ref clicking node), shifted +shiftWidth
	isComesLater=False (init/medi at LSB):
	  - layer's inward handle (x > clicking node) → adjusted
	  - ref's inward handle at RSB (x < ref clicking node), shifted −shiftWidth

	Returns True if the handle was adjusted.
	"""
	if isComesLater:
		handleIn = _inwardHandle(layerNode, wantSmallerX=True)
		if handleIn is None:
			return False
		outerIn = _outerNode(layerNode, handleIn)

		refHandle = _inwardHandle(refNode, wantSmallerX=False)
		if refHandle is None:
			return False
		refOuter = _outerNode(refNode, refHandle)

		handleOut = _Shifted(refHandle, dx=shiftWidth)
		outerOut = _Shifted(refOuter, dx=shiftWidth)

		g2AdjustHandles(handleIn, layerNode, handleOut, outerIn, outerOut, 'in')

	else:  # comesFirst: layer at LSB
		handleOut = _inwardHandle(layerNode, wantSmallerX=False)
		if handleOut is None:
			return False
		outerOut = _outerNode(layerNode, handleOut)

		refHandle = _inwardHandle(refNode, wantSmallerX=True)
		if refHandle is None:
			return False
		refOuter = _outerNode(refNode, refHandle)

		handleIn = _Shifted(refHandle, dx=-shiftWidth)
		outerIn = _Shifted(refOuter, dx=-shiftWidth)

		g2AdjustHandles(handleIn, layerNode, handleOut, outerIn, outerOut, 'out')

	return True


# ─────────────────────────── main function ────────────────────────────────────


def positionalHarmonize(layer, harmonizeWith="behDotless-ar.medi"):
	"""
	Establishes G2 harmony between layer and the same-master layer of
	harmonizeWith at their connection (clicking) points.

	For each clicking node, adjusts the single handle within the current
	glyph that faces the connection. The matching handle from the reference
	glyph provides the other side of the G2 ratio and is never modified.
	"""
	font = layer.parent.parent

	refGlyph = font.glyphs[harmonizeWith]
	if not refGlyph:
		print(f"⚠️  Glyph '{harmonizeWith}' not found in font.")
		return

	refLayer = refGlyph.layers[layer.associatedFontMaster().id]
	if not refLayer:
		print(f"⚠️  No matching master layer in '{harmonizeWith}'.")
		return

	sharedPts = clickingNodePositions(layer, refLayer)
	if not sharedPts:
		print(f"ℹ️  No clicking points between '{layer.parent.name}' and '{harmonizeWith}'.")
		return

	nameParts = layer.parent.name.split(".")
	comesFirst = "medi" in nameParts or "init" in nameParts
	comesLater = "medi" in nameParts or "fina" in nameParts

	layerWidth = int(round(layer.width))
	refWidth = int(round(refLayer.width))

	adjustedCount = 0

	for cx, cy in sharedPts:
		for path in layer.paths:
			for _, node in nodesAtPos(path, cx, cy):
				if node.type == OFFCURVE:
					continue

				if comesLater:
					# RSB connection: corresponding ref node is at (cx − layerWidth, cy)
					refNode = findNodeAtPos(refLayer, cx - layerWidth, cy)
					if refNode and harmonizeAtClickingNode(node, refNode, True, layerWidth):
						adjustedCount += 1

				if comesFirst:
					# LSB connection: corresponding ref node is at (cx + refWidth, cy)
					refNode = findNodeAtPos(refLayer, cx + refWidth, cy)
					if refNode and harmonizeAtClickingNode(node, refNode, False, refWidth):
						adjustedCount += 1

	layer.updateMetrics()
	if adjustedCount > 0:
		print(f"✅ G2-harmonized '{layer.parent.name}' ({adjustedCount} handle(s)) with '{harmonizeWith}'.")
	else:
		print(f"ℹ️  No handles adjusted for '{layer.parent.name}' — connection nodes may lack curve handles.")


# ─────────────────────────── run on selection ─────────────────────────────────

thisFont = Glyphs.font
if not thisFont:
	print("⚠️  No font open.")
else:
	Glyphs.clearLog()
	thisFont.disableUpdateInterface()
	try:
		for layer in thisFont.selectedLayers:
			thisGlyph = layer.parent
			thisGlyph.beginUndo()
			positionalHarmonize(layer)
			thisGlyph.endUndo()
	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ Error in Positional Harmonize\n")
		import traceback
		print(traceback.format_exc())
		raise e
	finally:
		thisFont.enableUpdateInterface()
