# MenuTitle: Build Symbols
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates an estimated glyph and draws an estimated sign in it. Does the same for bar and brokenbar, for which it respects standard stems and italic angle.
"""

# TODO: further abstraction of existing methods
# TODO: emptyset, currency, lozenge, product, summation, radical

from Foundation import NSPoint, NSRect, NSSize, NSAffineTransform
import vanilla
import math
from GlyphsApp import Glyphs, GSGlyph, GSPath, GSNode, GSAnchor, GSOFFCURVE, GSCURVE, GSSMOOTH, distance
from mekkablue import mekkaObject
from mekkablue.geometry import transform, italicize, offsetLayer


def scaleLayerByFactor(thisLayer, scaleFactor):
	"""
	Scales a layer by this factor.
	"""
	thisLayer.transform_checkForSelection_doComponents_(scaleMatrix(scaleFactor), False, True)


def scaleMatrix(scaleFactor):
	"""
	Returns a matrix for the scale factor,
	where 100% is represented as 1.0.
	"""
	scaleMatrix = (scaleFactor, 0.0, 0.0, scaleFactor, 0.0, 0.0)
	transformMatrix = transformFromMatrix(scaleMatrix)
	return transformMatrix


def transformFromMatrix(matrix):
	"""
	Returns an NSAffineTransform based on the matrix supplied.
	Matrix needs to be a tuple of 6 floats.
	"""
	transformation = NSAffineTransform.transform()
	transformation.setTransformStruct_(matrix)
	return transformation


def circleAtCenter(center=NSPoint(0, 0), radius=50, bcp=4.0 * (2.0**0.5 - 1.0) / 3.0):
	circle = GSPath()
	x = center.x
	y = center.y
	handle = radius * bcp
	points = (
		((x + handle, y - radius), (x + radius, y - handle), (x + radius, y)), ((x + radius, y + handle), (x + handle, y + radius), (x, y + radius)),
		((x - handle, y + radius), (x - radius, y + handle), (x - radius, y)), ((x - radius, y - handle), (x - handle, y - radius), (x, y - radius))
	)
	# Add the segments:
	for triplet in points:
		# Add the two BCPs of the segment:
		bcp1 = NSPoint(triplet[0][0], triplet[0][1])
		bcp2 = NSPoint(triplet[1][0], triplet[1][1])
		for bcpPosition in (bcp1, bcp2):
			newBCP = GSNode()
			newBCP.type = GSOFFCURVE
			newBCP.position = bcpPosition
			circle.nodes.append(newBCP)

		# Add the On-Curve of the segment:
		newCurvepoint = GSNode()
		newCurvepoint.type = GSCURVE
		newCurvepoint.smooth = True
		newCurvepoint.position = NSPoint(triplet[2][0], triplet[2][1])
		circle.nodes.append(newCurvepoint)

	circle.closed = True
	return circle


def circleInsideRect(rect):
	"""Returns a GSPath for a circle inscribed into the NSRect rect."""
	MAGICNUMBER = 4.0 * (2.0**0.5 - 1.0) / 3.0
	x = rect.origin.x
	y = rect.origin.y
	height = rect.size.height
	width = rect.size.width
	fullHeight = y + height
	fullWidth = x + width
	halfHeight = y + 0.5 * height
	halfWidth = x + 0.5 * width
	horHandle = width * 0.5 * MAGICNUMBER * 1.05
	verHandle = height * 0.5 * MAGICNUMBER * 1.05

	segments = (
		(NSPoint(x, halfHeight - verHandle), NSPoint(halfWidth - horHandle, y),
			NSPoint(halfWidth, y)), (NSPoint(halfWidth + horHandle, y), NSPoint(fullWidth, halfHeight - verHandle), NSPoint(fullWidth, halfHeight)),
		(NSPoint(fullWidth, halfHeight + verHandle), NSPoint(halfWidth + horHandle, fullHeight),
			NSPoint(halfWidth, fullHeight)), (NSPoint(halfWidth - horHandle, fullHeight), NSPoint(x, halfHeight + verHandle), NSPoint(x, halfHeight))
	)

	circlePath = GSPath()

	for thisSegment in segments:
		for i in range(3):
			nodeType = (GSOFFCURVE, GSOFFCURVE, GSCURVE)[i]
			nodePos = thisSegment[i]
			newNode = GSNode()
			newNode.position = nodePos
			newNode.type = nodeType
			newNode.connection = GSSMOOTH
			circlePath.nodes.append(newNode)

	# print(circlePath)
	# for n in circlePath.nodes:
	# 	print("   ", n)
	circlePath.closed = True
	return circlePath


def isEmpty(layer):
	try:
		# GLYPHS 3:
		if layer.shapes:
			return False
		else:
			return True
	except:
		# GLYPHS 2:
		if layer.paths:
			return False
		elif layer.components:
			return False
		else:
			return True


def createGlyph(font, name, unicodeValue, override=False, defaultWidth=500):
	glyph = font.glyphs[name]
	if not glyph:
		glyph = GSGlyph()
		glyph.name = name
		glyph.unicode = unicodeValue
		font.glyphs.append(glyph)
		glyph.updateGlyphInfo()
		return glyph
	else:
		if not override:
			print("Glyph %s already exists. No override chosen. Skipping." % name)
			return None

		else:
			print("Overwriting existing glyph %s." % name)

			# create backups of layers:
			if Glyphs.defaults["com.mekkablue.BuildSymbols.backupLayers"]:
				backupLayers = []
				for layer in glyph.layers:
					if layer.isMasterLayer or layer.isSpecialLayer:
						if isEmpty(layer):
							# nothing on layer? no backup needed:
							print("- Layer ‘%s’ is empty. No backup needed." % (layer.name if layer.name else "(empty)"))
						else:
							# create and collect backup layers:
							layerCopy = layer.copy()
							layerCopy.background = layer.copyDecomposedLayer()
							layerCopy.name = "Backup: %s" % layer.name
							backupLayers.append(layerCopy)
							print("- Creating backup of layer: %s" % (layer.name if layer.name else "(empty)"))

						layer.clear()
						layer.background.clear()
						layer.leftMetricsKey = None
						layer.rightMetricsKey = None
						layer.width = defaultWidth

				# add collected backup layers (after the loop)
				for backupLayer in backupLayers:
					glyph.layers.append(backupLayer)

			# remove special layers:
			for i in range(len(glyph.layers) - 1, -1, -1):
				layer = glyph.layers[i]
				if layer.isSpecialLayer:
					del glyph.layers[i]

			return glyph


def circleCoordsForHeight(s):
	radius = s / 2
	x = s / 2
	y = s / 2
	bcp = 4.0 * (2.0**0.5 - 1.0) / 3.0
	handle = radius * bcp
	coords = (
		(  # path
			(x, y - radius),
			((x + handle, y - radius), (x + radius, y - handle), (x + radius, y)),
			((x + radius, y + handle), (x + handle, y + radius), (x, y + radius)),
			((x - handle, y + radius), (x - radius, y + handle), (x - radius, y)),
			((x - radius, y - handle), (x - handle, y - radius), (x, y - radius)),
		),
	)
	return coords


def drawPenDataInLayer(thisLayer, penData, closePath=True):
	for thisPath in penData:
		pen = thisLayer.getPen()
		pen.moveTo(thisPath[0])
		for thisSegment in thisPath[1:]:
			if len(thisSegment) == 2:  # lineto (2 coordinates: x,y)
				pen.lineTo(thisSegment)
			elif len(thisSegment) == 3:  # curveto (3 x/y tuples)
				pen.curveTo(thisSegment[0], thisSegment[1], thisSegment[2])
			else:
				print("Path drawing error. Could not process this segment:\n" % thisSegment)
		if closePath:
			pen.closePath()
		pen.endPath()

	# clean up:
	# thisLayer.correctPathDirection()
	thisLayer.cleanUpPaths()


def areaOfLayer(layer):
	area = 0
	layerCopy = layer.copyDecomposedLayer()
	layerCopy.removeOverlap()
	try:
		# GLYPHS 3:
		for s in layerCopy.shapes:
			area += s.area()
	except:
		# GLYPHS 2:
		for p in layerCopy.paths:
			area += p.area()
	return area


def buildNotdef(thisFont, override=False):
	questionGlyph = thisFont.glyphs["question"]
	if not questionGlyph:
		print("⚠️ Error building .notdef: No question mark is available in your font. Cannot create .notdef.")
	else:
		name = ".notdef"
		notdefGlyph = createGlyph(thisFont, name, None, override=override)
		if notdefGlyph:
			sourceLayer = questionGlyph.layers[0]
			area = areaOfLayer(sourceLayer)
			for qLayer in questionGlyph.layers:
				if qLayer.isMasterLayer or qLayer.isSpecialLayer:
					qArea = areaOfLayer(qLayer)
					if qArea > area:
						sourceLayer = qLayer
						area = qArea

			if sourceLayer:
				# Build .notdef from question mark and circle:
				questionmarkLayer = sourceLayer.copyDecomposedLayer()
				scaleLayerByFactor(questionmarkLayer, 0.8)
				qOrigin = questionmarkLayer.fastBounds().origin
				qWidth = questionmarkLayer.fastBounds().size.width
				qHeight = questionmarkLayer.fastBounds().size.height
				qCenter = NSPoint(qOrigin.x + 0.5 * qWidth, qOrigin.y + 0.5 * qHeight)
				side = max((qWidth, qHeight)) * 1.5
				circleRect = NSRect(NSPoint(qCenter.x - 0.5 * side, qCenter.y - 0.5 * side), NSSize(side, side))
				circle = circleInsideRect(circleRect)
				try:
					# GLYPHS 3
					questionmarkLayer.shapes.append(circle)
				except:
					# GLYPHS 2
					questionmarkLayer.paths.append(circle)
				questionmarkLayer.correctPathDirection()

				# Create glyph:
				notdefGlyph.leftMetricsKey = "=40"
				notdefGlyph.rightMetricsKey = "=|"
				for masterID in [m.id for m in thisFont.masters]:
					notdefLayer = notdefGlyph.layers[masterID]
					for thisPath in questionmarkLayer.paths:
						try:
							# GLYPHS 3:
							notdefLayer.shapes.append(thisPath.copy())
						except:
							# GLYPHS 2:
							notdefLayer.paths.append(thisPath.copy())
					notdefLayer.syncMetrics()
			else:
				print("⚠️ Error building .notdef: Could not determine source layer of glyph 'question'.")


def buildLozenge(thisFont, override=False):
	glyphName = "lozenge"
	lozengeGlyph = createGlyph(thisFont, glyphName, "25CA", override=override)

	# set metrics keys and kern groups:
	lozengeGlyph.leftMetricsKey = "=50"
	lozengeGlyph.rightMetricsKey = "=|"
	lozengeGlyph.leftKerningGroup = glyphName
	lozengeGlyph.rightKerningGroup = glyphName

	for thisLayer in lozengeGlyph.layers:
		thisMaster = thisLayer.master
		capHeight = thisMaster.capHeight
		s = capHeight * 0.7  # 70% cap height

		penpoints_lozenge = (
			(  # fin
				(s * 0.3, s * 1.0),
				(s * 0.0, s * 0.5),
				(s * 0.3, s * 0.0),
				(s * 0.6, s * 0.5),
			),
		)

		# draw the skeleton:
		drawPenDataInLayer(thisLayer, penpoints_lozenge, closePath=True)

		# expand it:
		stemWidth = stemWidthForMaster(thisFont, thisMaster, maxWidth=s * 0.6 * 0.3)
		offsetLayer(thisLayer, stemWidth / 2, makeStroke=True, position=0.5)

		# move it into mid cap height:
		moveUp = (capHeight - s) * 0.5  # move to center of cap height
		moveUpStruct = transform(shiftY=moveUp).transformStruct()
		thisLayer.applyTransform(moveUpStruct)

		# update metrics:
		thisLayer.cleanUpPaths()
		thisLayer.syncMetrics()

		# cut off caps:
		midTop = sum([p.fastBounds().origin.y + p.fastBounds().size.height for p in thisLayer.paths]) / 2.0
		midBottom = sum([p.fastBounds().origin.y for p in thisLayer.paths]) / 2.0
		intersector = GSPath()
		coordinates = (
			(0, midBottom),
			(thisLayer.width, midBottom),
			(thisLayer.width, midTop),
			(0, midTop),
		)
		for coordinate in coordinates:
			intersector.nodes.append(GSNode(NSPoint(*coordinate)))
		intersector.closed = True

		if Glyphs.versionNumber >= 3:
			# GLYPHS 3
			thisLayer.shapes.append(intersector)
		else:
			# GLYPHS 2
			thisLayer.paths.append(intersector)

		thisLayer.pathIntersect_from_error_([intersector], [thisLayer.paths[0]], None)


def buildCurrency(thisFont, override=False):
	glyphName = "currency"
	currencyGlyph = createGlyph(thisFont, glyphName, "00A4", override=override)

	# set metrics keys and kern groups:
	currencyGlyph.leftMetricsKey = "=50"
	currencyGlyph.rightMetricsKey = "=|"
	currencyGlyph.leftKerningGroup = glyphName
	currencyGlyph.rightKerningGroup = glyphName

	for thisLayer in currencyGlyph.layers:
		thisMaster = thisLayer.master
		capHeight = thisMaster.capHeight
		s = capHeight * 0.6  # 60% cap height

		penpoints_currency = (
			(  # circle
				(s * 0.500, s * 0.173),
				((s * 0.680, s * 0.173), (s * 0.827, s * 0.320), (s * 0.827, s * 0.500)),
				((s * 0.827, s * 0.680), (s * 0.680, s * 0.827), (s * 0.500, s * 0.827)),
				((s * 0.320, s * 0.827), (s * 0.173, s * 0.680), (s * 0.173, s * 0.500)),
				((s * 0.173, s * 0.320), (s * 0.320, s * 0.173), (s * 0.500, s * 0.173)),
			),
			(  # fin
				(s * 1.000, s * 1.000), (s * 0.741, s * 0.741),
			),
			(  # fin
				(s * 0.000, s * 0.000), (s * 0.259, s * 0.259),
			),
			(  # fin
				(s * 0.000, s * 1.000), (s * 0.259, s * 0.741),
			),
			(  # fin
				(s * 1.000, s * 0.000), (s * 0.741, s * 0.259),
			),
		)

		# draw the skeleton:
		drawPenDataInLayer(thisLayer, penpoints_currency, closePath=False)

		# expand it:
		stemWidth = stemWidthForMaster(thisFont, thisMaster, maxWidth=s * 0.5 * 0.3)
		offsetLayer(thisLayer, stemWidth / 2, makeStroke=True, position=0.5)

		# move it into mid cap height:
		moveUp = (capHeight - s) * 0.5  # move to center of cap height
		moveUpStruct = transform(shiftY=moveUp).transformStruct()
		thisLayer.applyTransform(moveUpStruct)

		# update metrics:
		thisLayer.cleanUpPaths()
		thisLayer.syncMetrics()


def buildEstimated(thisFont, override=False):
	glyphname = "estimated"
	estimatedGlyph = createGlyph(thisFont, glyphname, "212E", override=override)

	penpoints_estimated = (
		(
			(416.0, -5.0), ((557.0, -5.0), (635.0, 33.0), (724.0, 131.0)), (654.0, 131.0), ((600.0, 70.0), (511.0, 22.0), (416.0, 22.0)),
			((274.0, 22.0), (179.0, 108.0), (179.0, 143.0)), (179.0, 311.0), ((179.0, 328.0), (185.0, 329.0), (194.0, 329.0)), (792.0, 329.0),
			((782.0, 557.0), (638.0, 682.0), (416.0, 682.0)), ((196.0, 682.0), (40.0, 544.0), (40.0, 338.0)), ((40.0, 129.0), (196.0, -5.0), (416.0, -5.0))
		),
		(
			(194.0, 350.0), ((183.0, 350.0), (179.0, 353.0), (179.0, 359.0)), (179.0, 538.0), ((179.0, 568.0), (280.0, 658.0), (415.0, 658.0)),
			((522.0, 658.0), (652.0, 585.0), (652.0, 531.0)), (652.0, 366.0), ((652.0, 354.0), (650.0, 350.0), (636.0, 350.0)), (194.0, 350.0)
		)
	)

	if estimatedGlyph:
		# set metrics keys and kern groups:
		estimatedGlyph.leftMetricsKey = "=40"
		estimatedGlyph.rightMetricsKey = "=|"
		estimatedGlyph.leftKerningGroup = "estimated"
		estimatedGlyph.rightKerningGroup = "estimated"

		# find zero:
		zeroGlyph = thisFont.glyphs["zero.lf"]
		if not zeroGlyph:
			zeroGlyph = thisFont.glyphs["zero.tf"]
			if not zeroGlyph:
				zeroGlyph = thisFont.glyphs["zero"]

		# draw in every layer:
		for thisLayer in estimatedGlyph.layers:
			if thisLayer.isMasterLayer:
				for thisPath in penpoints_estimated:
					pen = thisLayer.getPen()
					pen.moveTo(thisPath[0])
					for thisSegment in thisPath[1:]:
						if len(thisSegment) == 2:  # lineto
							pen.lineTo(thisSegment)
						elif len(thisSegment) == 3:  # curveto
							pen.curveTo(thisSegment[0], thisSegment[1], thisSegment[2])
						else:
							print("%s: Path drawing error. Could not process this segment: %s\n" % (glyphname, thisSegment))
					pen.closePath()
					pen.endPath()

				# scale estimated to match zero:
				if zeroGlyph:
					zeroBounds = zeroGlyph.layers[thisLayer.associatedMasterId].fastBounds()
					zeroHeight = zeroBounds.size.height
					if zeroHeight:  # zero could be empty
						zeroOvershoot = -zeroBounds.origin.y
						overshootDiff = zeroOvershoot - 5.0
						estimatedHeight = 687.0
						correctedEstimatedHeight = zeroHeight - 2 * overshootDiff
						if correctedEstimatedHeight != estimatedHeight:
							scaleFactor = correctedEstimatedHeight / estimatedHeight
							estimatedCorrection = transform(shiftY=5.0)
							estimatedCorrection.appendTransform_(transform(scale=scaleFactor))
							estimatedCorrection.appendTransform_(transform(-5.0))
							thisLayer.applyTransform(estimatedCorrection.transformStruct())

				# tidy up paths and set width:
				thisLayer.cleanUpPaths()
				thisLayer.syncMetrics()
				print("✅ Created estimated in master '%s'" % thisLayer.associatedFontMaster().name)

	else:
		print("⚠️ Could not create the estimated glyph already exists in this font. Rename or delete it and try again.")


def stemWidthForMaster(thisFont, thisMaster, default=50, maxWidth=None):
	try:
		slash = thisFont.glyphs["slash"].layers[thisMaster.id]
		slashLeft = slash.fastBounds().origin.x
		slashRight = slashLeft + slash.fastBounds().size.width
		slashBottom = slash.fastBounds().origin.x
		slashTop = slashLeft + slash.fastBounds().size.width
		middleHeight = (slashBottom + slashTop) / 2
		measureStart = NSPoint(slashLeft, middleHeight)
		measureEnd = NSPoint(slashRight, middleHeight)
		intersections = list(slash.intersectionsBetweenPoints(measureStart, measureEnd))
		slashStemWidth = distance(intersections[1].pointValue(), intersections[2].pointValue())  # hypotenuse
		angleRAD = math.atan((slashTop - slashBottom) / (slashRight - slashLeft))
		width = ((slashStemWidth * math.cos(angleRAD)) + slashStemWidth) * 0.5

		# compare with maxWidth:
		if maxWidth and maxWidth > 2:
			width = min(width, maxWidth)

		return width
	except:
		print("⚠️ Error measuring slash, will try Master stem width instead.")
		try:
			return thisMaster.verticalStems[0] * 0.8
		except:
			print("⚠️ Error building bars: No vertical stems set in Master '%s'. Will default to %i." % (thisMaster.name, default))
	return default


def buildDottedCircle(thisFont, override=False):
	dottedCircle = createGlyph(thisFont, "dottedCircle", "25CC", override=override)
	if dottedCircle:
		dottedCircle.leftMetricsKey = "=50"
		dottedCircle.rightMetricsKey = "=|"
		maxRad = 2 * math.pi
		steps = 12
		for thisLayer in dottedCircle.layers:
			if thisLayer.isMasterLayer:
				thisLayer.shapes = None
				factor = thisLayer.ascender * 0.74 / 2
				for i in range(steps):
					angle = i * maxRad / steps
					x = math.sin(angle)
					y = math.cos(angle)
					path = circleAtCenter(
						center=NSPoint(factor * x, factor * y + thisLayer.ascender / 2),
						radius=2 * factor / steps,
						bcp=0.58,
					)
					thisLayer.shapes.append(path)

				# update metrics:
				thisLayer.cleanUpPaths()
				thisLayer.syncMetrics()

				for anchorName in ("top", "bottom"):
					x = thisLayer.width / 2
					y = 0.0 if anchorName == "bottom" else thisLayer.ascender
					thisAnchor = GSAnchor()
					thisAnchor.name = anchorName
					thisAnchor.position = NSPoint(x, y)
					thisLayer.anchors.append(thisAnchor)


def buildBars(thisFont, override=False):
	barGlyph = createGlyph(thisFont, "bar", "007C", override=override)
	brokenbarGlyph = createGlyph(thisFont, "brokenbar", "00A6", override=override)

	slashGlyph = thisFont.glyphs["slash"]

	if barGlyph or brokenbarGlyph:
		for thisMaster in thisFont.masters:
			goodMeasure = (thisMaster.ascender - thisMaster.descender) * 0.2
			descender = round(thisMaster.descender - goodMeasure)
			ascender = round(thisMaster.ascender + goodMeasure)
			mID = thisMaster.id
			italicAngle = thisMaster.italicAngle
			pivot = thisMaster.xHeight * 0.5
			stemWidth = stemWidthForMaster(thisFont, thisMaster)
			stemWidth -= stemWidth * math.cos(math.radians(italicAngle)) - stemWidth  # correct for italic angle

			if slashGlyph:
				slashLayer = slashGlyph.layers[thisMaster.id]
				if slashLayer.fastBounds().size.height > 0:
					descender = slashLayer.fastBounds().origin.y
					ascender = descender + slashLayer.fastBounds().size.height
					middle = (descender + ascender) * 0.5
					suggestedStemWidth = slashLayer.width - slashLayer.rsbAtHeight_(middle) - slashLayer.lsbAtHeight_(middle)
					if suggestedStemWidth > 0:
						stemWidth = int(suggestedStemWidth * 0.96)

			sidebearing = max((350 - stemWidth) * 0.5, 60.0)
			gap = max(250 - stemWidth, 120.0)

			bottomLeft = italicize((sidebearing, descender), italicAngle=italicAngle, pivotalY=pivot)
			bottomRight = italicize((sidebearing + stemWidth, descender), italicAngle=italicAngle, pivotalY=pivot)
			topRight = italicize((sidebearing + stemWidth, ascender), italicAngle=italicAngle, pivotalY=pivot)
			topLeft = italicize((sidebearing, ascender), italicAngle=italicAngle, pivotalY=pivot)

			if barGlyph:
				barLayer = barGlyph.layers[mID]
				pen = barLayer.getPen()
				pen.moveTo(bottomLeft)
				pen.lineTo(bottomRight)
				pen.lineTo(topRight)
				pen.lineTo(topLeft)
				pen.closePath()
				pen.endPath()
				barLayer.RSB = sidebearing
				barGlyph.rightMetricsKey = "=|"
				barGlyph.leftKerningGroup = "bar"
				barGlyph.rightKerningGroup = "bar"
				print("✅ Created bar in master '%s'" % thisMaster.name)

			if brokenbarGlyph:
				gapBottomY = ((ascender + descender) - gap) * 0.5
				gapTopY = ((ascender + descender) + gap) * 0.5
				gapBottomRight = italicize((sidebearing + stemWidth, gapBottomY), italicAngle=italicAngle, pivotalY=pivot)
				gapBottomLeft = italicize((sidebearing, gapBottomY), italicAngle=italicAngle, pivotalY=pivot)
				gapTopRight = italicize((sidebearing + stemWidth, gapTopY), italicAngle=italicAngle, pivotalY=pivot)
				gapTopLeft = italicize((sidebearing, gapTopY), italicAngle=italicAngle, pivotalY=pivot)

				brokenbarLayer = brokenbarGlyph.layers[mID]
				pen = brokenbarLayer.getPen()
				pen.moveTo(bottomLeft)
				pen.lineTo(bottomRight)
				pen.lineTo(gapBottomRight)
				pen.lineTo(gapBottomLeft)
				pen.closePath()
				pen.endPath()

				brokenbarLayer = brokenbarGlyph.layers[mID]
				pen = brokenbarLayer.getPen()
				pen.moveTo(gapTopLeft)
				pen.lineTo(gapTopRight)
				pen.lineTo(topRight)
				pen.lineTo(topLeft)
				pen.closePath()
				pen.endPath()

				brokenbarLayer.RSB = sidebearing
				brokenbarGlyph.leftMetricsKey = "=bar"
				brokenbarGlyph.rightMetricsKey = "=|"
				brokenbarGlyph.leftKerningGroup = "bar"
				brokenbarGlyph.rightKerningGroup = "bar"
				print("✅ Created brokenbar in master '%s'" % thisMaster.name)
	else:
		print("⚠️ The glyphs bar and brokenbar already exist in this font. Rename or delete them and try again.")


class BuildSymbols(mekkaObject):
	prefDict = {
		"buildEstimated": 1,
		"buildBars": 1,
		"buildEmptyset": 1,
		"buildCurrency": 1,
		"buildLozenge": 1,
		"buildProduct": 1,
		"buildSummation": 1,
		"buildRadical": 1,
		"buildNotdef": 1,
		"buildDottedcircle": 1,
		"override": 0,
		"backupLayers": 0,
		"newTab": 0,
		"reuseTab": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 430
		windowHeight = 230
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Build Symbols",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight, column = 12, 15, 22, 100

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Create the following symbols automatically. See tooltips for requirements.", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.buildEstimated = vanilla.CheckBox((inset, linePos, -inset, 20), "estimated", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildEstimated.getNSButton().setToolTip_("Will build estimated ℮ and scale it to the size of your lining zero, if available.")

		self.w.buildBars = vanilla.CheckBox((inset + column, linePos, -inset, 20), "bar, brokenbar", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildBars.getNSButton().setToolTip_("Will model bar | and brokenbar ¦ after your slash /, or if there is no slash, use the master’s stem values for their size.")

		self.w.buildEmptyset = vanilla.CheckBox((inset + int(column * 2.1), linePos, -inset, 20), "emptyset", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildEmptyset.getNSButton().setToolTip_("Will build emptyset. Not yet implemented, sorry.")
		self.w.buildEmptyset.enable(False)

		self.w.buildDottedcircle = vanilla.CheckBox((inset + column * 3, linePos, -inset, 20), "dottedCircle", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildDottedcircle.getNSButton().setToolTip_("Will build dottedCircle ◌.")
		linePos += lineHeight

		self.w.buildCurrency = vanilla.CheckBox((inset, linePos, -inset, 20), "currency", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildCurrency.getNSButton().setToolTip_("Will build currency.")

		self.w.buildLozenge = vanilla.CheckBox((inset + column, linePos, -inset, 20), "lozenge", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildLozenge.getNSButton().setToolTip_("Will build lozenge.")

		self.w.buildProduct = vanilla.CheckBox((inset + int(column * 2.1), linePos, -inset, 20), "product", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildProduct.getNSButton().setToolTip_("Will build product. Not yet implemented, sorry.")
		self.w.buildProduct.enable(False)
		linePos += lineHeight

		self.w.buildSummation = vanilla.CheckBox((inset, linePos, -inset, 20), "summation", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildSummation.getNSButton().setToolTip_("Will build summation. Not yet implemented, sorry.")
		self.w.buildSummation.enable(False)

		self.w.buildRadical = vanilla.CheckBox((inset + column, linePos, -inset, 20), "radical", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildRadical.getNSButton().setToolTip_("Will build radical. Not yet implemented, sorry.")
		self.w.buildRadical.enable(False)

		self.w.buildNotdef = vanilla.CheckBox((inset + int(column * 2.1), linePos, -inset, 20), ".notdef", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildNotdef.getNSButton().setToolTip_("Will build the mandatory .notdef glyph based on the boldest available question mark.")
		linePos += lineHeight

		# ----------- SEPARATOR LINE -----------
		self.w.line = vanilla.HorizontalLine((inset, int(linePos + 0.5 * lineHeight - 1), -inset, 1))
		linePos += lineHeight

		# Other options:
		self.w.override = vanilla.CheckBox((inset, linePos, -inset, 20), "Overwrite existing glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.override.getNSButton().setToolTip_("If checked, will create fresh symbols even if they already exist. If unchecked, will skip glyphs that already exist.")
		self.w.backupLayers = vanilla.CheckBox((inset + 180, linePos, -inset, 20), "Backup existing layers", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.backupLayers.getNSButton().setToolTip_("If checked, will create backup layers when the glyph gets overwritten. Only available in combination with Override option.")
		linePos += lineHeight

		self.w.newTab = vanilla.CheckBox((inset, linePos - 1, 180, 20), "Open tab with new glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.newTab.getNSButton().setToolTip_("If checked, will open a new tab with the newly created symbols.")
		self.w.reuseTab = vanilla.CheckBox((inset + 180, linePos - 1, -inset, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.getNSButton().setToolTip_("If checked, will reuse the current tab, and open a new tab only if there is no Edit tab open already. Highly recommended.")
		linePos += lineHeight

		# Run Button:
		self.w.uncheckAllButton = vanilla.Button((-315 - inset, -20 - inset, -200 - inset, -inset), "Uncheck All", callback=self.checkAll)
		self.w.checkAllButton = vanilla.Button((-190 - inset, -20 - inset, -90 - inset, -inset), "Check All", callback=self.checkAll)
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Build", callback=self.BuildSymbolsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		# Allow "Reuse Tab" only if "Open Tab" is on:
		self.w.reuseTab.enable(self.w.newTab.get())
		self.w.backupLayers.enable(self.w.override.get())

	def checkAll(self, sender=None, onOrOff=True):
		if sender is self.w.uncheckAllButton:
			onOrOff = False
		Glyphs.defaults[self.domain("buildEstimated")] = onOrOff
		Glyphs.defaults[self.domain("buildBars")] = onOrOff
		Glyphs.defaults[self.domain("buildEmptyset")] = False  # onOrOff
		Glyphs.defaults[self.domain("buildCurrency")] = onOrOff
		Glyphs.defaults[self.domain("buildLozenge")] = onOrOff
		Glyphs.defaults[self.domain("buildProduct")] = False  # onOrOff
		Glyphs.defaults[self.domain("buildSummation")] = False  # onOrOff
		Glyphs.defaults[self.domain("buildRadical")] = False  # onOrOff
		Glyphs.defaults[self.domain("buildNotdef")] = onOrOff
		Glyphs.defaults[self.domain("buildDottedcircle")] = onOrOff
		self.LoadPreferences()

	def BuildSymbolsMain(self, sender):
		try:
			Glyphs.clearLog()  # clears macro window log

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			print("Build Symbols Report for %s" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
			else:
				print("⚠️ File not yet saved.")
			print()

			# retrieve user settings:
			override = self.pref("override")
			newTab = self.pref("newTab")
			reuseTab = self.pref("reuseTab")

			tabText = ""

			# build glyphs:
			if self.pref("buildEstimated"):
				print("\n🔣 Building estimated:")
				buildEstimated(thisFont, override=override)
				tabText += "/estimated"

			if self.pref("buildBars"):
				print("\n🔣 Building bars:")
				buildBars(thisFont, override=override)
				tabText += "/bar/brokenbar"

			if self.pref("buildEmptyset"):
				print("\n🔣 Building emptyset:")
				print("😢 Not yet implemented, sorry.")
				pass

			if self.pref("buildCurrency"):
				print("\n🔣 Building currency:")
				buildCurrency(thisFont, override=override)
				tabText += "/currency"

			if self.pref("buildLozenge"):
				print("\n🔣 Building lozenge:")
				buildLozenge(thisFont, override=override)
				tabText += "/lozenge"

			if self.pref("buildProduct"):
				print("\n🔣 Building product:")
				print("😢 Not yet implemented, sorry.")
				pass

			if self.pref("buildSummation"):
				print("\n🔣 Building summation:")
				print("😢 Not yet implemented, sorry.")
				pass

			if self.pref("buildRadical"):
				print("\n🔣 Building radical:")
				print("😢 Not yet implemented, sorry.")
				pass

			if self.pref("buildNotdef"):
				print("\n🔣 Building notdef:")
				buildNotdef(thisFont, override=override)
				tabText += "/.notdef"

			if self.pref("buildDottedcircle"):
				print("\n🔣 Building dottedCircle:")
				buildDottedCircle(thisFont, override=override)
				tabText += "/dottedCircle"

			# Floating notification:
			Glyphs.showNotification(
				"%s: symbols built" % (thisFont.familyName),
				"Script ‘Build Symbols’ is finished.",
			)

			if newTab and tabText:
				if reuseTab and thisFont.currentTab:
					# reuses current tab:
					thisFont.currentTab.text = tabText
				else:
					# opens new Edit tab:
					thisFont.newTab(tabText)

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Build Symbols Error: %s" % e)
			import traceback
			print(traceback.format_exc())


BuildSymbols()
