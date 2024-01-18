# MenuTitle: Path Problem Finder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds all kinds of potential problems in outlines, and opens a new tab with affected layers.
"""

import vanilla
import math
from timeit import default_timer as timer
from AppKit import NSPoint
from GlyphsApp import Glyphs, GSPath, GSControlLayer, GSShapeTypePath, GSLINE, GSCURVE, CURVE, GSOFFCURVE, QCURVE, Message, distance
from mekkaCore import mekkaObject


def reportTimeInNaturalLanguage(seconds):
	if seconds > 60.0:
		timereport = f"{int(seconds / 60)}:{int(seconds) % 60:02i} minutes"
	elif seconds < 1.0:
		timereport = f"{seconds:.2f} seconds"
	elif seconds < 20.0:
		timereport = f"{seconds:.1f} seconds"
	else:
		timereport = f"{int(seconds)} seconds"
	return timereport


canHaveOpenOutlines = (
	"_cap",
	"_corner",
	"_line",
	"_segment",
)


def hasStrayPoints(thisLayer):
	for p in thisLayer.paths:
		if len(p.nodes) == 1:
			return True
	return False


def hasDecimalCoordinates(thisLayer):
	for p in thisLayer.paths:
		for n in p.nodes:
			for coord in (n.x, n.y):
				if coord % 1.0 != 0.0:
					return True
	return False


def hasQuadraticCurves(thisLayer):
	for p in thisLayer.paths:
		for n in p.nodes:
			if n.type is QCURVE:
				return True
	return False


def hasOffcurveAsStartPoint(Layer):
	for p in Layer.paths:
		scenario1 = p.nodes[0].type == GSOFFCURVE and p.nodes[1].type != GSOFFCURVE
		scenario2 = p.nodes[0].type == CURVE and p.nodes[-1].type == GSOFFCURVE
		if scenario1 or scenario2:
			return True
	return False


def hasShallowCurveSegment(thisLayer, minSize):
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			if thisNode.type == CURVE:
				thisSegment = (
					thisNode.prevNode.prevNode.prevNode,
					thisNode.prevNode.prevNode,
					thisNode.prevNode,
					thisNode,
				)
				xCoords = [p.x for p in thisSegment]
				yCoords = [p.y for p in thisSegment]
				xDist = abs(min(xCoords) - max(xCoords))
				yDist = abs(min(yCoords) - max(yCoords))
				if xDist < minSize or yDist < minSize:
					for affectedNode in thisSegment:
						thisLayer.selection.append(affectedNode)
					return True
	return False


def hasZeroHandles(thisLayer):
	for thisPath in thisLayer.paths:
		numberOfNodes = len(thisPath.nodes)
		for i in range(numberOfNodes - 1):
			thisNode = thisPath.nodes[i]
			if thisNode.type == GSOFFCURVE:
				prevNodeIndex = (i - 1) % numberOfNodes
				nextNodeIndex = (i + 1) % numberOfNodes
				prevNode = thisPath.nodes[prevNodeIndex]
				nextNode = thisPath.nodes[nextNodeIndex]
				if thisNode.position == prevNode.position or thisNode.position == nextNode.position:
					return True
	return False


def hasTwoPointOutlines(thisLayer):
	for thisPath in thisLayer.paths:
		onCurveNodes = [n for n in thisPath.nodes if n.type != GSOFFCURVE]
		if len(onCurveNodes) < 3:
			return True
	return False


def hasOpenPaths(thisLayer):
	for thisPath in thisLayer.paths:
		if not thisPath.closed:
			return True
	return False


def hasBadOutlineOrder(thisLayer):
	firstPath = None
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		if thisLayer.shapes:
			for thisShape in thisLayer.shapes:
				if isinstance(thisShape, GSPath):
					firstPath = thisShape
					break
	else:
		# GLYPHS 2
		if thisLayer.paths:
			firstPath = thisLayer.paths[0]

	if firstPath and firstPath.direction != -1 and len(thisLayer.paths) > 1:
		return True
	else:
		return False


def hasAlmostOrthogonalLines(thisLayer, threshold=3.0):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSLINE:
				prevNodeIndex = (i - 1) % len(thisPath.nodes)
				prevNode = thisPath.nodes[prevNodeIndex]
				xDiff = abs(thisNode.x - prevNode.x)
				yDiff = abs(thisNode.y - prevNode.y)
				if (0.1 < xDiff and xDiff < threshold) or (0.1 < yDiff and threshold > yDiff):
					return True
	return False


def hasShortSegment(thisLayer, threshold=8.0):
	for thisPath in thisLayer.paths:
		for thisSegment in thisPath.segments:
			if thisSegment.length() < threshold:
				return True
	return False


def hasShallowCurve(thisLayer, threshold=5.0):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSCURVE:
				pointA = thisNode.position
				pointB = thisPath.nodes[(i - 1) % len(thisPath.nodes)].position
				pointC = thisPath.nodes[(i - 2) % len(thisPath.nodes)].position
				pointD = thisPath.nodes[(i - 3) % len(thisPath.nodes)].position
				for handle in (pointC, pointD):
					dist, vect = distanceAndRelativePosition(pointA, pointB, handle)
					if 0.0 < vect < 1.0 and dist < threshold:
						return True
	return False


def hasBadPathDirections(thisLayer):
	copyLayer = thisLayer.copy()
	copyLayer.correctPathDirection()
	for i in range(len(copyLayer.paths)):
		originalPath = thisLayer.paths[i]
		copyPath = copyLayer.paths[i]
		if copyPath.direction != originalPath.direction:
			return True
	return False


def hasShallowCurveBBox(thisLayer, threshold=10.0):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSCURVE:
				pointA = thisNode.position
				pointD = thisPath.nodes[(i - 3) % len(thisPath.nodes)].position
				if abs(pointA.x - pointD.x) < threshold or abs(pointA.y - pointD.y) < threshold:
					minX, maxX = sorted((pointA.x, pointD.x))
					minY, maxY = sorted((pointA.y, pointD.y))
					pointB = thisPath.nodes[(i - 1) % len(thisPath.nodes)].position
					pointC = thisPath.nodes[(i - 2) % len(thisPath.nodes)].position
					horizontallyWithin = minX - 1 < min(pointB.x, pointC.x) and maxX + 1 > max(pointB.x, pointC.x)
					verticallyWithin = minY - 1 < min(pointB.y, pointC.y) and maxY + 1 > max(pointB.y, pointC.y)
					if horizontallyWithin and verticallyWithin:
						return True
	return False


def angleBetweenPoints(firstPoint, secondPoint):
	"""
	Returns the angle (in degrees) of the straight line between firstPoint and secondPoint,
	0 degrees being the second point to the right of first point.
	firstPoint, secondPoint: must be NSPoint or GSNode
	"""
	xDiff = secondPoint.x - firstPoint.x
	yDiff = secondPoint.y - firstPoint.y
	return math.degrees(math.atan2(yDiff, xDiff))


def hasAngledHandles(thisLayer, threshold=8):
	for thisPath in thisLayer.paths:
		for i, handle in enumerate(thisPath.nodes):
			if handle.type == GSOFFCURVE:
				onCurveNodeIndex = (i - 1) % len(thisPath.nodes)
				onCurveNode = thisPath.nodes[onCurveNodeIndex]
				if onCurveNode.type == GSOFFCURVE:
					onCurveNodeIndex = (i + 1) % len(thisPath.nodes)
					onCurveNode = thisPath.nodes[onCurveNodeIndex]
				handleIsOrthogonal = handle.x == onCurveNode.x or handle.y == onCurveNode.y
				if not handleIsOrthogonal:
					angle = math.fabs(math.fmod(angleBetweenPoints(handle.position, onCurveNode.position), 90.0))
					if angle < threshold or angle > (90 - threshold):
						return True
	return False


def hasShortHandles(thisLayer, threshold=10.0):
	for thisPath in thisLayer.paths:
		for i, handle in enumerate(thisPath.nodes):
			if handle.type == GSOFFCURVE:
				onCurveNodeIndex = (i - 1) % len(thisPath.nodes)
				onCurveNode = thisPath.nodes[onCurveNodeIndex]
				if onCurveNode.type == GSOFFCURVE:
					onCurveNodeIndex = (i + 1) % len(thisPath.nodes)
					onCurveNode = thisPath.nodes[onCurveNodeIndex]
				if 0.0 < distance(handle.position, onCurveNode.position) < threshold:
					return True
	return False


def hasEmptyPaths(thisLayer):
	for thisShape in thisLayer.shapes:
		if thisShape.shapeType == GSShapeTypePath and len(thisShape.nodes) == 0:
			return True
	return False


def intersect(pointA, pointB, pointC, pointD):
	"""
	Returns an NSPoint of the intersection AB with CD,
	or None if there is no intersection.
	pointA, pointB: NSPoints or GSNodes representing the first line AB,
	pointC, pointD: NSPoints or GSNodes representing the second line CD.
	"""
	xA, yA = pointA.x, pointA.y
	xB, yB = pointB.x, pointB.y
	xC, yC = pointC.x, pointC.y
	xD, yD = pointD.x, pointD.y

	try:
		slopeAB = (float(yB) - float(yA)) / (float(xB) - float(xA))
	except:
		slopeAB = None  # division by zero if vertical

	try:
		slopeCD = (float(yD) - float(yC)) / (float(xD) - float(xC))
	except:
		slopeCD = None  # division by zero if vertical

	if slopeAB == slopeCD:  # parallel, no intersection
		return None
	elif slopeAB is None:  # first line is vertical
		x = xA
		y = slopeCD * (x - xC) + yC
	elif slopeCD is None:  # second line is vertical
		x = xC
		y = slopeAB * (x - xA) + yA
	else:  # both lines have different angles other than vertical
		x = (slopeAB * xA - yA - slopeCD * xC + yC) / (slopeAB - slopeCD)
		y = slopeAB * (x - xA) + yA
	return NSPoint(x, y)


def hasLargeHandles(thisLayer):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSCURVE:
				pointA = thisNode.position
				pointB = thisPath.nodes[(i - 1) % len(thisPath.nodes)].position
				pointC = thisPath.nodes[(i - 2) % len(thisPath.nodes)].position
				pointD = thisPath.nodes[(i - 3) % len(thisPath.nodes)].position
				intersection = intersect(pointA, pointB, pointC, pointD)
				if intersection:
					firstHandleTooLong = distance(pointA, pointB) > distance(pointA, intersection)
					secondHandleTooLong = distance(pointD, pointC) > distance(pointD, intersection)
					if firstHandleTooLong or secondHandleTooLong:
						return True
	return False


def hasOutwardHandles(thisLayer):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSCURVE:
				pointA = thisNode.position
				pointB = thisPath.nodes[(i - 1) % len(thisPath.nodes)].position
				pointC = thisPath.nodes[(i - 2) % len(thisPath.nodes)].position
				pointD = thisPath.nodes[(i - 3) % len(thisPath.nodes)].position
				if isOutside(pointA, pointD, pointB) or isOutside(pointA, pointD, pointC):
					return True
	return False


def hasCuspingHandles(thisLayer):
	for thisPath in thisLayer.paths:
		for n in thisPath.nodes:
			if n.type == GSOFFCURVE and n.nextNode.type == GSOFFCURVE:
				distAC = distance(n.prevNode.position, n.nextNode.position)
				distAB = distance(n.prevNode.position, n.position)
				distBD = distance(n.position, n.nextNode.nextNode.position)
				distCD = distance(n.nextNode.position, n.nextNode.nextNode.position)
				if distAC < distAB and distBD < distCD:
					thisLayer.selection = (n, n.nextNode)
					return True


def isOutside(p1, p2, p3):
	"""
	Returns True if p3 is outside p1-p2.
	"""
	deviation, nx = distanceAndRelativePosition(p1, p2, p3)
	if nx < 0.0 or nx > 1.0:
		return True
	return False


def distanceAndRelativePosition(p1, p2, p3):
	"""
	Returns:
	1. distance from p3 to nearest point of p1-p2
	2. relative position (0...1) of p3 between p1 & p2
	"""
	x1, y1 = p1.x, p1.y
	x2, y2 = p2.x, p2.y
	x3, y3 = p3.x, p3.y

	dx = x2 - x1
	dy = y2 - y1
	d2 = dx * dx + dy * dy
	try:
		nx = ((x3 - x1) * dx + (y3 - y1) * dy) / d2
	except:
		# division by zero
		nx = 0.0

	deviation = distance(p3, NSPoint(dx * nx + x1, dy * nx + y1))
	return deviation, nx


class PathProblemFinder(mekkaObject):
	title = "Path Problem Finder"
	prefDict = {
		# "prefName": defaultValue,
		"zeroHandles": 1,
		"outwardHandles": 0,
		"cuspingHandles": 0,
		"largeHandles": 0,
		"offcurveAsStartPoint": 1,
		"shortHandles": 0,
		"shortHandlesThreshold": 12,
		"angledHandles": 1,
		"angledHandlesAngle": 8,
		"shallowCurveBBox": 0,
		"shallowCurveBBoxThreshold": 5,
		"shallowCurve": 0,
		"shallowCurveThreshold": 10,
		"almostOrthogonalLines": 1,
		"almostOrthogonalLinesThreshold": 3,
		"shortSegment": 0,
		"shortSegmentThreshold": 8,
		"badOutlineOrder": 1,
		"badPathDirections": 1,
		"strayPoints": 1,
		"twoPointOutlines": 0,
		"openPaths": 0,
		"emptyPaths": 1,
		"quadraticCurves": 0,
		"decimalCoordinates": 0,
		"includeAllGlyphs": 1,
		"includeAllFonts": 0,
		"includeNonExporting": 0,
		"reuseTab": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 285
		windowHeight = 505
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			self.title,  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		if self.w.getPosSize()[3] != windowHeight - 19:
			print(self.w.getPosSize()[3], windowHeight - 19)
			self.w.resize(self.w.getPosSize()[2], windowHeight - 19, animate=False)

		# UI elements:
		linePos, inset, lineHeight, secondColumn = 12, 15, 22, 135
		indent, rightIndent = 155, 50
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "New tab with layers containing path problems:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.zeroHandles = vanilla.CheckBox((inset, linePos, secondColumn, 20), "Zero handles", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.zeroHandles.getNSButton().setToolTip_("Zero handles (a.k.a. half-dead curves) can cause problems with screen rendering, hinting and interpolation. Indicated with purple disks in the Show Angled Handles plug-in.")
		self.w.outwardHandles = vanilla.CheckBox((secondColumn, linePos, -inset, 20), "Outward-bent handles", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.outwardHandles.getNSButton().setToolTip_("Will find handles that point outside the stretch of their enclosing on-curves. Usually unwanted.")
		linePos += lineHeight

		self.w.largeHandles = vanilla.CheckBox((inset, linePos, -inset, 20), "Overshooting handles (larger than 100%)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.largeHandles.getNSButton().setToolTip_("Handles that are longer than 100%, i.e. going beyond the intersection with the opposing handle. Indicated with laser beams in the Show Angled Handles plug-in.")
		linePos += lineHeight

		self.w.offcurveAsStartPoint = vanilla.CheckBox((inset, linePos, indent, 20), "BCP as startpoint", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.offcurveAsStartPoint.getNSButton().setToolTip_("Finds paths where the first point happens to be a handle (off-curve point, BCP). Not really an issue, but you’ll like it if you are going full OCD on your font.")
		self.w.cuspingHandles = vanilla.CheckBox((secondColumn, linePos, -inset, 20), "Cusping handles", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.cuspingHandles.getNSButton().setToolTip_("Will find situations where, on a curve segment, the second handle comes before the first handle, i.e., is closer to the first on-curve. Usually unintended.")
		linePos += lineHeight

		self.w.shortHandles = vanilla.CheckBox((inset, linePos, indent, 20), "Handles shorter than:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.shortHandlesThreshold = vanilla.EditText((inset + indent, linePos, -inset - rightIndent - 5, 19), "12", callback=self.SavePreferences, sizeStyle='small')
		self.w.shortHandlesText = vanilla.TextBox((-inset - rightIndent, linePos + 3, -inset, 14), "units", sizeStyle='small', selectable=True)
		tooltipText = "Will find handles shorter than the specified amount in units. Short handles may cause kinks when rounded to the grid."
		self.w.shortHandlesThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shortHandles.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.angledHandles = vanilla.CheckBox((inset, linePos, indent, 20), "Angled handles up to:", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.angledHandlesAngle = vanilla.EditText((inset + indent, linePos, -inset - rightIndent - 5, 19), "8", callback=self.SavePreferences, sizeStyle='small')
		self.w.angledHandlesText = vanilla.TextBox((-inset - rightIndent, linePos + 3, -inset, 14), "degrees", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.shallowCurveBBox = vanilla.CheckBox((inset, linePos, indent, 20), "Curve bbox smaller than:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.shallowCurveBBoxThreshold = vanilla.EditText((inset + indent, linePos, -inset - rightIndent - 5, 19), "10", sizeStyle='small')
		self.w.shallowCurveBBoxText = vanilla.TextBox((-inset - rightIndent, linePos + 3, -inset, 14), "units", sizeStyle='small', selectable=True)
		tooltipText = "Will find very flat curve segments. Flat curves leave little manœuvring space for handles (BCPs), or cause very short handles, which in turn causes grid rounding problems. Can usually be fixed by removing an extremum point or adding an overlap."
		self.w.shallowCurveBBoxThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shallowCurveBBox.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.shallowCurve = vanilla.CheckBox((inset, linePos, indent, 20), "Curves shallower than:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.shallowCurveThreshold = vanilla.EditText((inset + indent, linePos, -inset - rightIndent - 5, 19), "5", sizeStyle='small')
		self.w.shallowCurveText = vanilla.TextBox((-inset - rightIndent, linePos + 3, -inset, 14), "units", sizeStyle='small', selectable=True)
		tooltipText = "Finds curve segments where the handles deviate less than the specified threshold from the enclosing on-curves."
		self.w.shallowCurveThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shallowCurve.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.shortSegment = vanilla.CheckBox((inset, linePos, indent, 20), "Segments shorter than:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.shortSegmentThreshold = vanilla.EditText((inset + indent, linePos, -inset - rightIndent - 5, 19), "8", sizeStyle='small')
		self.w.shortSegmentText = vanilla.TextBox((-inset - rightIndent, linePos + 3, -inset, 14), "units", sizeStyle='small', selectable=True)
		tooltipText = "Finds line segments (two consecutive on-curve nodes) shorter than the specified threshold length. Very short line segments may be deleted because they are barely visible. Also, if not orthogonal, may pose grid rounding problems."
		self.w.shortSegmentThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shortSegment.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.almostOrthogonalLines = vanilla.CheckBox((inset, linePos, indent, 20), "Non-orthogonal lines:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.almostOrthogonalLinesThreshold = vanilla.EditText((inset + indent, linePos, -inset - rightIndent - 5, 19), "3", callback=self.SavePreferences, sizeStyle='small')
		self.w.almostOrthogonalLinesText = vanilla.TextBox((-inset - rightIndent, linePos + 3, -inset, 14), "units off", sizeStyle='small', selectable=True)
		tooltipText = "Will find line segments that are close to, but not completely horizontal or vertical. Will look for segments where the x or y distance between the two nodes is less than the specified threshold. Often unintentional."
		self.w.almostOrthogonalLinesThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.almostOrthogonalLines.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.badOutlineOrder = vanilla.CheckBox((inset, linePos, secondColumn, 20), "Bad outline order", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.badOutlineOrder.getNSButton().setToolTip_("If the first path is clockwise, paths are most likely in the wrong order.")

		self.w.badPathDirections = vanilla.CheckBox((secondColumn, linePos, -inset, 20), "Bad path directions", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.badPathDirections.getNSButton().setToolTip_("Tries to find paths that have wrong orientations (clockwise vs. counterclockwise).\n⚠️ In complex setups, false positives are likely.")
		linePos += lineHeight

		self.w.openPaths = vanilla.CheckBox((inset, linePos, secondColumn, 20), "Open paths", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.openPaths.getNSButton().setToolTip_("Finds unclosed paths. Special glyphs that are supposed to have open paths, like corner and cap components, are ignored.")

		self.w.emptyPaths = vanilla.CheckBox((secondColumn, linePos, -inset, 20), "Empty paths", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.emptyPaths.getNSButton().setToolTip_("Tries to find paths that have no nodes at all. Should not happen but can be the result of an automated processing. Used to be a bug in Magic Remover. Can be fixed with Path > Tidy Up Paths, or with the mekkablue script Paths > Remove Stray Points and Empty Paths.")
		linePos += lineHeight

		self.w.strayPoints = vanilla.CheckBox((inset, linePos, secondColumn, 20), "Stray points", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.strayPoints.getNSButton().setToolTip_("In Glyphs 1, paths with only one node (‘single-node paths’ or ‘stray points’) used to be a method for disabling auto-alignment of components. But they are probably a mistake. Can be fixed wth mekkablue script Paths > Remove Stray Points and Empty Paths.")

		self.w.twoPointOutlines = vanilla.CheckBox((secondColumn, linePos, -inset, 20), "Two-node paths", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.twoPointOutlines.getNSButton().setToolTip_("Paths with only two on-curve nodes are most likely leftover debris from a previous operation.")
		linePos += lineHeight

		self.w.quadraticCurves = vanilla.CheckBox((inset, linePos - 1, secondColumn, 20), "Quadratic curves", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.quadraticCurves.getNSButton().setToolTip_("Finds quadratic (TrueType) curves. Useful if quadratic curves were not intended.")
		# linePos += lineHeight

		self.w.decimalCoordinates = vanilla.CheckBox((secondColumn, linePos - 1, -inset, 20), "Decimal coordinates", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.decimalCoordinates.getNSButton().setToolTip_("Nodes and handles with decimal coordinates, i.e., points not exactly on the unit grid.")
		linePos += lineHeight + 5

		self.w.checkCheckBoxes = vanilla.TextBox((inset, linePos + 2, 50, 14), "Select:", sizeStyle="small", selectable=True)
		self.w.checkALL = vanilla.SquareButton((70, linePos, 50, 18), "ALL", sizeStyle="small", callback=self.updateUI)
		self.w.checkNONE = vanilla.SquareButton((70 + 60 * 1, linePos, 50, 18), "NONE", sizeStyle="small", callback=self.updateUI)
		self.w.checkDEFAULT = vanilla.SquareButton((70 + 60 * 2, linePos, 70, 18), "DEFAULT", sizeStyle="small", callback=self.updateUI)
		linePos += lineHeight

		# Line Separator:
		self.w.line = vanilla.HorizontalLine((inset, linePos + 3, -inset, 1))
		linePos += int(lineHeight / 2)

		# Script Options:
		self.w.includeAllGlyphs = vanilla.CheckBox((inset, linePos, secondColumn, 20), "Check ALL glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeAllGlyphs.getNSButton().setToolTip_("If enabled, will ignore your current (glyph) selection, and simply go through the complete font. Recommended. May still ignore non-exporting glyph, see following option.")
		self.w.includeAllFonts = vanilla.CheckBox((secondColumn, linePos, -inset, 20), "⚠️ in ALL fonts", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeAllFonts.getNSButton().setToolTip_("If enabled, will go through ALL open fonts. Attention: can take quite some time.")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset, linePos, -inset, 20), "Include non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_("If disabled, will ignore glyphs that are set to not export.")
		linePos += lineHeight

		self.w.reuseTab = vanilla.CheckBox((inset, linePos, 125, 20), "Reuse existing tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.getNSButton().setToolTip_("If enabled, will only open a new tab if none is open. Recommended.")
		linePos += lineHeight

		# Progress Bar and Status text:
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		self.w.status = vanilla.TextBox((inset, -18 - inset, -inset - 80, 14), "🤖 Ready.", sizeStyle='small', selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Report", sizeStyle='regular', callback=self.PathProblemFinderMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		if sender in (self.w.checkALL, self.w.checkNONE, self.w.checkDEFAULT):
			excludedCheckSettings = ("includeAllGlyphs", "includeNonExporting", "reuseTab")
			checkSettings = [
				k for k in self.prefDict.keys() if k not in excludedCheckSettings and (not k.endswith("Threshold") and not k.endswith("Angle") or sender == self.w.checkDEFAULT)
			]
			for prefName in checkSettings:
				value = 0
				if sender == self.w.checkALL:
					value = 1
				elif sender == self.w.checkDEFAULT:
					value = self.prefDict[prefName]
				Glyphs.defaults[self.domain(prefName)] = value
			self.LoadPreferences()

		self.w.shallowCurveThreshold.enable(self.w.shallowCurve.get())
		self.w.shallowCurveBBoxThreshold.enable(self.w.shallowCurveBBox.get())
		self.w.almostOrthogonalLinesThreshold.enable(self.w.almostOrthogonalLines.get())
		self.w.shortHandlesThreshold.enable(self.w.shortHandles.get())
		self.w.angledHandlesAngle.enable(self.w.angledHandles.get())
		self.w.shortSegmentThreshold.enable(self.w.shortSegment.get())

		anyOptionIsOn = (
			self.w.zeroHandles.get() or self.w.outwardHandles.get() or self.w.cuspingHandles.get() or self.w.largeHandles.get() or self.w.shortHandles.get()
			or self.w.angledHandles.get() or self.w.shallowCurveBBox.get() or self.w.shallowCurve.get() or self.w.shortSegment.get() or self.w.almostOrthogonalLines.get()
			or self.w.badOutlineOrder.get() or self.w.badPathDirections.get() or self.w.strayPoints.get() or self.w.twoPointOutlines.get() or self.w.offcurveAsStartPoint.get()
			or self.w.openPaths.get() or self.w.quadraticCurves.get() or self.w.decimalCoordinates.get() or self.w.emptyPaths.get()
		)
		self.w.runButton.enable(anyOptionIsOn)

	def PathProblemFinderMain(self, sender):
		# clear macro window log:
		Glyphs.clearLog()

		# start taking time:
		start = timer()

		# update settings to the latest user input:
		self.SavePreferences()

		# Query user settings:
		zeroHandles = self.pref("zeroHandles")
		outwardHandles = self.pref("outwardHandles")
		cuspingHandles = self.pref("cuspingHandles")
		largeHandles = self.pref("largeHandles")
		offcurveAsStartPoint = self.pref("offcurveAsStartPoint")
		shortHandles = self.pref("shortHandles")
		shortHandlesThreshold = self.pref("shortHandlesThreshold")
		angledHandles = self.pref("angledHandles")
		# angledHandlesAngle = self.pref("angledHandlesAngle")
		shallowCurveBBox = self.pref("shallowCurveBBox")
		shallowCurveBBoxThreshold = self.pref("shallowCurveBBoxThreshold")
		shallowCurve = self.pref("shallowCurve")
		shallowCurveThreshold = self.pref("shallowCurveThreshold")
		almostOrthogonalLines = self.pref("almostOrthogonalLines")
		almostOrthogonalLinesThreshold = self.pref("almostOrthogonalLinesThreshold")
		shortSegment = self.pref("shortSegment")
		shortSegmentThreshold = self.pref("shortSegmentThreshold")
		badOutlineOrder = self.pref("badOutlineOrder")
		badPathDirections = self.pref("badPathDirections")
		strayPoints = self.pref("strayPoints")
		twoPointOutlines = self.pref("twoPointOutlines")
		openPaths = self.pref("openPaths")
		emptyPaths = self.pref("emptyPaths")
		quadraticCurves = self.pref("quadraticCurves")
		decimalCoordinates = self.pref("decimalCoordinates")
		includeAllGlyphs = self.pref("includeAllGlyphs")
		includeAllFonts = self.pref("includeAllFonts")
		includeNonExporting = self.pref("includeNonExporting")
		reuseTab = self.pref("reuseTab")

		theseFonts = Glyphs.fonts  # frontmost font
		countOfFontsWithIssues = 0
		totalLayerCount = 0
		totalGlyphCount = 0
		if not theseFonts:
			Message(
				title="No Font Open",
				message="The script requires a font. Open a font and run the script again.",
				OKButton=None,
			)
			return

		if not includeAllFonts:
			theseFonts = (Glyphs.font, )

		for fontIndex, thisFont in enumerate(theseFonts):
			try:
				thisFont.disableUpdateInterface()  # suppresses UI updates in Font View

				print(f"\n🪐 {self.title} Report for {thisFont.familyName}")
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				# determine the glyphs to work through:
				if includeAllGlyphs or includeAllFonts:
					glyphs = [g for g in thisFont.glyphs if includeNonExporting or g.export]
				else:
					glyphs = [layer.parent for layer in thisFont.selectedLayers]

				glyphCount = len(glyphs)
				print(f"Processing {glyphCount} glyphs:")

				allTestLayers = []
				allTestReports = []

				layersWithZeroHandles = []
				allTestLayers.append(layersWithZeroHandles)
				allTestReports.append("Zero Handles")
				layersWithOutwardHandles = []
				allTestLayers.append(layersWithOutwardHandles)
				allTestReports.append("Outward Handles")
				layersWithCuspingHandles = []
				allTestLayers.append(layersWithCuspingHandles)
				allTestReports.append("Cusping Handles")
				layersWithLargeHandles = []
				allTestLayers.append(layersWithLargeHandles)
				allTestReports.append("Large Handles")
				layersWithShortHandles = []
				allTestLayers.append(layersWithShortHandles)
				allTestReports.append("Short Handles")
				layersWithAngledHandles = []
				allTestLayers.append(layersWithAngledHandles)
				allTestReports.append("Angled Handles")
				layersWithShallowCurve = []
				allTestLayers.append(layersWithShallowCurve)
				allTestReports.append("Shallow Curve")
				layersWithShallowCurveBBox = []
				allTestLayers.append(layersWithShallowCurveBBox)
				allTestReports.append("Small Curve BBox")
				layersWithAlmostOrthogonalLines = []
				allTestLayers.append(layersWithAlmostOrthogonalLines)
				allTestReports.append("Almost Orthogonal Lines")
				layersWithshortSegments = []
				allTestLayers.append(layersWithshortSegments)
				allTestReports.append("Short Line Segments")
				layersWithBadOutlineOrder = []
				allTestLayers.append(layersWithBadOutlineOrder)
				allTestReports.append("Bad Outline Order")
				layersWithBadPathDirections = []
				allTestLayers.append(layersWithBadPathDirections)
				allTestReports.append("Bad Path Orientation")
				layersWithOffcurveAsStartpoint = []
				allTestLayers.append(layersWithOffcurveAsStartpoint)
				allTestReports.append("Off-curve as start point")
				layersWithStrayPoints = []
				allTestLayers.append(layersWithStrayPoints)
				allTestReports.append("Stray Points")
				layersWithTwoPointOutlines = []
				allTestLayers.append(layersWithTwoPointOutlines)
				allTestReports.append("Two-Point Outlines")
				layersWithOpenPaths = []
				allTestLayers.append(layersWithOpenPaths)
				allTestReports.append("Open Paths")
				layersWithQuadraticCurves = []
				allTestLayers.append(layersWithQuadraticCurves)
				allTestReports.append("Quadratic Curves")
				layersWithDecimalCoordinates = []
				allTestLayers.append(layersWithDecimalCoordinates)
				allTestReports.append("Decimal Coordinates")
				layersWithEmptyPaths = []
				allTestLayers.append(layersWithEmptyPaths)
				allTestReports.append("Empty Paths")

				progressSteps = glyphCount / 10
				progressCounter = 0
				stepsPerFont = 100 / len(theseFonts)
				firstStepPerFont = stepsPerFont * fontIndex
				for i, thisGlyph in enumerate(glyphs):
					# status update:
					if progressCounter > progressSteps:
						self.w.progress.set(firstStepPerFont + stepsPerFont * (i / glyphCount))
						progressCounter = 0
					progressCounter += 1
					self.w.status.set(f"{fontIndex}. {thisGlyph.name}...")
					# print(f"{i + 1}. {thisGlyph.name}")

					# step through layers
					for thisLayer in thisGlyph.layers:
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:

							if zeroHandles and hasZeroHandles(thisLayer):
								layersWithZeroHandles.append(thisLayer)
								print(f"  ❌ Zero handle(s) on layer: {thisLayer.name}")

							if outwardHandles and hasOutwardHandles(thisLayer):
								layersWithOutwardHandles.append(thisLayer)
								print(f"  ❌ Outward handle(s) on layer: {thisLayer.name}")

							if cuspingHandles and hasCuspingHandles(thisLayer):
								layersWithCuspingHandles.append(thisLayer)
								print(f"  ❌ Cusping handle(s) on layer: {thisLayer.name}")

							if largeHandles and hasLargeHandles(thisLayer):
								layersWithLargeHandles.append(thisLayer)
								print(f"  ❌ Large handle(s) on layer: {thisLayer.name}")

							if offcurveAsStartPoint and hasOffcurveAsStartPoint(thisLayer):
								layersWithOffcurveAsStartpoint.append(thisLayer)
								print(f"  ❌ Off-curve as start point on layer: {thisLayer.name}")

							if shortHandles and hasShortHandles(thisLayer, threshold=float(shortHandlesThreshold)):
								layersWithShortHandles.append(thisLayer)
								print(f"  ❌ Short handle(s) on layer: {thisLayer.name}")

							if angledHandles and hasAngledHandles(thisLayer):
								layersWithAngledHandles.append(thisLayer)
								print(f"  ❌ Angled handle(s) on layer: {thisLayer.name}")

							if shallowCurve and hasShallowCurve(thisLayer, threshold=float(shallowCurveThreshold)):
								layersWithShallowCurve.append(thisLayer)
								print(f"  ❌ Shallow curve(s) on layer: {thisLayer.name}")

							if shallowCurveBBox and hasShallowCurveBBox(thisLayer, threshold=float(shallowCurveBBoxThreshold)):
								layersWithShallowCurveBBox.append(thisLayer)
								print(f"  ❌ Shallow curve bbox(es) on layer: {thisLayer.name}")

							if almostOrthogonalLines and hasAlmostOrthogonalLines(thisLayer, threshold=float(almostOrthogonalLinesThreshold)):
								layersWithAlmostOrthogonalLines.append(thisLayer)
								print(f"  ❌ Almost orthogonal line(s) on layer: {thisLayer.name}")

							if shortSegment and hasShortSegment(thisLayer, threshold=float(shortSegmentThreshold)):
								layersWithshortSegments.append(thisLayer)
								print(f"  ❌ Short line(s) on layer: {thisLayer.name}")

							if badOutlineOrder and hasBadOutlineOrder(thisLayer):
								layersWithBadOutlineOrder.append(thisLayer)
								print(f"  ❌ Bad outline order(s) on layer: {thisLayer.name}")

							if badPathDirections and hasBadPathDirections(thisLayer):
								layersWithBadPathDirections.append(thisLayer)
								print(f"  ❌ Bad path direction(s) on layer: {thisLayer.name}")

							if strayPoints and hasStrayPoints(thisLayer):
								layersWithStrayPoints.append(thisLayer)
								print(f"  ❌ Stray points on layer: {thisLayer.name}")

							if twoPointOutlines and hasTwoPointOutlines(thisLayer):
								layersWithTwoPointOutlines.append(thisLayer)
								print(f"  ❌ Two-point outline(s) on layer: {thisLayer.name}")

							if openPaths:
								shouldProcess = True
								for nameStart in canHaveOpenOutlines:
									if nameStart in thisGlyph.name:
										shouldProcess = False
								if shouldProcess and hasOpenPaths(thisLayer):
									layersWithOpenPaths.append(thisLayer)
									print(f"  ❌ Open path(s) on layer: {thisLayer.name}")

							if decimalCoordinates and hasDecimalCoordinates(thisLayer):
								layersWithDecimalCoordinates.append(thisLayer)
								print(f"  ❌ Decimal coordinates in layer: {thisLayer.name}")

							if quadraticCurves and hasQuadraticCurves(thisLayer):
								layersWithQuadraticCurves.append(thisLayer)
								print(f"  ❌ Quadratic curves in layer: {thisLayer.name}")

							if emptyPaths and hasEmptyPaths(thisLayer):
								layersWithEmptyPaths.append(thisLayer)
								print(f"  ❌ Empty paths in layer: {thisLayer.name}")

				anyIssueFound = any(allTestLayers)
				countOfLayers = 0
				if anyIssueFound:
					countOfFontsWithIssues += 1
					tab = thisFont.currentTab
					if not tab or not reuseTab:
						# opens new Edit tab:
						tab = thisFont.newTab()
					tab.direction = 0  # force LTR
					layers = []

					currentMaster = thisFont.masters[tab.masterIndex]
					masterID = currentMaster.id

					# collect reports:
					for affectedLayers, reportTitle in zip(allTestLayers, allTestReports):
						countOfLayers += self.reportInTabAndMacroWindow(affectedLayers, reportTitle, layers, thisFont, masterID)

					tab.layers = layers

				totalLayerCount += countOfLayers
				totalGlyphCount += glyphCount

			except Exception as e:
				Glyphs.showMacroWindow()
				print(f"\n⚠️ Error in script:{e} \n")
				import traceback
				print(traceback.format_exc())
				print(thisFont)
				print()
			finally:
				thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

		# take time:
		end = timer()
		timereport = reportTimeInNaturalLanguage(end - start)
		print(f"\nTotal time elapsed: {timereport}.\nDone.")
		self.w.status.set(f"✅ Done. {timereport}.")
		self.w.progress.set(100)

		if len(theseFonts) == 1:
			if countOfFontsWithIssues:
				Message(
					title=f"{thisFont.familyName}: found path problems",
					message=f"{self.title} found {countOfLayers} issue{'s' if countOfLayers != 1 else ''} in {glyphCount} glyph{'s' if glyphCount != 1 else ''}. Details in Macro Window.",
					OKButton=None
				)
			else:
				Message(
					title=f"{thisFont.familyName}: all clear!",
					message=f"{self.title} found no issues, congratulations! Details in Macro Window.",
					OKButton=None,
				)
		else:
			if countOfFontsWithIssues:
				Message(
					title=f"Found path problems in {countOfFontsWithIssues} fonts",
					message=f"{self.title} found {totalLayerCount} issue{'s' if totalLayerCount != 1 else ''} in {totalGlyphCount} glyph{'s' if totalGlyphCount != 1 else ''} of {len(theseFonts)} fonts. Details in Macro Window.",
					OKButton=None
				)
			else:
				Message(
					title=f"All clear in {len(theseFonts)} fonts!",
					message=f"{self.title} found no issues, congratulations! Details in Macro Window.",
					OKButton=None,
				)

	def reportInTabAndMacroWindow(self, layerList, title, layers, font, masterID):
		if layerList and font:
			# report in Tab:
			tabtext = f"{title}:"

			# split description into layers, so we do not use layers
			# (simply adding to tab.text will reset all layers to the current master)
			for letter in tabtext:
				g = font.glyphs[letter]
				if g:
					layer = g.layers[masterID]
					if layer:
						layers.append(layer)
			layers.append(GSControlLayer.newline())
			for layer in layerList:
				layers.append(layer)
			for i in range(2):
				layers.append(GSControlLayer.newline())

			# report in Macro Window:
			glyphNames = "/" + "/".join(set([layer.parent.name for layer in layerList]))
			print(f"\n🔠 {title}:\n{glyphNames}")

		return len(layerList)


PathProblemFinder()
