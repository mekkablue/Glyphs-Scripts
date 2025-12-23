#MenuTitle: Tunnify 2.0
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
A better, more gentle Tunnify, focused on staing closer to the same shape for each segment. Repeated running will change the shapes repeatedly.
"""

import math
from AppKit import NSPoint
from GlyphsApp import GSNode

def segmentMaxHandle(a, b, c, d):
	"""
	Intersection of segments a-b and c-d with zero-handle fix.
	a, b, c, d are GSNode/NSPoint with .x, .y and optionally .position.
	Returns NSPoint or None.
	"""

	# Extract positions (GSNode or NSPoint)
	def pos(p):
		return getattr(p, "position", p)

	pa = pos(a)
	pb = pos(b)
	pc = pos(c)
	pd = pos(d)

	# Zero-handle fixes
	if pa.x == pb.x and pa.y == pb.y:
		# use c.position instead of b.position
		pb = pc
	if pc.x == pd.x and pc.y == pd.y:
		# use b.position instead of c.position
		pc = pb

	x1, y1 = pa.x, pa.y
	x2, y2 = pb.x, pb.y
	x3, y3 = pc.x, pc.y
	x4, y4 = pd.x, pd.y

	den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
	if den == 0:
		return None

	t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
	u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / den

	if 0.0 <= t and u <= 1.0:
		ix = x1 + t * (x2 - x1)
		iy = y1 + t * (y2 - y1)
		return NSPoint(ix, iy)

	return None


def bezierPoint(a, b, c, d, t):
	"""Calculate a point on a cubic Bézier curve at parameter t."""
	x = (1-t)**3 * a.x + 3*(1-t)**2 * t * b.x + 3*(1-t)*t**2 * c.x + t**3 * d.x
	y = (1-t)**3 * a.y + 3*(1-t)**2 * t * b.y + 3*(1-t)*t**2 * c.y + t**3 * d.y
	return NSPoint(x, y)

def vectorFromTo(p1, p2):
	"""Vector from p1 to p2."""
	return NSPoint(p2.x - p1.x, p2.y - p1.y)

def scaleVector(v, scale):
	"""Scale vector v by scale."""
	return NSPoint(v.x * scale, v.y * scale)

def addVectors(p, v):
	"""Add vector v to point p."""
	return NSPoint(p.x + v.x, p.y + v.y)

def distance(p1, p2):
	"""Euclidean distance between two points."""
	return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)

def mid(p1, p2):
	return NSPoint((p1.x + p2.x)*0.5, (p1.y + p2.y)*0.5)

def twoThirds(p1, p2):
	pt = NSPoint(
		p1.x * 0.33 + p2.x * 0.67,
		p1.y * 0.33 + p2.y * 0.67,
		)
	return pt

def changeCurvatureToPassThroughPoint(a, b, c, d, passThroughPoint, min_t=0.25, max_t=0.75):
	"""
	Adjust control points b and c so the cubic Bézier curve passes near passThroughPoint
	at some t in [min_t, max_t]. Returns (a, new_b, new_c, d, best_t).
	
	Parameters:
	a, d: Fixed endpoints (NSPoint)
	b, c: Original control points (NSPoint)
	passThroughPoint: Target point (NSPoint)
	min_t, max_t: t-value search range (default: 0.25 to 0.75)
	
	Returns:
	(a, new_b, new_c, d, best_t) where:
		a, d: Unchanged endpoints
		new_b, new_c: Adjusted control points
		best_t: Optimal t-value found in [min_t, max_t]
	"""
	# Vectors for control point adjustment directions
	vec_ab = vectorFromTo(b, a)  # Vector from b toward a
	vec_dc = vectorFromTo(c, d)  # Vector from c toward d
	
	best_scale = 0
	best_t = min_t
	best_dist = float('inf')
	
	# Generate search space
	t_values = [min_t + i*(max_t-min_t)/50 for i in range(51)]  # 51 points in t-range
	scale_values = [i*0.01 for i in range(-100, 101)]  # Scale factors [-1.0, 1.0]
	
	# Brute-force search for optimal parameters
	for t in t_values:
		for scale in scale_values:
			# Adjust control points
			new_b = addVectors(b, scaleVector(vec_ab, scale))
			new_c = addVectors(c, scaleVector(vec_dc, scale))
			
			# Calculate curve point
			pt = bezierPoint(a, new_b, new_c, d, t)
			dist = distance(pt, passThroughPoint)
			
			# Update best parameters if closer
			if dist < best_dist:
				best_dist = dist
				best_scale = scale
				best_t = t
	
	# Apply best parameters
	new_b = addVectors(b, scaleVector(vec_ab, best_scale))
	new_c = addVectors(c, scaleVector(vec_dc, best_scale))
	
	return (a, new_b, new_c, d) #, best_t)

def tunnifySegment(a, b, c, d):
	maxPt = segmentMaxHandle(a, b, c, d)
	if maxPt is None:
		# print("No maxPt", a.position, b.position) # DEBUG
		return
	passThrough = bezierPoint(a, b, c, d, 0.5)
	newPositions = changeCurvatureToPassThroughPoint(
		a.position,
		mid(b.position, maxPt),
		mid(c.position, maxPt),
		d.position,
		passThrough,
		min_t=0.3,
		max_t=0.7,
		)
	for i, pt in enumerate(newPositions):
		(a, b, c, d)[i].position = pt

def tunnifyLayer(layer, selectionMatters=False):
	for p in layer.paths:
		for i, a in enumerate(p.nodes):
			if a.type == OFFCURVE:
				continue
			if p.closed == False and i > (len(p.nodes) - 4):
				continue
			b = a.nextNode
			if b.type != OFFCURVE:
				continue
			c, d = a.nextNode.nextNode, a.nextNode.nextNode.nextNode
			if c.type != OFFCURVE or d.type == OFFCURVE:
				continue
			if not selectionMatters or any([n.selected for n in (a, b, c, d)]):
				tunnifySegment(a, b, c, d)

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
selectionMatters = (len(selectedLayers)==1 and bool(selectedLayers[0].selection))

Glyphs.clearLog() # clears log in Macro window

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		print(f"🔡 Tunnifying {'selection in ' if selectionMatters else ''}{thisGlyph.name}")
		thisGlyph.beginUndo() # begin undo grouping
		tunnifyLayer(thisLayer, selectionMatters=selectionMatters)
		thisGlyph.endUndo()   # end undo grouping
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Tunnify 2.0\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	print("✅ Done.")
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
