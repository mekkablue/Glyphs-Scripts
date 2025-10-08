# -*- coding: utf-8 -*-
from __future__ import print_function

from AppKit import NSPoint, NSNotFound
from mekkablue import caseDict
from GlyphsApp import Glyphs, GSPath, GSNode, GSLINE
import math

if Glyphs.versionNumber >= 3.0:
	from GlyphsApp import LTR

intervalList = (1, 3, 5, 10, 20)
categoryList = (
	"Letter:Uppercase",
	"Letter:Lowercase",
	"Letter:Smallcaps",
	"Punctuation",
	"Symbol:Currency",
	"Symbol:Math",
	"Symbol:Other",
	"Symbol:Arrow",
	"Number:Decimal Digit",
	"Number:Small",
	"Number:Fraction",
)


def stringToListOfGlyphsForFont(string, Font, report=True, excludeNonExporting=True, suffix=""):
	# parse string into parseList:
	parseList = []
	waitForSeparator = False
	parsedName = ""

	# cut off comment:
	if "#" in string:
		string = string[:string.find("#")].strip()

	# parse string:
	for i, x in enumerate(string):
		if x in "@/ ":
			if parsedName:
				parseList.append(parsedName)
				parsedName = ""

			if x in "@/":
				waitForSeparator = True
			else:
				waitForSeparator = False

			if x == "@":
				parsedName = "@"

		elif waitForSeparator:
			parsedName += x
			if i == len(string) - 1:
				parseList.append(parsedName)
		else:
			parsedName = ""
			parseList.append(x)

	# go through parseList and find corresponding glyph in Font:
	glyphList = []
	for parsedName in parseList:

		if parsedName.startswith("@"):
			# category and subcategory:
			if ":" in parsedName:
				category, subcategory = parsedName[1:].split(":")
			else:
				category, subcategory = parsedName[1:], None
			# TODO parse
			categoryGlyphs = listOfNamesForCategories(
				Font,
				category,
				subcategory,  # OK
				"latin",  # requiredScript,  # need to implement still
				None,  # excludedGlyphNameParts,  # need to implement still
				excludeNonExporting,  # OK
				suffix=suffix,
			)
			if categoryGlyphs:
				glyphList += categoryGlyphs
				if report:
					print("Added glyphs for category %s, subcategory %s: %s" % (category, subcategory, ", ".join([g.name for g in categoryGlyphs])))
			elif report:
				print("Warning: no glyphs found for category %s, subcategory %s." % (category, subcategory))

		else:
			# actual single glyph names:
			glyph = Font.glyphForName_(parsedName + suffix)

			# actual single character:
			if not glyph and len(parsedName) == 1:
				unicodeForName = "%04X" % ord(parsedName)
				glyphInfo = Glyphs.glyphInfoForUnicode(unicodeForName)
				if glyphInfo:
					glyphName = "%s%s" % (glyphInfo.name, suffix)
					glyph = Font.glyphs[glyphName]

			# check if glyph exists, exports, and collect in glyphList:
			if glyph:
				if (glyph.export or not excludeNonExporting):
					glyphList.append(glyph)
				elif report:
					print("Ignoring non-exporting glyph '%s'." % (parsedName + suffix))
			elif report:
				print("Warning: Could not find glyph for '%s'." % (parsedName + suffix))

	return glyphList


def nameUntilFirstPeriod(glyphName):
	if "." not in glyphName:
		return glyphName
	else:
		offset = glyphName.find(".")
		return glyphName[:offset]


def effectiveKerning(leftGlyphName, rightGlyphName, thisFont, thisFontMasterID, directionSensitive=True):
	leftLayer = thisFont.glyphs[leftGlyphName].layers[thisFontMasterID]
	rightLayer = thisFont.glyphs[rightGlyphName].layers[thisFontMasterID]
	if Glyphs.versionNumber >= 3:
		direction = LTR
		if directionSensitive:
			if thisFont.currentTab:
				direction = thisFont.currentTab.direction
			else:  # no tab open
				direction = Glyphs.userInterfaceLayoutDirection()
		effectiveKerning = leftLayer.nextKerningForLayer_direction_(rightLayer, direction)
	else:
		effectiveKerning = leftLayer.rightKerningForLayer_(rightLayer)
	if effectiveKerning < NSNotFound:
		return effectiveKerning
	else:
		return 0.0

# older version:
# def effectiveKerning(leftGlyphName, rightGlyphName, thisFont, thisFontMasterID):
# leftLayer = thisFont.glyphs[leftGlyphName].layers[thisFontMasterID]
# rightLayer = thisFont.glyphs[rightGlyphName].layers[thisFontMasterID]
# if Glyphs.versionNumber >= 3.0:
# 	effectiveKerning = leftLayer.nextKerningForLayer_direction_(rightLayer, LTR)
# else:
# 	effectiveKerning = leftLayer.rightKerningForLayer_(rightLayer)
# return effectiveKerning  # can be NSNotFound

