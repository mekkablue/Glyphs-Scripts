#MenuTitle: Insert Split Nodes at Selected Extra Nodes
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Select an Extra Node (View > Show Nodes > Extra Nodes) and run this script, it will insert nodes in the respective paths. Do not rely on this script, it will become an extension to the Select tool (V) later.
"""

import math
from GlyphsApp import GSHandle, OFFCURVE

def nearestSegmentTimeForPoint(pt, nodes):
	"""
	Find the t value (0.0 to 1.0) on a segment closest to point pt.
	
	Args:
		pt: Target point (x, y)
		nodes: Tuple of either 2 points (A, B) for line or 4 points (A, B, C, D) for cubic Bézier
	
	Returns:
		t value between 0.0 and 1.0
	"""
	
	if len(nodes) == 2:
		# Line segment
		A, B = nodes
		
		# Vector from A to B
		dx = B[0] - A[0]
		dy = B[1] - A[1]
		
		# Vector from A to pt
		px = pt[0] - A[0]
		py = pt[1] - A[1]
		
		# Project pt onto line AB
		segmentLengthSquared = dx * dx + dy * dy
		
		if segmentLengthSquared == 0:
			return 0.0
		
		t = (px * dx + py * dy) / segmentLengthSquared
		return max(0.0, min(1.0, t))
	
	elif len(nodes) == 4:
		# Cubic Bézier curve
		A, B, C, D = nodes
		
		def bezierPoint(t):
			"""Calculate point on cubic Bézier at parameter t"""
			t2 = t * t
			t3 = t2 * t
			mt = 1 - t
			mt2 = mt * mt
			mt3 = mt2 * mt
			
			x = mt3 * A[0] + 3 * mt2 * t * B[0] + 3 * mt * t2 * C[0] + t3 * D[0]
			y = mt3 * A[1] + 3 * mt2 * t * B[1] + 3 * mt * t2 * C[1] + t3 * D[1]
			return (x, y)
		
		def distanceSquared(t):
			"""Calculate squared distance from pt to curve at parameter t"""
			p = bezierPoint(t)
			dx = p[0] - pt[0]
			dy = p[1] - pt[1]
			return dx * dx + dy * dy
		
		# Sample the curve to find a good starting point
		bestT = 0.0
		bestDist = distanceSquared(0.0)
		
		samples = 20
		for i in range(samples + 1):
			t = i / samples
			dist = distanceSquared(t)
			if dist < bestDist:
				bestDist = dist
				bestT = t
		
		# Refine using Newton-Raphson-like iteration
		t = bestT
		epsilon = 1e-6
		maxIterations = 10
		
		for _ in range(maxIterations):
			# Calculate derivative of distance function
			h = 0.0001
			if t > h and t < 1.0 - h:
				grad = (distanceSquared(t + h) - distanceSquared(t - h)) / (2 * h)
				secondGrad = (distanceSquared(t + h) - 2 * distanceSquared(t) + distanceSquared(t - h)) / (h * h)
				
				if abs(secondGrad) > epsilon:
					tNew = t - grad / secondGrad
					tNew = max(0.0, min(1.0, tNew))
					
					if abs(tNew - t) < epsilon:
						break
					t = tNew
				else:
					break
			else:
				break
		
		# Final check at boundaries
		dist0 = distanceSquared(0.0)
		dist1 = distanceSquared(1.0)
		distT = distanceSquared(t)
		
		if dist0 < distT:
			return 0.0
		elif dist1 < distT:
			return 1.0
		
		return t
	
	else:
		raise ValueError("nodes must contain either 2 points (line) or 4 points (cubic Bézier)")

font = Glyphs.font
selectedLayers = font.selectedLayers
if len(selectedLayers) == 1:
	layer = selectedLayers[0]
	for s in layer.selection:
		if not isinstance(s, GSHandle):
			continue
		pt = s.position
		for intersect in layer.intersections():
			if distance(pt, intersect) < 0.72:
				for p in layer.paths:
					for i, n in enumerate(p.nodes):
						if n.type == OFFCURVE:
							continue
						if n.prevNode.type == OFFCURVE:
							segment=(
								n.prevNode.prevNode.prevNode.position,
								n.prevNode.prevNode.position,
								n.prevNode.position,
								n.position,
								)
						else:
							segment=(
								n.prevNode.position,
								n.position,
								)
						nearestTime = nearestSegmentTimeForPoint(pt, segment)
						nearestPoint = p.pointAtPathTime_(i+nearestTime)
						if distance(pt, nearestPoint) < 0.72:
							p.insertNodeWithPathTime_(i+nearestTime)
							break
