# MenuTitle: Positional Connection Harmonizer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Harmonizes connections between initial, medial and final glyphs based on behDotless-ar.medi.
"""

from AppKit import NSPoint
from math import sqrt
from GlyphsApp import Glyphs, GSNode, addPoints, subtractPoints, Message, OFFCURVE


def getIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
	px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
	py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
	return px, py


def remap(oldValue, oldMin, oldMax, newMin, newMax):
	try:
		oldRange = (oldMax - oldMin)
		newRange = (newMax - newMin)
		newValue = (((oldValue - oldMin) * newRange) / oldRange) + newMin
		return newValue
	except:
		return None


def getDist(a, b):
	dist = sqrt((b.x - a.x)**2 + (b.y - a.y)**2)
	return dist


def diffPoint(N, P, t):
	node = NSPoint()
	newX = remap(t, 0, 1, N.x, P.x)
	newY = remap(t, 0, 1, N.y, P.y)
	if not (newX is None or newY is None):
		newPosition = NSPoint(newX, newY)
		return subtractPoints(
			node.position if isinstance(node, GSNode) else node,
			newPosition,
		)
	return None


def harmonize(N, NN, P, PP):
	# adjacent handles:
	# N = node.nextNode
	# NN = node.nextNode.nextNode
	# P = node.prevNode
	# PP = node.prevNode.prevNode

	# find intersection of lines created by offcurves
	xIntersect, yIntersect = (
		getIntersection(
			N.x, N.y, NN.x, NN.y,
			P.x, P.y, PP.x, PP.y,
		)
	)
	intersection = NSPoint(xIntersect, yIntersect)

	# find ratios
	r0 = getDist(NN, N) / getDist(N, intersection)
	r1 = getDist(intersection, P) / getDist(P, PP)
	ratio = sqrt(r0 * r1)

	t = ratio / (ratio + 1)
	diff = diffPoint(N, P, t)
	return diff

	# N.position = addPoints(N.position, diff)
	# P.position = addPoints(P.position, diff)


def normalize(oncurve, off1, off2):
	return subtractPoints(off1, oncurve), subtractPoints(off2, oncurve)


def process(Layer, otherLayer):

	N, NN, P, PP = None, None, None, None
	nodeN, nodeP = None, None
	for p in Layer.paths:
		for n in p.nodes:
			if n.type != OFFCURVE and n.y <= 0:
				if n.prevNode.type == OFFCURVE:
					P, PP = normalize(n.position, n.prevNode.position, n.prevNode.prevNode.position)
					nodeP = n.prevNode
					continue
				if n.nextNode.type == OFFCURVE:
					N, NN = normalize(n.position, n.nextNode.position, n.nextNode.nextNode.position)
					nodeN = n.nextNode
					continue

	if all((N, NN, P, PP)):
		move = harmonize(N, NN, P, PP)
		nodeN.position = addPoints(nodeN.position, move)
		nodeP.position = addPoints(nodeP.position, move)


thisFont = Glyphs.font  # frontmost font
selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs
Glyphs.clearLog()  # clears log in Macro window

otherGlyph = thisFont.glyphs["behDotless-ar-medi"]
if not otherGlyph:
	Message(title="No Reference Glyph", message="This script requires a glyph called behDotless-ar.medi as a harmonization reference.", OKButton=None)
else:
	thisFont.disableUpdateInterface()  # suppresses UI updates in Font View

	try:
		for thisLayer in selectedLayers:
			otherLayer = otherGlyph.layers[thisLayer.master.id]
			thisGlyph = thisLayer.parent
			print(f"Processing {thisGlyph.name}")
			thisGlyph.beginUndo()  # begin undo grouping
			process(thisLayer, otherLayer)
			thisGlyph.endUndo()   # end undo grouping
	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ Error in script: Positional Connection Harmonizer\n")
		import traceback
		print(traceback.format_exc())
		print()
		raise e
	finally:
		thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