#  # if effectiveKerning < NSNotFound:
#  # 	return effectiveKerning
#  # else:
#  # 	return 0.0


def listOfNamesForCategories(thisFont, requiredCategory, requiredSubCategory, requiredScript, excludedGlyphNameParts, excludeNonExporting, suffix=""):
	nameList = []
	for thisGlyph in thisFont.glyphs:
		thisScript = thisGlyph.script
		glyphName = thisGlyph.name
		nameIsOK = True

		if suffix:
			nameIsOK = glyphName.endswith(suffix)

		if nameIsOK and excludedGlyphNameParts:
			for thisNamePart in excludedGlyphNameParts:
				nameIsOK = nameIsOK and thisNamePart not in glyphName

		if nameIsOK and (thisGlyph.export or not excludeNonExporting):
			if thisScript is None or thisScript == requiredScript:
				if thisGlyph.category == requiredCategory:
					if Glyphs.versionNumber >= 3:
						# GLYPHS 3
						if requiredSubCategory is None or thisGlyph.subCategory == requiredSubCategory or (
							requiredSubCategory in caseDict.keys() and thisGlyph.case == caseDict[requiredSubCategory]
						):
							nameList.append(glyphName)
					else:
						# GLYPHS 2
						if requiredSubCategory is None or thisGlyph.subCategory == requiredSubCategory:
							nameList.append(glyphName)

	return [thisFont.glyphs[n] for n in nameList]


def splitString(string, delimiter=":", minimum=2):
	# split string into a list:
	returnList = string.split(delimiter)

	# remove trailing spaces:
	for i in range(len(returnList)):
		returnList[i] = returnList[i].strip()

	# if necessary fill up with None:
	while len(returnList) < minimum:
		returnList.append(None)

	if returnList == [""]:
		return None

	return returnList


def measureLayerAtHeightFromLeftOrRight(thisLayer, height, leftSide=True):
	try:
		if leftSide:
			measurement = thisLayer.lsbAtHeight_(height)
		else:
			measurement = thisLayer.rsbAtHeight_(height)
		if measurement < NSNotFound:
			return measurement
		else:
			return None
	except:
		return None


def isHeightInIntervals(height, ignoreIntervals):
	if ignoreIntervals:
		for interval in ignoreIntervals:
			if height <= interval[1] and height >= interval[0]:
				return True
	return False


def minDistanceBetweenTwoLayers(leftLayer, rightLayer, interval=5.0, kerning=0.0, report=False, ignoreIntervals=[]):
	# correction = leftLayer.RSB+rightLayer.LSB
	if Glyphs.versionNumber >= 3.2:
		leftBounds, rightBounds = leftLayer.fastBounds(), rightLayer.fastBounds()
	else:
		leftBounds, rightBounds = leftLayer.bounds, rightLayer.bounds
	topY = min(leftBounds.origin.y + leftBounds.size.height, rightBounds.origin.y + rightBounds.size.height)
	bottomY = max(leftBounds.origin.y, rightBounds.origin.y)
	distance = topY - bottomY
	minDist = None
	for i in range(int(distance / interval)):
		height = bottomY + i * interval
		if not isHeightInIntervals(height, ignoreIntervals) or not ignoreIntervals:
			left = leftLayer.rsbAtHeight_(height)
			right = rightLayer.lsbAtHeight_(height)
			if left < NSNotFound and right < NSNotFound:  # avoid gaps like in i or j
				total = left + right + kerning  # +correction
				if minDist is None or minDist > total:
					minDist = total
	return minDist


def sortedIntervalsFromString(intervals="", font=None, mID=None):
	ignoreIntervals = []
	if intervals:
		for interval in intervals.split(","):
			if interval.find(":") != -1:
				interval = interval.strip()
				try:
					loEnd = interval.split(":")[0].strip()
					hiEnd = interval.split(":")[1].strip()

					if loEnd.isdigit():
						loEnd = int(loEnd)
					elif font and mID:
						layer = font.glyphs[loEnd].layers[mID]
						if layer:
							loEnd = int(layer.bounds.origin.y)
						else:
							raise Exception(f"Cannot find glyph with name: {loEnd} for lower end of interval")
							continue
					else:
						raise Exception(f"Cannot interpret lower end of ignore interval: {loEnd}. No font or master specified.")
						continue

					if hiEnd.isdigit():
						hiEnd = int(hiEnd)
					elif font and mID:
						layer = font.glyphs[hiEnd].layers[mID]
						if layer:
							hiEnd = int(layer.bounds.origin.y + layer.bounds.size.height)
						else:
							raise Exception(f"Cannot find glyph with name: {hiEnd} for higher end of interval")
							continue
					else:
						raise Exception(f"Cannot interpret higher end of ignore interval: {hiEnd}. No font or master specified.")
						continue

					intervalTuple = tuple(sorted([loEnd, hiEnd]))
					ignoreIntervals.append(intervalTuple)
				except Exception as e:
					print(f"Warning: could not convert '{interval.strip()}' into a number interval.")
					print(e)
					pass
			else:
				print(f"Warning: '{interval.strip()}' is not an interval (missing colon)")

	return ignoreIntervals


