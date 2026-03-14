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


def lineIntersect(p0, p1, p2, p3):
	"""Returns intersection point of lines p0-p1 and p2-p3 or None"""
	# Line p0-p1(a,b): a*p0.x + b*p1.x = ...
	a1 = p1.y - p0.y
	b1 = p0.x - p1.x
	c1 = a1 * p0.x + b1 * p0.y

	a2 = p3.y - p2.y
	b2 = p2.x - p3.x
	c2 = a2 * p2.x + b2 * p2.y

	det = a1 * b2 - a2 * b1
	if abs(det) < 1e-10:
		return None
	iX = (b2 * c1 - b1 * c2) / det
	iY = (a1 * c2 - a2 * c1) / det
	return NSMakePoint(iX, iY)

def pointDistanceSquared(p1, p2):
	dx = p1.x - p2.x
	dy = p1.y - p2.y
	return dx * dx + dy * dy

def distSquared(p1, p2):
	return pointDistanceSquared(p1, p2)

def harmonizeOnePoint(A, B, C, D, E, F, G, harmonizeIndex=2):
	"""
	Harmonize segments A-D-G at D by adjusting only the specified point.
	A, D, G: oncurve points (ADG cubic)
	B, C: handles for A-D
	E, F: handles for D-G
	harmonizeIndex: 0=A,1=B,2=C,3=D,4=E,5=F,6=G
	Returns the new NSPoint for the adjusted point.
	"""
	points = [A, B, C, D, E, F, G]
	if harmonizeIndex == 3:  # D, trivial
		return D

	# Identify left and right segments
	if harmonizeIndex <= 3:
		# Adjust left: right fixed
		leftOn1 = A
		leftH1 = B
		leftH2 = C
		joinOn1 = D
		rightOn1 = G
		rightH1 = E
		rightH2 = F
		fixedOn = G
	else:
		# Adjust right: left fixed
		leftOn1 = A
		leftH1 = B
		leftH2 = C
		joinOn1 = D
		rightOn1 = G
		rightH1 = E
		rightH2 = F
		fixedOn = A

	# Compute d = intersection leftH2-joinOn1 line and rightH1-rightH2 line
	line1P0 = leftH2
	line1P1 = joinOn1
	line2P0 = rightH1
	line2P1 = rightH2
	d = lineIntersect(line1P0, line1P1, line2P0, line2P1)
	if d is None:
		# Collinear or parallel, cannot compute geometric mean, return original
		return points[harmonizeIndex]

	# Compute ratios p0 = |leftH1 - leftH2| / |leftH2 - d|, but wait, according to algo p0 = |a1,a2| / |a2,d|
	# a1=leftH1? No: standard cubic a0=on1, a1=h1, a2=h2, a3=join
	# |a1 a2| incoming handle length? But gist says |a1,a2| / |a2,d|
	# Assuming a1 is incoming handle leftH1, a2=outgoing leftH2
	p0Num = math.sqrt(distSquared(leftH1, leftH2))
	p0Den = math.sqrt(distSquared(leftH2, d))
	if p0Den < 1e-10:
		return points[harmonizeIndex]
	p0 = p0Num / p0Den

	p1Num = math.sqrt(distSquared(d, rightH1))  # |d, b1|
	p1Den = math.sqrt(distSquared(rightH1, rightH2))
	if p1Den < 1e-10:
		return points[harmonizeIndex]
	p1 = p1Num / p1Den

	p = math.sqrt(p0 * p1)
	t = p / (p + 1.0)

	# Harmonic position for joinOn1
	harmonicD = NSMakePoint(leftH2.x * (1 - t) + rightH1.x * t,
						 leftH2.y * (1 - t) + rightH1.y * t)

	deltaX = harmonicD.x - joinOn1.x
	deltaY = harmonicD.y - joinOn1.y

	if harmonizeIndex <= 3:
		# Adjust left segment point
		newPoint = NSMakePoint(points[harmonizeIndex].x + deltaX,
							   points[harmonizeIndex].y + deltaY)
	else:
		# Adjust right segment point
		newPoint = NSMakePoint(points[harmonizeIndex].x + deltaX,
							   points[harmonizeIndex].y + deltaY)

	return newPoint

# ─────────────────────────── geometry helpers ─────────────────────────────────


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


def harmonizeOnePoint(A, B, C, D, E, F, G, harmonizeIndex=2):
	"""
	Harmonize two cubic Bezier segments that share on-curve point D, by moving
	exactly one handle to achieve G2 continuity at D.

	  A – B – C – D – E – F – G
	 on   off  off  on  off  off  on
	      ← left segment →   ← right segment →

	A, D, G: on-curve points.  B, C: handles for segment A→D (B near A, C near D).
	E, F: handles for segment D→G (E near D, F near G).

	harmonizeIndex: index of the point to adjust (0=A … 6=G).
	  2 → adjust C  (layer's inner handle when layer is at RSB / comesLater)
	  4 → adjust E  (layer's inner handle when layer is at LSB / comesFirst)

	Returns the new NSPoint for the adjusted point.
	Algorithm: Simon Cozens / mekkablue GreyHarmony.
	"""
	def dist(p, q):
		return math.hypot(q.x - p.x, q.y - p.y)

	# d = intersection of line C→D (left tangent at D) and line E→F (right shoulder)
	d = lineIntersection(C, D, E, F)
	if d is None:
		return [A, B, C, D, E, F, G][harmonizeIndex]

	p0Den = dist(C, d)
	p1Den = dist(E, F)
	if p0Den < 1e-10 or p1Den < 1e-10:
		return [A, B, C, D, E, F, G][harmonizeIndex]

	p0 = dist(B, C) / p0Den   # left ratio:  dist(B,C) / dist(C,d)
	p1 = dist(d, E) / p1Den   # right ratio: dist(d,E) / dist(E,F)

	p = math.sqrt(p0 * p1)
	t = p / (p + 1.0)

	harmonicD = NSPoint(C.x + t * (E.x - C.x), C.y + t * (E.y - C.y))
	deltaX = harmonicD.x - D.x
	deltaY = harmonicD.y - D.y

	pts = [A, B, C, D, E, F, G]
	return NSPoint(pts[harmonizeIndex].x + deltaX, pts[harmonizeIndex].y + deltaY)


