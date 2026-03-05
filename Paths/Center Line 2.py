#MenuTitle: Center Line 2
# -*- coding: utf-8 -*-
__doc__ = """
Will create center lines between selected segments and their opposites.
Hold down OPTION to put center lines in the background.
The script casts a ray perpendicular to each selected segment, collects ALL
intersections with other segments, and then picks the best opposing segment
based on: (a) it being reverse to the original, and (b) most similar in
length and angle (parallelism).
When more than one candidate is found, additional rays are cast from t=0.4,
t=0.6, t=0.3 and t=0.7 along the reference segment. Each additional ray that
also hits the same candidate boosts its score (confirmation bonus).
"""

import mekkablue
import math
from GlyphsApp import Glyphs, GSPath, GSNode, GSElement, Message
from AppKit import NSEvent, NSAlternateKeyMask


# -------------------------------------------------------------------------
# Geometry helpers
# -------------------------------------------------------------------------

def ptDist(a, b):
	"""Euclidean distance between two NSPoint/GSNode-like objects."""
	return math.hypot(b.x - a.x, b.y - a.y)


def segAngle(p1, p2):
	"""Angle of segment from p1 to p2, in radians."""
	return math.atan2(p2.y - p1.y, p2.x - p1.x)


def segLength(p1, p2):
	return ptDist(p1, p2)


def lineIntersect(p1, p2, p3, p4):
	"""
	Returns the intersection parameter t along (p1->p2) and u along (p3->p4),
	or None if the lines are parallel / degenerate.
	t in [0,1] means intersection is on segment p1-p2.
	u in [0,1] means intersection is on segment p3-p4.
	"""
	dx1 = p2.x - p1.x
	dy1 = p2.y - p1.y
	dx2 = p4.x - p3.x
	dy2 = p4.y - p3.y
	denom = dx1 * dy2 - dy1 * dx2
	if abs(denom) < 1e-9:
		return None
	dx3 = p3.x - p1.x
	dy3 = p3.y - p1.y
	t = (dx3 * dy2 - dy3 * dx2) / denom
	u = (dx3 * dy1 - dy3 * dx1) / denom
	return t, u


def ptAlongSeg(a, b, t):
	"""Point at parameter t (0=a, 1=b) along segment a→b."""
	class Pt:
		pass
	p = Pt()
	p.x = a.x + t * (b.x - a.x)
	p.y = a.y + t * (b.y - a.y)
	return p


def rayEndPoint(origin, angle, length=100000):
	"""Returns a far-away point along angle from origin (acts as ray endpoint)."""
	class Pt:
		pass
	ep = Pt()
	ep.x = origin.x + math.cos(angle) * length
	ep.y = origin.y + math.sin(angle) * length
	return ep


# -------------------------------------------------------------------------
# Segment helpers
# -------------------------------------------------------------------------

def selectedLineSegments(layer):
	"""
	Returns list of (nodeA, nodeB) for every selected ON-curve to ON-curve
	line segment in the layer.
	Only considers straight (line) segments: nodeB must be of type LINE or
	OFFCURVE == 0 (in case of line the next node is LINE type).
	In Glyphs, a 'line' segment is nodeB with type LINE (GSLINE = 'l').
	"""
	segments = []
	for path in layer.paths:
		nodes = path.nodes
		count = len(nodes)
		for i, node in enumerate(nodes):
			if not node.selected:
				continue
			nextNode = nodes[(i + 1) % count]
			# A straight segment: current node can be any type, next node is LINE
			if nextNode.type == "line" and nextNode.selected:
				segments.append((node, nextNode))
	return segments


def allLineSegmentsInLayer(layer):
	"""All straight segments in the layer as (nodeA, nodeB) pairs."""
	segs = []
	for path in layer.paths:
		nodes = path.nodes
		count = len(nodes)
		for i, node in enumerate(nodes):
			nextNode = nodes[(i + 1) % count]
			if nextNode.type == "line":
				segs.append((node, nextNode))
	return segs


# -------------------------------------------------------------------------
# Opposing segment scoring
# -------------------------------------------------------------------------

def reversalScore(seg1A, seg1B, seg2A, seg2B):
	"""
	Score for how 'reverse' seg2 is to seg1.
	A perfect reversal: seg2A is near seg1B and seg2B is near seg1A.
	Score = 1.0 for perfect reversal, 0.0 for forward parallel.
	"""
	# Direct: seg2A close to seg1A, seg2B close to seg1B
	directDist = ptDist(seg1A, seg2A) + ptDist(seg1B, seg2B)
	# Reversed: seg2A close to seg1B, seg2B close to seg1A
	reverseDist = ptDist(seg1A, seg2B) + ptDist(seg1B, seg2A)
	total = directDist + reverseDist
	if total < 1e-9:
		return 0.5
	return directDist / total  # higher = more reversed


