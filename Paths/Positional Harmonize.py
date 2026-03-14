# MenuTitle: Positional Harmonize
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Establishes G2 continuity between the current layer and a reference glyph
(default: behDotless-ar.medi) at their connection (clicking) points,
by adjusting handle positions only — on-curve nodes are never moved.

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

	Algorithm:
	  d    = intersection of line(outerIn → handleIn) and line(outerOut → handleOut)
	  r0   = dist(outerIn, handleIn) / dist(handleIn, d)
	  r1   = dist(d, handleOut)      / dist(handleOut, outerOut)
	  p    = sqrt(r0 * r1)
	  t    = p / (p + 1)
	  ideal = lerp(handleIn, handleOut, t)   ← G2-ideal position for smoothNode
	  delta = ideal − smoothNode              ← applied to handles since node is fixed

	fixSide : 'in' | 'out' | 'both'
	"""
	B = outerIn.position
	C = handleIn.position
	D = smoothNode.position  # never moved
	E = handleOut.position
	F = outerOut.position

	# Intersection of the two outer-handle tangent lines
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

	if fixSide in ('in', 'both'):
		handleIn.position = NSPoint(C.x + dx, C.y + dy)
	if fixSide in ('out', 'both'):
		handleOut.position = NSPoint(E.x + dx, E.y + dy)


# ─────────────────────────── main function ────────────────────────────────────


def positionalHarmonize(layer, harmonizeWith="behDotless-ar.medi"):
	"""
	Establishes G2 harmony between layer and the same-master layer of
	harmonizeWith at their shared on-curve (clicking) points.

	Only handles are moved; on-curve nodes stay fixed.
	Handles bridging two clicking points within the same glyph are left alone
	so the glyph's own internal curve shapes are preserved.
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

	sharedSet = frozenset(sharedPts)

	for cx, cy in sharedPts:
		for path in layer.paths:
			count = len(path.nodes)
			nodes = path.nodes

			for idx, node in nodesAtPos(path, cx, cy):
				if node.type == OFFCURVE or not node.smooth:
					continue

				prevNode = nodes[(idx - 1) % count]
				nextNode = nodes[(idx + 1) % count]
				prevIsHandle = prevNode.type == OFFCURVE
				nextIsHandle = nextNode.type == OFFCURVE

				if not prevIsHandle or not nextIsHandle:
					continue  # need curves on both sides for G2

				outerIn = nodes[(idx - 2) % count]
				outerOut = nodes[(idx + 2) % count]

				# Detect "internal" handles: those bridging two clicking nodes
				# within the same glyph.  In a standard cubic path, the on-curve
				# three steps away is the neighbour that a handle points toward.
				prevBeyond = nodes[(idx - 3) % count]
				nextBeyond = nodes[(idx + 3) % count]
				prevInternal = (int(round(prevBeyond.position.x)), int(round(prevBeyond.position.y))) in sharedSet
				nextInternal = (int(round(nextBeyond.position.x)), int(round(nextBeyond.position.y))) in sharedSet

				if prevInternal and not nextInternal:
					fixSide = 'out'
				elif nextInternal and not prevInternal:
					fixSide = 'in'
				else:
					fixSide = 'both'

				g2AdjustHandles(prevNode, node, nextNode, outerIn, outerOut, fixSide)

	layer.updateMetrics()
	print(f"✅ G2-harmonized '{layer.parent.name}' ({len(sharedPts)} clicking point(s)) with '{harmonizeWith}'.")


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
