# MenuTitle: Positional Harmonize
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Establishes G2 continuity between the current layer and behDotless-ar.medi
at their connection (clicking) points, by adjusting the one handle of the 
current glyph that faces the connection. On-curve nodes are never moved.

The ‘other’ handle used for the G2 ratio comes from behDotless-ar.medi,
shifted into the same coordinate space. Connection nodes need not be smooth.
"""

# G2 algorithm: Simon Cozens / mekkablue GreyHarmony.
# Clicking points: mekkablue Position Clicker algorithm (LSB ↔ RSB offset matching).

from math import sqrt
from AppKit import NSPoint, NSMakePoint
from GlyphsApp import Glyphs, OFFCURVE


def subPoints(p1, p2):
	return NSPoint(p1.x - p2.x, p1.y - p2.y)


def addPoints(p1, p2):
	return NSPoint(p1.x + p2.x, p1.y + p2.y)


def scalePoint(p, factor):
	return NSPoint(p.x * factor, p.y * factor)


def cross2D(p1, p2):
	return p1.x * p2.y - p1.y * p2.x


def harmonizedC(A, B, D, E, F, G):
	vectorED = subPoints(D, E)
	vectorDE = subPoints(E, D)

	left = cross2D(subPoints(D, B), vectorDE)
	right = cross2D(vectorDE, subPoints(F, E))
	epsilon = 1e-12

	if abs(right) < epsilon:
		return None

	ratio = left / right
	if ratio <= 0.0:
		return None

	factor = 1.0 + sqrt(ratio)
	return addPoints(E, scalePoint(vectorED, factor))


def harmonizedE(A, B, C, D, F, G):
	return harmonizedC(G, F, D, C, B, A)


def harmonizedCforDetachedSegments(A1, B1, D1, D2, E2, F2, G2):
	offset = subPoints(D1, D2)
	E2 = addPoints(E2, offset)
	F2 = addPoints(F2, offset)
	G2 = addPoints(G2, offset)
	return harmonizedC(A1, B1, D1, E2, F2, G2)


def harmonizedEforDetachedSegments(A1, B1, C1, D1, D2, F2, G2):
	return harmonizedCforDetachedSegments(G2, F2, D2, D1, C1, B1, A1)


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
		# C = C_handle.position
		D1 = layerNode.position
		D2 = refNode.position
		E = E_handle.position
		F = F_node.position
		G = G_node.position

		C_handle.position = harmonizedCforDetachedSegments(A, B, D1, D2, E, F, G)

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

		A = A_node.position
		B = B_node.position
		C = C_handle.position
		D1 = refNode.position
		D2 = layerNode.position
		# E = E_handle.position
		F = F_node.position
		G = G_node.position

		# E_handle.position = harmonizedCforDetachedSegments(G, F, D2, D1, C, B, A)
		E_handle.position = harmonizedEforDetachedSegments(A, B, C, D1, D2, F, G)

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
		print(f"✅ G2-harmonized '{layer.parent.name}' ({adjustedCount} handle{'' if adjustedCount==1 else 's'}) with '{harmonizeWith}'.")
	else:
		print(f"ℹ️ No handles adjusted for '{layer.parent.name}' — connection nodes may lack curve handles.")


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