def parallelityScore(angle1, angle2):
	"""
	1.0 = perfectly parallel (or anti-parallel), 0.0 = perpendicular.
	"""
	diff = abs(angle1 - angle2) % math.pi
	if diff > math.pi / 2:
		diff = math.pi - diff
	# diff == 0 → parallel, diff == pi/2 → perpendicular
	return 1.0 - (diff / (math.pi / 2))


def lengthSimilarityScore(len1, len2):
	"""1.0 = identical length, approaching 0 for very different lengths."""
	if len1 < 1e-9 and len2 < 1e-9:
		return 1.0
	bigger = max(len1, len2)
	smaller = min(len1, len2)
	return smaller / bigger


def scoreCandidateSegment(refA, refB, candA, candB):
	"""
	Combined score for how good candA-candB is as an opposing segment to refA-refB.
	Higher is better.
	"""
	refAngle = segAngle(refA, refB)
	candAngle = segAngle(candA, candB)
	refLen = segLength(refA, refB)
	candLen = segLength(candA, candB)

	wReverse = 0.5
	wParallel = 0.3
	wLength = 0.2

	rScore = reversalScore(refA, refB, candA, candB)
	pScore = parallelityScore(refAngle, candAngle)
	lScore = lengthSimilarityScore(refLen, candLen)

	return wReverse * rScore + wParallel * pScore + wLength * lScore


# -------------------------------------------------------------------------
# Ray casting: find all segments perpendicular rays from the ref seg hit
# -------------------------------------------------------------------------

# Additional t-positions tried when multiple candidates exist.
# t=0.5 is always cast first (the primary ray from midpoint).
EXTRA_T_POSITIONS = (0.4, 0.6, 0.3, 0.7)
# Bonus added to a candidate's score for each additional ray that confirms it.
CONFIRMATION_BONUS = 0.05


def castRayFromPoint(origin, refA, refB, allSegs, refSeg):
	"""
	Cast a perpendicular ray (both directions) from `origin` and return a set
	of candidate segment identities (id(cA), id(cB)) that are hit.
	"""
	refAngle = segAngle(refA, refB)
	perpAngle = refAngle + math.pi / 2
	hitIds = set()
	for direction in (perpAngle, perpAngle + math.pi):
		farPt = rayEndPoint(origin, direction)
		for (cA, cB) in allSegs:
			if (cA, cB) == refSeg or (cB, cA) == refSeg:
				continue
			result = lineIntersect(origin, farPt, cA, cB)
			if result is None:
				continue
			t, u = result
			if t <= 1e-6 or not (-1e-6 <= u <= 1.0 + 1e-6):
				continue
			hitIds.add((id(cA), id(cB)))
	return hitIds


def findOpposingSegments(refA, refB, allSegs, refSeg):
	"""
	Cast a ray perpendicular to refA-refB from its midpoint (t=0.5).
	Collect ALL segments it hits (excluding the reference segment itself).

	If more than one candidate is found, also cast rays from t=0.4, 0.6, 0.3,
	0.7 along the reference segment. Each additional ray that also hits the
	same candidate adds a CONFIRMATION_BONUS to its score.

	Returns list of (finalScore, cA, cB, hitX, hitY, rayT) sorted best first.
	"""
	refAngle = segAngle(refA, refB)
	perpAngle = refAngle + math.pi / 2

	mid = ptAlongSeg(refA, refB, 0.5)

	# --- primary ray from midpoint ---
	primaryCandidates = []  # list of [score, cA, cB, hitX, hitY, rayT]
	for direction in (perpAngle, perpAngle + math.pi):
		farPt = rayEndPoint(mid, direction)
		for (cA, cB) in allSegs:
			if (cA, cB) == refSeg or (cB, cA) == refSeg:
				continue
			result = lineIntersect(mid, farPt, cA, cB)
			if result is None:
				continue
			t, u = result
			if t <= 1e-6 or not (-1e-6 <= u <= 1.0 + 1e-6):
				continue
			baseScore = scoreCandidateSegment(refA, refB, cA, cB)
			hitX = cA.x + u * (cB.x - cA.x)
			hitY = cA.y + u * (cB.y - cA.y)
			primaryCandidates.append([baseScore, cA, cB, hitX, hitY, t])

	if not primaryCandidates:
		return []

	# Only worth probing extra t-positions when there is ambiguity
	if len(primaryCandidates) == 1:
		return [(c[0], c[1], c[2], c[3], c[4], c[5]) for c in primaryCandidates]

	# --- confirmation rays at additional t-positions ---
	# Build a lookup: (id(cA), id(cB)) → index in primaryCandidates
	candIdxByIds = {(id(c[1]), id(c[2])): i for i, c in enumerate(primaryCandidates)}

	for tPos in EXTRA_T_POSITIONS:
		origin = ptAlongSeg(refA, refB, tPos)
		hitIds = castRayFromPoint(origin, refA, refB, allSegs, refSeg)
		for segIds, idx in candIdxByIds.items():
			if segIds in hitIds:
				primaryCandidates[idx][0] += CONFIRMATION_BONUS

	primaryCandidates.sort(key=lambda c: -c[0])
	return [(c[0], c[1], c[2], c[3], c[4], c[5]) for c in primaryCandidates]


