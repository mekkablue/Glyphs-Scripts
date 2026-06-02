

import math
from math import degrees, atan2
from Foundation import NSClassFromString, NSPoint
from AppKit import NSAffineTransform


def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct()  # returns the 6-float tuple
	Apply the matrix tuple like this:
		Layer.applyTransform(tMatrix)
		Component.applyTransform(tMatrix)
		Path.applyTransform(tMatrix)
	Chain multiple NSAffineTransform objects t1, t2 like this:
		t1.appendTransform_(t2)
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX, shiftY)
	if skew:
		myTransform.shearXBy_(math.tan(math.radians(skew)))
	return myTransform


def italicize(thisPoint, italicAngle=0.0, pivotalY=0.0):
	"""
	Returns the italicized position of an NSPoint 'thisPoint'
	for a given angle 'italicAngle' and the pivotal height 'pivotalY',
	around which the italic slanting is executed, usually half x-height.
	Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
	"""
	x = thisPoint.x
	yOffset = thisPoint.y - pivotalY  # calculate vertical offset
	italicAngle = math.radians(italicAngle)  # convert to radians
	tangens = math.tan(italicAngle)  # math.tan needs radians
	horizontalDeviance = tangens * yOffset  # vertical distance from pivotal point
	x += horizontalDeviance  # x of point that is yOffset from pivotal point
	return NSPoint(x, thisPoint.y)


def intersectionLineLinePoints(pointA, pointB, pointC, pointD, includeMidBcp=False):
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
			if not includeMidBcp:
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


def bezierWithPoints(A, B, C, D, t):
	x, y = bezier(A.x, A.y, B.x, B.y, C.x, C.y, D.x, D.y, t)
	return NSPoint(x, y)


def bezier(x1, y1, x2, y2, x3, y3, x4, y4, t):
	"""
	Returns coordinates for t (=0.0...1.0) on curve segment.
	x1,y1 and x4,y4: coordinates of on-curve nodes
	x2,y2 and x3,y3: coordinates of BCPs
	"""
	x = x1 * (1 - t)**3 + x2 * 3 * t * (1 - t)**2 + x3 * 3 * t**2 * (1 - t) + x4 * t**3
	y = y1 * (1 - t)**3 + y2 * 3 * t * (1 - t)**2 + y3 * 3 * t**2 * (1 - t) + y4 * t**3

	return x, y


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

	if xDiffFactor is not None:
		if 0.0 <= xDiffFactor <= 1.0:
			returnValue = True

	if yDiffFactor is not None:
		if 0.0 <= yDiffFactor <= 1.0:
			returnValue = True

	return returnValue


def divideAndTolerateZero(dividend, divisor):
	if float(divisor) == 0.0:
		return None
	else:
		return dividend / divisor


def angle(firstPoint, secondPoint):
	"""
	Returns the angle (in degrees) of the straight line between firstPoint and secondPoint,
	0 degrees being the second point to the right of first point.
	firstPoint, secondPoint: must be NSPoint or GSNode
	"""
	xDiff = secondPoint.x - firstPoint.x
	yDiff = secondPoint.y - firstPoint.y
	return degrees(atan2(yDiff, xDiff))


def centerOfRect(rect):
	"""
	Returns the center of NSRect rect as an NSPoint.
	"""
	center = NSPoint(rect.origin.x + rect.size.width / 2, rect.origin.y + rect.size.height / 2)
	return center


def normalizedCoordinate(x, y, layer, angle=0):
	"""
	Returns (nx, ny) in 0.0–1.0, 0.0–1.0 relative to the layer's bounding box,
	where (0, 0) is the bottom-left corner and (1, 1) is the top-right corner.
	angle: italic slant in degrees (positive = forward/rightward lean).
	At angle=0 the reference frame is an upright rectangle; at angle≠0 it is a
	parallelogram whose left and right edges lean by that angle, so a point on
	a slanted stem keeps the same nx across all heights.
	"""
	bbox = layer.bounds
	w = bbox.size.width
	h = bbox.size.height
	if w == 0 or h == 0:
		return (0.0, 0.0)
	dy = y - bbox.origin.y
	ny = dy / h
	slantOffset = dy * math.tan(math.radians(angle))
	nx = (x - bbox.origin.x - slantOffset) / w
	return (nx, ny)


def normalizedMove(glyph, pathIndex, nodeIndex, layerID1, layerID2):
	"""
	Returns (dnx, dny) — the move of a node from layerID1 to layerID2 in
	normalized bbox space (0.0–1.0 per axis), corrected for each layer's
	italic angle.  Positive values mean the node moved right / up.
	Returns None if either layer is missing, empty, or the path/node index
	is out of range.
	"""
	layer1 = glyph.layers[layerID1]
	layer2 = glyph.layers[layerID2]
	if layer1 is None or layer2 is None:
		return None
	try:
		node1 = layer1.paths[pathIndex].nodes[nodeIndex]
		node2 = layer2.paths[pathIndex].nodes[nodeIndex]
	except (IndexError, AttributeError):
		return None
	for layer in (layer1, layer2):
		b = layer.bounds
		if b.size.width == 0 or b.size.height == 0:
			return None
	nx1, ny1 = normalizedCoordinate(node1.x, node1.y, layer1, angle=layer1.italicAngle)
	nx2, ny2 = normalizedCoordinate(node2.x, node2.y, layer2, angle=layer2.italicAngle)
	return (nx2 - nx1, ny2 - ny1)


def offsetLayer(thisLayer, offset, makeStroke=False, position=0.5, autoStroke=False):
	offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
	try:
		# GLYPHS 3:
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			thisLayer,
			offset,
			offset,  # horizontal and vertical offset
			makeStroke,  # if True, creates a stroke
			autoStroke,  # if True, distorts resulting shape to vertical metrics
			position,  # stroke distribution to the left and right, 0.5 = middle
			None,
			None,
			None,
			0,
			0,
			True
		)
	except:
		# GLYPHS 2:
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyle_keepCompatibleOutlines_(
			thisLayer,
			offset,
			offset,  # horizontal and vertical offset
			makeStroke,  # if True, creates a stroke
			autoStroke,  # if True, distorts resulting shape to vertical metrics
			position,  # stroke distribution to the left and right, 0.5 = middle
			thisLayer.glyphMetrics(),  # metrics (G3)
			None,
			None,  # error, shadow
			0,  # NSButtLineCapStyle,  # cap style
			True,  # keep compatible
		)
