# -*- coding: utf-8 -*--- --
from __future__ import print_function
from GlyphsApp import Glyphs
from Foundation import NSNotFound

intervalList = (1,3,5,10,20)
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

def stringToListOfGlyphsForFont( string, Font, report=True, excludeNonExporting=True, suffix="" ):
	# parse string into parseList:
	parseList = []
	waitForSeparator = False
	parsedName = ""
	
	# cut off comment:
	if "#" in string:
		string = string[:string.find("#")].strip()
	
	# parse string:
	for i,x in enumerate(string):
		if x in "/ ":
			if parsedName:
				parseList.append(parsedName)
				parsedName = ""
			if x == "/":
				waitForSeparator = True
			else:
				waitForSeparator = False
		elif waitForSeparator:
			parsedName += x
			if i == len(string)-1:
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
				Font, category, subcategory, #OK
				"latin", # requiredScript,  # need to implement still
				None, # excludedGlyphNameParts, # need to implement still
				excludeNonExporting, #OK
				suffix=suffix,
			)
			if categoryGlyphs:
				glyphList += categoryGlyphs
				if report:
					print(u"Added glyphs for category %s, subcategory %s: %s" % (category, subcategory, ", ".join(categoryGlyphs)))
			elif report:
				print(u"Warning: no glyphs found for category %s, subcategory %s." % (category, subcategory))
		
		else:
			# actual single glyph names:
			glyph = Font.glyphForName_(parsedName+suffix)
			
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
					print(u"Ignoring non-exporting glyph '%s'." % (parsedName+suffix))
			elif report:
				print(u"Warning: Could not find glyph for '%s'." % (parsedName+suffix))
	
	return glyphList

def nameUntilFirstPeriod( glyphName ):
	if not "." in glyphName:
		return glyphName
	else:
		offset = glyphName.find(".")
		return glyphName[:offset]

def effectiveKerning( leftGlyphName, rightGlyphName, thisFont, thisFontMasterID ):
	leftLayer = thisFont.glyphs[leftGlyphName].layers[thisFontMasterID]
	rightLayer = thisFont.glyphs[rightGlyphName].layers[thisFontMasterID]
	effectiveKerning = leftLayer.rightKerningForLayer_( rightLayer )
	if effectiveKerning < NSNotFound:
		return effectiveKerning
	else:
		return 0.0

def listOfNamesForCategories( thisFont, requiredCategory, requiredSubCategory, requiredScript, excludedGlyphNameParts, excludeNonExporting, suffix="" ):
	nameList = []
	for thisGlyph in thisFont.glyphs:
		thisScript = thisGlyph.script
		glyphName = thisGlyph.name
		nameIsOK = True
		
		if suffix:
			nameIsOK = glyphName.endswith(suffix)
		
		if nameIsOK and excludedGlyphNameParts:
			for thisNamePart in excludedGlyphNameParts:
				nameIsOK = nameIsOK and not thisNamePart in glyphName
		
		if nameIsOK and (thisGlyph.export or not excludeNonExporting):
				if thisScript == None or thisScript == requiredScript:
					if thisGlyph.category == requiredCategory:
						if requiredSubCategory:
							if thisGlyph.subCategory == requiredSubCategory:
								nameList.append( glyphName )
						else:
							nameList.append( glyphName )
	return nameList
	
def splitString( string, delimiter=":", minimum=2 ):
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

def measureLayerAtHeightFromLeftOrRight( thisLayer, height, leftSide=True ):
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

def isHeightInIntervals( height, ignoreIntervals ):
	if ignoreIntervals:
		for interval in ignoreIntervals:
			if height <= interval[1] and height >= interval[0]:
				return True
	return False

def minDistanceBetweenTwoLayers( leftLayer, rightLayer, interval=5.0, kerning=0.0, report=False, ignoreIntervals=[] ):
	# correction = leftLayer.RSB+rightLayer.LSB
	topY = min( leftLayer.bounds.origin.y+leftLayer.bounds.size.height, rightLayer.bounds.origin.y+rightLayer.bounds.size.height )
	bottomY = max( leftLayer.bounds.origin.y, rightLayer.bounds.origin.y )
	distance = topY - bottomY
	minDist = None
	for i in range(int(distance//interval)):
		height = bottomY + i * interval
		if not isHeightInIntervals(height, ignoreIntervals) or not ignoreIntervals:
			left = measureLayerAtHeightFromLeftOrRight( leftLayer, height, leftSide=False )
			right = measureLayerAtHeightFromLeftOrRight( rightLayer, height, leftSide=True )
			try: # avoid gaps like in i or j
				total = left+right+kerning # +correction
				if minDist == None or minDist > total:
					minDist = total
			except:
				pass
	return minDist

def sortedIntervalsFromString( intervals="" ):
	ignoreIntervals = []
	if intervals:
		for interval in intervals.split(","):
			if interval.find(":") != -1:
				interval = interval.strip()
				try:
					intervalTuple = tuple(sorted([
						int(interval.split(":")[0].strip()),
						int(interval.split(":")[1].strip()),
					]))
					ignoreIntervals.append(intervalTuple)
				except:
					print("Warning: could not convert '%s' into a number interval." % interval.strip())
					pass
			else:
				print("Warning: '%s' is not an interval (missing colon)" % interval.strip())

	return ignoreIntervals