# -------------------------------------------------------------------------
# Path creation helper
# -------------------------------------------------------------------------

def makeCenterLinePath(x1, y1, x2, y2):
	"""Create an open GSPath with two nodes (a line segment)."""
	path = GSPath()
	path.closed = False
	n1 = GSNode()
	n1.position = (x1, y1)
	n1.type = "line"
	n2 = GSNode()
	n2.position = (x2, y2)
	n2.type = "line"
	path.nodes.append(n1)
	path.nodes.append(n2)
	return path


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------

def centerLineMain():
	font = Glyphs.font
	if not font:
		Message(title="No Font Open", message="Please open a font and try again.", OKButton=None)
		return

	# Check for Option key → put lines in background
	optionKeyDown = NSEvent.modifierFlags() & NSAlternateKeyMask

	layer = font.selectedLayers[0] if font.selectedLayers else None
	if not layer:
		Message(title="No Layer Selected", message="Please select a glyph layer.", OKButton=None)
		return

	selectedSegs = selectedLineSegments(layer)
	if not selectedSegs:
		Message(
			title="No Line Segments Selected",
			message="Please select at least one straight segment (two adjacent on-curve nodes).",
			OKButton=None,
		)
		return

	allSegs = allLineSegmentsInLayer(layer)
	addedPaths = []

	for (refA, refB) in selectedSegs:
		candidates = findOpposingSegments(refA, refB, allSegs, (refA, refB))
		if not candidates:
			print("⚠️ No opposing segment found for segment %s–%s" % (refA.position, refB.position))
			continue

		# Best candidate is first (highest score)
		score, candA, candB, hitX, hitY, _ = candidates[0]

		# Midpoint of reference segment
		midPt = ptAlongSeg(refA, refB, 0.5)
		midRefX, midRefY = midPt.x, midPt.y

		# Center line runs between midpoint of ref and intersection with best candidate
		# More precise: midpoint of ref ↔ midpoint of hit on candidate
		# Actually, the true center line should connect midpoints perpendicular through both stems.
		# We compute the center: average of (midRef) and (hitPt midpoint on candidate).
		# For a stem, the hit point on the candidate is the opposing "center" of the stem wall.
		# The center line midpoint between midRef and hitPt:
		centerX = (midRefX + hitX) / 2.0
		centerY = (midRefY + hitY) / 2.0

		# For the center line itself: draw it parallel to the reference segment,
		# centered at centerX/centerY, with the same half-length as the ref segment.
		refAngle = segAngle(refA, refB)
		halfLen = segLength(refA, refB) / 2.0
		lineX1 = centerX - math.cos(refAngle) * halfLen
		lineY1 = centerY - math.sin(refAngle) * halfLen
		lineX2 = centerX + math.cos(refAngle) * halfLen
		lineY2 = centerY + math.sin(refAngle) * halfLen

		path = makeCenterLinePath(lineX1, lineY1, lineX2, lineY2)
		addedPaths.append(path)
		print("✅ Center line added (score %.3f) for segment %s–%s" % (score, refA.position, refB.position))

	if not addedPaths:
		print("No center lines were created.")
		return

	font.disableUpdateInterface()
	try:
		targetLayer = layer.background if optionKeyDown else layer
		for path in addedPaths:
			targetLayer.paths.append(path)
		destination = "background" if optionKeyDown else "foreground"
		print("Added %i center line(s) to %s." % (len(addedPaths), destination))
	finally:
		font.enableUpdateInterface()


centerLineMain()
