# -*- coding: utf-8 -*--- --
from __future__ import print_function

from Foundation import NSNotFound

from GlyphsApp import Glyphs, caseDict
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
# def effectiveKerning( leftGlyphName, rightGlyphName, thisFont, thisFontMasterID ):
# leftLayer = thisFont.glyphs[leftGlyphName].layers[thisFontMasterID]
# rightLayer = thisFont.glyphs[rightGlyphName].layers[thisFontMasterID]
# if Glyphs.versionNumber >= 3.0:
# 	effectiveKerning = leftLayer.nextKerningForLayer_direction_( rightLayer, LTR )
# else:
# 	effectiveKerning = leftLayer.rightKerningForLayer_( rightLayer )
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
						raise Exception(f"Cannot interpret lower end of ignore interval: {loEnd}")
						continue

					if hiEnd.isdigit():
						loEnd = int(hiEnd)
					elif font and mID:
						layer = font.glyphs[hiEnd].layers[mID]
						if layer:
							hiEnd = int(layer.bounds.origin.y + layer.bounds.size.height)
						else:
							raise Exception(f"Cannot find glyph with name: {hiEnd} for higher end of interval")
							continue
					else:
						raise Exception(f"Cannot interpret higher end of ignore interval: {hiEnd}")
						continue

					intervalTuple = tuple(sorted([loEnd, hiEnd]))
					ignoreIntervals.append(intervalTuple)
				except Exception as e:
					print("Warning: could not convert '%s' into a number interval." % interval.strip())
					print(e)
					pass
			else:
				print("Warning: '%s' is not an interval (missing colon)" % interval.strip())

	return ignoreIntervals
