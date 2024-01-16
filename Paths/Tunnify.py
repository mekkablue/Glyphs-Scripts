# MenuTitle: Tunnify
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Averages out the handles of selected path segments (or all paths if nothing is selected or multiple glyphs are selected). Doing this is a good idea for zero handles, and as preparation for interpolation. If you just want to fix zero handles, then check out the FixZeroHandles plugin in Window > Plugin Manager.
"""

from Foundation import NSPoint
from GlyphsApp import Glyphs, GSOFFCURVE

tunnifiedZeroLo = 0.43
tunnifiedZeroHi = 0.73


def intersectionWithNSPoints(pointA, pointB, pointC, pointD):
	"""
	Returns an NSPoint of the intersection AB with CD.
	Or False if there is no intersection
	"""
	try:
		x1, y1 = pointA.x, pointA.y
		x2, y2 = pointB.x, pointB.y
		x3, y3 = pointC.x, pointC.y
		x4, y4 = pointD.x, pointD.y

		try:
			slope12 = (float(y2) - float(y1)) / (float(x2) - float(x1))
		except:
			# division by zero if vertical
			slope12 = None

		try:
			slope34 = (float(y4) - float(y3)) / (float(x4) - float(x3))
		except:
			# division by zero if vertical
			slope34 = None

		if slope12 == slope34:
			# parallel, no intersection
			return None
		elif slope12 is None:
			# first line is vertical
			x = x1
			y = slope34 * (x - x3) + y3
		elif slope34 is None:
			# second line is vertical
			x = x3
			y = slope12 * (x - x1) + y1
		else:
			# both lines have an angle
			x = (slope12 * x1 - y1 - slope34 * x3 + y3) / (slope12 - slope34)
			y = slope12 * (x - x1) + y1

		intersectionPoint = NSPoint(x, y)
		if bothPointsAreOnSameSideOfOrigin(intersectionPoint, pointB, pointA) and bothPointsAreOnSameSideOfOrigin(intersectionPoint, pointC, pointD):
			if pointIsBetweenOtherPoints(intersectionPoint, pointB, pointA) or pointIsBetweenOtherPoints(intersectionPoint, pointC, pointD):
				return None
			return intersectionPoint
		else:
			return None

	except Exception as e:
		print(e)
		import traceback
		print(traceback.format_exc())
		return None


def bothPointsAreOnSameSideOfOrigin(pointA, pointB, pointOrigin):
	returnValue = True
	xDiff = (pointA.x - pointOrigin.x) * (pointB.x - pointOrigin.x)
	yDiff = (pointA.y - pointOrigin.y) * (pointB.y - pointOrigin.y)
	if xDiff <= 0.0 and yDiff <= 0.0:
		returnValue = False
	return returnValue


def pointIsBetweenOtherPoints(thisPoint, otherPointA, otherPointB):
	returnValue = False

	xDiffAB = otherPointB.x - otherPointA.x
	yDiffAB = otherPointB.y - otherPointA.y
	xDiffAP = thisPoint.x - otherPointA.x
	yDiffAP = thisPoint.y - otherPointA.y
	xDiffFactor = divideAndTolerateZero(xDiffAP, xDiffAB)
	yDiffFactor = divideAndTolerateZero(yDiffAP, yDiffAB)

	if xDiffFactor:
		if 0.0 <= xDiffFactor <= 1.0:
			returnValue = True

	if yDiffFactor:
		if 0.0 <= yDiffFactor <= 1.0:
			returnValue = True

	return returnValue


def divideAndTolerateZero(dividend, divisor):
	if float(divisor) == 0.0:
		return None
	else:
		return dividend / divisor


def pointDistance(x1, y1, x2, y2):
	"""Calculates the distance between P1 and P2."""
	dist = ((float(x2) - float(x1))**2 + (float(y2) - float(y1))**2)**0.5
	return dist


def bezier(x1, y1, x2, y2, x3, y3, x4, y4, t):
	x = x1 * (1 - t)**3 + x2 * 3 * t * (1 - t)**2 + x3 * 3 * t**2 * (1 - t) + x4 * t**3
	y = y1 * (1 - t)**3 + y2 * 3 * t * (1 - t)**2 + y3 * 3 * t**2 * (1 - t) + y4 * t**3
	return x, y


def xyAtPercentageBetweenTwoPoints(firstPoint, secondPoint, percentage):
	"""
	Returns the x, y for the point at percentage
	(where 100 percent is represented as 1.0)
	between NSPoints firstPoint and secondPoint.
	"""
	x = firstPoint.x + percentage * (secondPoint.x - firstPoint.x)
	y = firstPoint.y + percentage * (secondPoint.y - firstPoint.y)
	return x, y


def handlePercentages(segment):
	"""Calculates the handle distributions and intersection for segment P1, P2, P3, P4."""
	x1, y1 = segment[0]
	x2, y2 = segment[1]
	x3, y3 = segment[2]
	x4, y4 = segment[3]

	if [x1, y1] == [x2, y2]:
		# zero handle at beginning of segment
		xInt, yInt = x3, y3
		return tunnifiedZeroLo, tunnifiedZeroHi, xInt, yInt
	elif [x3, y3] == [x4, y4]:
		# zero handle at end of segment
		xInt, yInt = x2, y2
		return tunnifiedZeroHi, tunnifiedZeroLo, xInt, yInt
	else:
		# no zero handle, just bad distribution
		intersectionPoint = intersectionWithNSPoints(NSPoint(x1, y1), NSPoint(x2, y2), NSPoint(x3, y3), NSPoint(x4, y4))
		if intersectionPoint:
			xInt, yInt = intersectionPoint.x, intersectionPoint.y
			percentageP1P2 = pointDistance(x1, y1, x2, y2) / pointDistance(x1, y1, xInt, yInt)
			percentageP3P4 = pointDistance(x4, y4, x3, y3) / pointDistance(x4, y4, xInt, yInt)
			tunnifiedPercentage = (percentageP1P2 + percentageP3P4) / 2
			return tunnifiedPercentage, tunnifiedPercentage, xInt, yInt
		else:
			return None


def tunnify(segment):
	"""
	Calculates the average curvature for Bezier curve segment P1, P2, P3, P4,
	and returns new values for P2, P3.
	"""
	x1, y1 = segment[0]
	x4, y4 = segment[3]
	newHandlePercentages = handlePercentages(segment)
	if newHandlePercentages:
		firstHandlePercentage, secondHandlePercentage, xInt, yInt = newHandlePercentages
		intersectionPoint = NSPoint(xInt, yInt)
		segmentStartPoint = NSPoint(x1, y1)
		segmentFinalPoint = NSPoint(x4, y4)

		firstHandleX, firstHandleY = xyAtPercentageBetweenTwoPoints(segmentStartPoint, intersectionPoint, firstHandlePercentage)
		secondHandleX, secondHandleY = xyAtPercentageBetweenTwoPoints(segmentFinalPoint, intersectionPoint, secondHandlePercentage)
		return firstHandleX, firstHandleY, secondHandleX, secondHandleY
	else:
		return None


Font = Glyphs.font

if len(Font.selectedLayers) > 1:
	selectionCounts = False
elif not Font.selectedLayers[0].selection:
	selectionCounts = False
else:
	selectionCounts = True

for selectedLayer in Font.selectedLayers:
	selectedGlyph = selectedLayer.parent
	# selectedGlyph.beginUndo()  # undo grouping causes crashes

	for thisPath in selectedLayer.paths:
		numOfNodes = len(thisPath.nodes)

		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSOFFCURVE and (thisNode.selected or not selectionCounts):
				if thisPath.nodes[i - 1].type == GSOFFCURVE:
					segmentNodeIndexes = [i - 2, i - 1, i, i + 1]
				else:
					segmentNodeIndexes = [i - 1, i, i + 1, i + 2]

				for x in range(len(segmentNodeIndexes)):
					segmentNodeIndexes[x] = segmentNodeIndexes[x] % numOfNodes

				thisSegment = [(n.x, n.y) for n in [thisPath.nodes[i] for i in segmentNodeIndexes]]
				newSegmentHandles = tunnify(thisSegment)
				if newSegmentHandles:
					x_handle1, y_handle1, x_handle2, y_handle2 = newSegmentHandles
					thisPath.nodes[segmentNodeIndexes[1]].x = x_handle1
					thisPath.nodes[segmentNodeIndexes[1]].y = y_handle1
					thisPath.nodes[segmentNodeIndexes[2]].x = x_handle2
					thisPath.nodes[segmentNodeIndexes[2]].y = y_handle2

	# selectedGlyph.endUndo()  # undo grouping causes crashes