def _segmentAnchor(clickingNode, handle):
	"""
	Return the on-curve node at the far end of the Bezier segment that contains handle.
	handle must be the prevNode or nextNode of clickingNode.
	"""
	if handle is clickingNode.prevNode:
		n = handle.prevNode
		while n.type == OFFCURVE:
			n = n.prevNode
		return n
	else:
		n = handle.nextNode
		while n.type == OFFCURVE:
			n = n.nextNode
		return n


def _inwardHandle(node, wantSmallerX):
	"""
	Return the off-curve handle adjacent to node whose Bezier segment leads into the
	glyph interior, or None if the inward segment is a straight line (no off-curve).

	Uses the x-position of each segment's far-end on-curve anchor to determine direction:
	  RSB clicking node (wantSmallerX=True):  inward curve goes left  → pick smaller anchor x.
	  LSB clicking node (wantSmallerX=False): inward curve goes right → pick larger  anchor x.

	Returns None if no adjacent off-curve exists on the inward side (line segment there).
	"""
	prevN = node.prevNode
	nextN = node.nextNode

	# Collect every adjacent off-curve handle together with its segment anchor's x.
	candidates = []
	if prevN.type == OFFCURVE:
		candidates.append((prevN, _segmentAnchor(node, prevN).position.x))
	if nextN.type == OFFCURVE:
		candidates.append((nextN, _segmentAnchor(node, nextN).position.x))

	if not candidates:
		return None  # no off-curve neighbours at all

	nodeX = node.position.x
	if wantSmallerX:
		# Interior is to the left: pick the candidate whose anchor is furthest left.
		handle, anchorX = min(candidates, key=lambda item: item[1])
		return handle if anchorX < nodeX else None  # None → inward side is a line
	else:
		# Interior is to the right: pick the candidate whose anchor is furthest right.
		handle, anchorX = max(candidates, key=lambda item: item[1])
		return handle if anchorX > nodeX else None  # None → inward side is a line


def _outerNode(clickingNode, handle):
	"""The node one step further beyond handle, away from clickingNode."""
	if handle is clickingNode.prevNode:
		return handle.prevNode
	return handle.nextNode


def harmonizeAtClickingNode(layerNode, refNode, isComesLater, shiftWidth):
	"""
	Applies G2 harmonization at a cross-glyph clicking point by assembling the
	seven-point geometry (A B C D E F G) and calling harmonizeOnePoint().

	isComesLater=True  (fina/medi, layer at RSB):
	  Left segment A→D lives in the layer (C is adjusted, harmonizeIndex=2).
	  Right segment D→G lives in the ref, shifted +shiftWidth into composite space.

	isComesLater=False (init/medi, layer at LSB):
	  Left segment A→D lives in the ref, shifted −shiftWidth into composite space.
	  Right segment D→G lives in the layer (E is adjusted, harmonizeIndex=4).

	Returns True if a handle was adjusted.
	"""
	if isComesLater:
		# ── left segment (A B C D): layer ──────────────────────────────────────
		C_handle = _inwardHandle(layerNode, wantSmallerX=True)
		if C_handle is None:
			return False
		B_node = _outerNode(layerNode, C_handle)
		A_node = _segmentAnchor(layerNode, C_handle)

		# ── right segment (D E F G): ref, shifted +shiftWidth ──────────────────
		E_handle = _inwardHandle(refNode, wantSmallerX=False)
		if E_handle is None:
			return False
		F_node = _outerNode(refNode, E_handle)
		G_node = _segmentAnchor(refNode, E_handle)

		A = A_node.position
		B = B_node.position
		C = C_handle.position
		D = layerNode.position
		E = NSPoint(E_handle.position.x + shiftWidth, E_handle.position.y)
		F = NSPoint(F_node.position.x + shiftWidth, F_node.position.y)
		G = NSPoint(G_node.position.x + shiftWidth, G_node.position.y)

		C_handle.position = harmonizeOnePoint(A, B, C, D, E, F, G, harmonizeIndex=2)

	else:  # comesFirst: layer at LSB
		# ── left segment (A B C D): ref, shifted −shiftWidth ───────────────────
		C_handle = _inwardHandle(refNode, wantSmallerX=True)
		if C_handle is None:
			return False
		B_node = _outerNode(refNode, C_handle)
		A_node = _segmentAnchor(refNode, C_handle)

		# ── right segment (D E F G): layer ─────────────────────────────────────
		E_handle = _inwardHandle(layerNode, wantSmallerX=False)
		if E_handle is None:
			return False
		F_node = _outerNode(layerNode, E_handle)
		G_node = _segmentAnchor(layerNode, E_handle)

		A = NSPoint(A_node.position.x - shiftWidth, A_node.position.y)
		B = NSPoint(B_node.position.x - shiftWidth, B_node.position.y)
		C = NSPoint(C_handle.position.x - shiftWidth, C_handle.position.y)
		D = layerNode.position
		E = E_handle.position
		F = F_node.position
		G = G_node.position

		E_handle.position = harmonizeOnePoint(A, B, C, D, E, F, G, harmonizeIndex=4)

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