def distanceFromEntry(entry, font, masterID, default=0.0):
	try:
		distance = float(entry)
	except:
		correction = 0
		for operator in "+-":
			if operator in entry and entry.split(operator)[1].isnumeric():
				entry, correctionString = entry.split(operator)
				correction = float(operator + correctionString)
				break
		glyphs = stringToListOfGlyphsForFont(entry, font)
		if len(glyphs) > 2:
			glyphs = glyphs[:2]
		elif len(glyphs) == 1:
			glyphs.append(glyphs[0])
		elif len(glyphs) == 0:
			return default
		leftLayer = glyphs[0].layers[masterID]
		rightLayer = glyphs[1].layers[masterID]
		distance = minDistanceBetweenTwoLayers(leftLayer, rightLayer, interval=2.0) + correction
		print(f"‘{entry}’ = {distance}")
	return distance


def bubbleForLayer(layer, offset=10.0):
	def boxIsInsideBox(smallBox, bigBox):
		if bigBox.size.width * bigBox.size.height == 0.0:
			return False
		if smallBox.size.width > bigBox.size.width:
			return False
		if smallBox.size.height > bigBox.size.height:
			return False
		if smallBox.origin.x < bigBox.origin.x:
			return False
		if smallBox.origin.y < bigBox.origin.y:
			return False
		if smallBox.origin.x + smallBox.size.width > bigBox.origin.x + bigBox.size.width:
			return False
		if smallBox.origin.y + smallBox.size.height > bigBox.origin.y + bigBox.size.height:
			return False
		return True
	
	# just keep the relevant paths:
	workLayer = layer.copyDecomposedLayer()
	workLayer.removeOverlap()
	collectedPoints = []
	for path in workLayer.paths:
		if boxIsInsideBox(path.bounds, workLayer.bounds):
			continue
		collectedPoints.extend([(p.x, p.y) for p in path.nodes])
	
	bubbleCoordinates = bubble(collectedPoints, offset=offset)
	bubblePath = GSPath()
	for coord in bubbleCoordinates:
		newNode = GSNode()
		newNode.position = NSPoint(*coord)
		newNode.type = GSLINE
		bubblePath.nodes.append(newNode)
	
	bubblePath.closed = True
	return bubblePath


def bubble(points, offset=0.0):
	"""
	Creates a counter-clockwise winding polygon with only left angles around a list of NSPoints.
	:param points: List of NSPoints (each NSPoint is represented as a tuple of (x, y)).
	:param offset: Padding distance, default is 0.0.
	:return: List of NSPoints representing the outer polygon.
	"""
	offset *= -1
	
	if len(points) < 3:
		return points

	# Calculate convex hull using Gift Wrapping algorithm
	hull = []
	leftMost = min(points, key=lambda p: p[0])
	pointOnHull = leftMost

	while True:
		hull.append(pointOnHull)
		nextPoint = points[0]
		for candidate in points[1:]:
			# Check if candidate forms a left turn
			if nextPoint == pointOnHull or _calculateCrossProduct(pointOnHull, nextPoint, candidate) < 0:
				nextPoint = candidate
		if nextPoint == leftMost:
			break
		pointOnHull = nextPoint

	# Create offset points
	offsetPoints = []
	
	# Process each edge of the hull
	for i in range(len(hull)):
		p1 = hull[i]
		p2 = hull[(i + 1) % len(hull)]
		
		# Calculate direction and normal vectors
		deltaX = p2[0] - p1[0]
		deltaY = p2[1] - p1[1]
		length = (deltaX * deltaX + deltaY * deltaY) ** 0.5
		
		# Normalize and create perpendicular vector
		normalX = -deltaY / length
		normalY = deltaX / length
		
		# Create offset points
		offsetPoints.append((
			p1[0] + normalX * offset,
			p1[1] + normalY * offset
		))
		offsetPoints.append((
			p2[0] + normalX * offset,
			p2[1] + normalY * offset
		))

	# Remove duplicates and sort counter-clockwise
	offsetPoints = list(set(offsetPoints))
	center = _calculateCenter(offsetPoints)
	offsetPoints.sort(key=lambda p: _calculateAngle(p, center))
	return offsetPoints


def _calculateCrossProduct(o, a, b):
	return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _calculateCenter(points):
	x = sum(p[0] for p in points) / len(points)
	y = sum(p[1] for p in points) / len(points)
	return (x, y)


def _calculateAngle(p, center):
	return math.atan2(p[1] - center[1], p[0] - center[0])
