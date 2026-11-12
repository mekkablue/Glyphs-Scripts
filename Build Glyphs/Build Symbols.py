# MenuTitle: Build Symbols
__doc__ = """
Creates an estimated glyph and draws an estimated sign in it. Does the same for bar and brokenbar, for which it respects standard stems and italic angle, and for emptyset, dottedCircle, currency, lozenge and .notdef.
"""

# TODO: further abstraction of existing methods
# TODO: product, summation, radical

from Foundation import NSPoint, NSRect, NSSize, NSAffineTransform
import vanilla
import math
import traceback
from GlyphsApp import Glyphs, GSGlyph, GSPath, GSNode, GSAnchor, GSOFFCURVE, GSCURVE, GSLINE, GSSMOOTH, distance
from mekkablue import mekkaObject
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
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

	circlePath.closed = True
	return circlePath


def isEmpty(layer):
	return not layer.shapes


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

			# create backups of layers (if wanted), and clear them:
			backupLayers = []
			makeBackups = Glyphs.defaults["com.mekkablue.BuildSymbols.backupLayers"]
			for layer in glyph.layers:
				if layer.isMasterLayer or layer.isSpecialLayer:
					if makeBackups:
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
				print("Path drawing error. Could not process this segment: %s\n" % thisSegment)
		if closePath:
			pen.closePath()
		pen.endPath()

	# clean up:
	thisLayer.cleanUpPaths()


def areaOfLayer(layer):
	area = 0
	layerCopy = layer.copyDecomposedLayer()
	layerCopy.removeOverlap()
	for shape in layerCopy.shapes:
		area += shape.area()
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

			# Build .notdef from question mark and circle:
			questionmarkLayer = sourceLayer.copyDecomposedLayer()
			scaleLayerByFactor(questionmarkLayer, 0.8)
			qBounds = questionmarkLayer.fastBounds()
			qOrigin = qBounds.origin
			qWidth = qBounds.size.width
			qHeight = qBounds.size.height
			qCenter = NSPoint(qOrigin.x + 0.5 * qWidth, qOrigin.y + 0.5 * qHeight)
			side = max((qWidth, qHeight)) * 1.5
			circleRect = NSRect(NSPoint(qCenter.x - 0.5 * side, qCenter.y - 0.5 * side), NSSize(side, side))
			circle = circleInsideRect(circleRect)
			questionmarkLayer.shapes.append(circle)
			questionmarkLayer.correctPathDirection()

			# Create glyph:
			notdefGlyph.leftMetricsKey = "=40"
			notdefGlyph.rightMetricsKey = "=|"
			for masterID in [m.id for m in thisFont.masters]:
				notdefLayer = notdefGlyph.layers[masterID]
				for thisPath in questionmarkLayer.paths:
					notdefLayer.shapes.append(thisPath.copy())
				notdefLayer.syncMetrics()


def buildLozenge(thisFont, override=False):
	glyphName = "lozenge"
	lozengeGlyph = createGlyph(thisFont, glyphName, "25CA", override=override)
	if not lozengeGlyph:
		return

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

		thisLayer.shapes.append(intersector)

		thisLayer.pathIntersect_from_error_([intersector], [thisLayer.paths[0]], None)
		thisLayer.syncMetrics()  # the outline changed after the first sync


def buildCurrency(thisFont, override=False):
	glyphName = "currency"
	currencyGlyph = createGlyph(thisFont, glyphName, "00A4", override=override)
	if not currencyGlyph:
		return

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
							estimatedCorrection.appendTransform_(transform(shiftY=-5.0))
							thisLayer.applyTransform(estimatedCorrection.transformStruct())

				# tidy up paths and set width:
				thisLayer.cleanUpPaths()
				thisLayer.syncMetrics()
				print("✅ Created estimated in master '%s'" % thisLayer.associatedFontMaster().name)

	else:
		print("⚠️ Could not create estimated, because the glyph already exists in this font. Rename or delete it and try again.")


def stemWidthForMaster(thisFont, thisMaster, default=50, maxWidth=None):
	try:
		slash = thisFont.glyphs["slash"].layers[thisMaster.id]
		slashLeft = slash.fastBounds().origin.x
		slashRight = slashLeft + slash.fastBounds().size.width
		slashBottom = slash.fastBounds().origin.y
		slashTop = slashBottom + slash.fastBounds().size.height
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
			print("⚠️ Error measuring stem width: No vertical stems set in Master '%s'. Will default to %i." % (thisMaster.name, default))
	return default


def barStemWidthForMaster(thisFont, thisMaster):
	"""Stem thickness for bar and brokenbar (and emptyset): measured on the slash if there is one, else from the master stems."""
	stemWidth = stemWidthForMaster(thisFont, thisMaster)
	stemWidth -= stemWidth * math.cos(math.radians(thisMaster.italicAngle)) - stemWidth  # correct for italic angle

	slashGlyph = thisFont.glyphs["slash"]
	if slashGlyph:
		slashLayer = slashGlyph.layers[thisMaster.id]
		slashBounds = slashLayer.fastBounds()
		if slashBounds.size.height > 0:
			middle = slashBounds.origin.y + slashBounds.size.height * 0.5
			suggestedStemWidth = slashLayer.width - slashLayer.rsbAtHeight_(middle) - slashLayer.lsbAtHeight_(middle)
			if suggestedStemWidth > 0:
				stemWidth = int(suggestedStemWidth * 0.96)
	return stemWidth


def buildEmptyset(thisFont, override=False):
	emptysetGlyph = createGlyph(thisFont, "emptyset", "2205", override=override)
	if not emptysetGlyph:
		return

	emptysetGlyph.leftMetricsKey = "=50"
	emptysetGlyph.rightMetricsKey = "=|"

	# find a zero for measuring the overshoot:
	zeroGlyph = None
	for zeroName in ("zero.lf", "zero.tf", "zero"):
		if thisFont.glyphs[zeroName]:
			zeroGlyph = thisFont.glyphs[zeroName]
			break

	diagonalFactor = 2.0**0.5  # diagonal of a square bounding box, in units of its side
	for thisMaster in thisFont.masters:
		thisLayer = emptysetGlyph.layers[thisMaster.id]
		thisLayer.clear()

		# height: average of x-height and cap height, plus overshoot at bottom and top:
		overshoot = 5.0
		if zeroGlyph:
			zeroBounds = zeroGlyph.layers[thisMaster.id].bounds
			if zeroBounds is not None and zeroBounds.size.height > 0:
				overshoot = abs(min(-5.0, zeroBounds.origin.y))
		baseHeight = (thisMaster.xHeight + thisMaster.capHeight) * 0.5
		height = baseHeight + 2 * overshoot
		radius = height * 0.5
		center = NSPoint(radius, baseHeight * 0.5)

		# stem thickness as for bar and brokenbar, but at most 18% of the height:
		stemWidth = min(barStemWidthForMaster(thisFont, thisMaster), height * 0.18)

		# circle with 57% handles; the stroke grows only inward.
		# Outer circle runs counterclockwise, inner circle clockwise (counter):
		thisLayer.shapes.append(circleAtCenter(center=center, radius=radius, bcp=0.57))
		innerCircle = circleAtCenter(center=center, radius=radius - stemWidth, bcp=0.57)
		innerCircle.reverse()
		thisLayer.shapes.append(innerCircle)

		# slash at 45° through the center of the circle, with the same thickness (counterclockwise,
		# overlapping the circle on purpose, so no overlaps are removed):
		slashLength = (height + 2 * height * diagonalFactor) / 3.0
		halfLength = slashLength * 0.5
		halfWidth = stemWidth * 0.5
		slash = GSPath()
		for lengthSign, widthSign in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
			along = lengthSign * halfLength
			across = widthSign * halfWidth
			x = center.x + (along - across) / diagonalFactor
			y = center.y + (along + across) / diagonalFactor
			node = GSNode()
			node.type = GSLINE
			node.position = NSPoint(x, y)
			slash.nodes.append(node)
		slash.closed = True
		thisLayer.shapes.append(slash)

		thisLayer.syncMetrics()
		print(f"✅ Created emptyset in master '{thisMaster.name}'")


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

				anchors_to_add = ["top", "bottom"]
				if thisFont.glyphs["ogonekcomb"]:
					anchors_to_add.append("ogonekcomb")

				for anchorName in anchors_to_add:
					x = thisLayer.width / 2
					y = thisLayer.ascender if anchorName == "top" else 0.0
					thisAnchor = GSAnchor()
					thisAnchor.name = anchorName
					thisAnchor.position = NSPoint(x, y)
					thisLayer.anchors.append(thisAnchor)


def buildBars(thisFont, override=False):
	barGlyph = createGlyph(thisFont, "bar", "007C", override=override)
	brokenbarGlyph = createGlyph(thisFont, "brokenbar", "00A6", override=override)

	slashGlyph = thisFont.glyphs["slash"]

	if barGlyph or brokenbarGlyph:
		# default vertical extent: from the lowest descender to the highest ascender of all masters
		lowestDescender = min(thisMaster.descender for thisMaster in thisFont.masters)
		highestAscender = max(thisMaster.ascender for thisMaster in thisFont.masters)
		for thisMaster in thisFont.masters:
			descender = lowestDescender
			ascender = highestAscender
			mID = thisMaster.id
			italicAngle = thisMaster.italicAngle
			pivot = thisMaster.xHeight * 0.5
			stemWidth = barStemWidthForMaster(thisFont, thisMaster)

			if slashGlyph:
				slashLayer = slashGlyph.layers[thisMaster.id]
				if slashLayer.fastBounds().size.height > 0:
					descender = slashLayer.fastBounds().origin.y
					ascender = descender + slashLayer.fastBounds().size.height

			sidebearing = max((350 - stemWidth) * 0.5, 60.0)
			gap = max(250 - stemWidth, 120.0)

			bottomLeft = italicize(NSPoint(sidebearing, descender), italicAngle=italicAngle, pivotalY=pivot)
			bottomRight = italicize(NSPoint(sidebearing + stemWidth, descender), italicAngle=italicAngle, pivotalY=pivot)
			topRight = italicize(NSPoint(sidebearing + stemWidth, ascender), italicAngle=italicAngle, pivotalY=pivot)
			topLeft = italicize(NSPoint(sidebearing, ascender), italicAngle=italicAngle, pivotalY=pivot)

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
				barLayer.syncMetrics()
				print("✅ Created bar in master '%s'" % thisMaster.name)

			if brokenbarGlyph:
				gapBottomY = ((ascender + descender) - gap) * 0.5
				gapTopY = ((ascender + descender) + gap) * 0.5
				gapBottomRight = italicize(NSPoint(sidebearing + stemWidth, gapBottomY), italicAngle=italicAngle, pivotalY=pivot)
				gapBottomLeft = italicize(NSPoint(sidebearing, gapBottomY), italicAngle=italicAngle, pivotalY=pivot)
				gapTopRight = italicize(NSPoint(sidebearing + stemWidth, gapTopY), italicAngle=italicAngle, pivotalY=pivot)
				gapTopLeft = italicize(NSPoint(sidebearing, gapTopY), italicAngle=italicAngle, pivotalY=pivot)

				brokenbarLayer = brokenbarGlyph.layers[mID]
				pen = brokenbarLayer.getPen()
				pen.moveTo(bottomLeft)
				pen.lineTo(bottomRight)
				pen.lineTo(gapBottomRight)
				pen.lineTo(gapBottomLeft)
				pen.closePath()
				pen.endPath()

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
				brokenbarLayer.syncMetrics()
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
		windowWidth = 434
		windowHeight = 1  # Auto Layout grows the window to the required size
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Build Symbols",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:

		self.w.descriptionText = vanilla.TextBox("auto", "Create the following symbols automatically. See tooltips for requirements.", sizeStyle='small', selectable=True)

		self.w.buildEstimated = vanilla.CheckBox("auto", "estimated ℮", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildEstimated.setToolTip("Will build estimated ℮ and scale it to the size of your lining zero, if available.")

		self.w.buildBars = vanilla.CheckBox("auto", "bar | brokenbar ¦", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildBars.setToolTip("Will model bar | and brokenbar ¦ after your slash /, or if there is no slash, use the master’s stem values for their width. Without a slash, they extend from the lowest descender to the highest ascender of all masters.")

		self.w.buildEmptyset = vanilla.CheckBox("auto", "emptyset ∅", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildEmptyset.setToolTip("Will build emptyset ∅: a circle with a slash, with the stem thickness of bar and brokenbar (but at most 18% of the height). Its height is the average of x-height and cap height plus the overshoot of your zero.")

		self.w.buildDottedcircle = vanilla.CheckBox("auto", "dottedCircle ◌", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildDottedcircle.setToolTip("Will build dottedCircle ◌.")

		self.w.buildCurrency = vanilla.CheckBox("auto", "currency ¤", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildCurrency.setToolTip("Will build currency.")

		self.w.buildLozenge = vanilla.CheckBox("auto", "lozenge ◊", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildLozenge.setToolTip("Will build lozenge.")

		self.w.buildProduct = vanilla.CheckBox("auto", "product ∏", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildProduct.setToolTip("Will build product. Not yet implemented, sorry.")
		self.w.buildProduct.enable(False)

		self.w.buildSummation = vanilla.CheckBox("auto", "summation ∑", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildSummation.setToolTip("Will build summation. Not yet implemented, sorry.")
		self.w.buildSummation.enable(False)

		self.w.buildRadical = vanilla.CheckBox("auto", "radical √", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildRadical.setToolTip("Will build radical. Not yet implemented, sorry.")
		self.w.buildRadical.enable(False)

		self.w.buildNotdef = vanilla.CheckBox("auto", ".notdef", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildNotdef.setToolTip("Will build the mandatory .notdef glyph based on the boldest available question mark.")

		# ----------- SEPARATOR LINE -----------
		self.w.line = vanilla.HorizontalLine("auto")

		# Other options:
		self.w.override = vanilla.CheckBox("auto", "Overwrite existing glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.override.setToolTip("If checked, will create fresh symbols even if they already exist. If unchecked, will skip glyphs that already exist.")
		self.w.backupLayers = vanilla.CheckBox("auto", "Backup existing layers", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.backupLayers.setToolTip("If checked, will create backup layers when the glyph gets overwritten. Only available in combination with ‘Overwrite existing glyphs’.")

		self.w.newTab = vanilla.CheckBox("auto", "Open tab with new glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.newTab.setToolTip("If checked, will open a new tab with the newly created symbols.")
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.setToolTip("If checked, will reuse the current tab, and open a new tab only if there is no Edit tab open already. Highly recommended.")

		# Run Button:
		self.w.uncheckAllButton = vanilla.Button("auto", "Uncheck All", callback=self.checkAll)
		self.w.checkAllButton = vanilla.Button("auto", "Check All", callback=self.checkAll)
		self.w.uncheckAllButton.setToolTip("Unchecks all symbols.")
		self.w.checkAllButton.setToolTip("Checks all symbols that can be built.")
		self.w.runButton = vanilla.Button("auto", "Build", callback=self.BuildSymbolsMain)
		self.w.runButton.setToolTip("Builds the checked symbols in the frontmost font.")
		self.w.setDefaultButton(self.w.runButton)

		# one shared width per grid column, so the checkboxes line up across the rows:
		gridCheckBoxes = (
			self.w.buildEstimated, self.w.buildBars, self.w.buildEmptyset, self.w.buildDottedcircle,
			self.w.buildCurrency, self.w.buildLozenge, self.w.buildProduct,
			self.w.buildSummation, self.w.buildRadical, self.w.buildNotdef,
		)
		columnRules = [
			{"view1": cell, "attribute1": "width", "view2": gridCheckBoxes[0], "attribute2": "width"}
			for cell in gridCheckBoxes[1:]
		] + [
			{"view1": self.w.newTab, "attribute1": "width", "view2": self.w.override, "attribute2": "width"},
		]
		# checkboxes and square buttons do not resist vertical stretching by default.
		# With every control hugging vertically and no flexible gap in the chain below,
		# the window takes exactly the height Auto Layout needs -- NSLayoutPriorityWindowSizeStayPut
		# is the level above which a constraint outranks "keep the window size".
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[buildEstimated]-gap-[buildBars]-gap-[buildEmptyset]-gap-[buildDottedcircle]-(>=inset)-|",
				"H:|-inset-[buildCurrency]-gap-[buildLozenge]-gap-[buildProduct]",
				"H:|-inset-[buildSummation]-gap-[buildRadical]-gap-[buildNotdef]",
				"H:|-inset-[line]-inset-|",
				"H:|-inset-[override]-gap-[backupLayers]-inset-|",
				"H:|-inset-[newTab]-gap-[reuseTab]-inset-|",
				"H:|-inset-[uncheckAllButton(>=70)]-gap-[checkAllButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				# one vertical chain per column; equal row heights keep the rows aligned
				"V:|-row-[descriptionText]-row-[buildEstimated]-row-[buildCurrency]-row-[buildSummation]-row-[line(1)]-row-[override]-row-[newTab]-inset-[runButton]-inset-|",
				"V:|-row-[descriptionText]-row-[buildBars]-row-[buildLozenge]-row-[buildRadical]-row-[line]-row-[backupLayers]-row-[reuseTab]",
				"V:|-row-[descriptionText]-row-[buildEmptyset]-row-[buildProduct]-row-[buildNotdef]",
				"V:|-row-[descriptionText]-row-[buildDottedcircle]",
				"V:[uncheckAllButton]-inset-|",
				"V:[checkAllButton]-inset-|",
			] + columnRules,
			metrics={"inset": 15, "gap": 8, "row": 8},
		)

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
		Glyphs.defaults[self.domain("buildEmptyset")] = onOrOff
		Glyphs.defaults[self.domain("buildCurrency")] = onOrOff
		Glyphs.defaults[self.domain("buildLozenge")] = onOrOff
		Glyphs.defaults[self.domain("buildProduct")] = False  # not yet implemented, so never checked
		Glyphs.defaults[self.domain("buildSummation")] = False  # not yet implemented, so never checked
		Glyphs.defaults[self.domain("buildRadical")] = False  # not yet implemented, so never checked
		Glyphs.defaults[self.domain("buildNotdef")] = onOrOff
		Glyphs.defaults[self.domain("buildDottedcircle")] = onOrOff
		self.LoadPreferences()

	@staticmethod
	def tabStringForExistingGlyphs(thisFont, glyphNames):
		"""Returns '/name' for each glyph (separated by slashes) that actually exists in the font, e.g. when the build failed."""
		return "".join(f"/{glyphName}" for glyphName in glyphNames.split("/") if thisFont.glyphs[glyphName])

	def BuildSymbolsMain(self, sender):
		try:
			Glyphs.clearLog()  # clears macro window log

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Glyphs.showMacroWindow()
				print("⚠️ Build Symbols: No font open.")
				return

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
				tabText += self.tabStringForExistingGlyphs(thisFont, "estimated")

			if self.pref("buildBars"):
				print("\n🔣 Building bars:")
				buildBars(thisFont, override=override)
				tabText += self.tabStringForExistingGlyphs(thisFont, "bar/brokenbar")

			if self.pref("buildEmptyset"):
				print("\n🔣 Building emptyset:")
				buildEmptyset(thisFont, override=override)
				tabText += self.tabStringForExistingGlyphs(thisFont, "emptyset")

			if self.pref("buildCurrency"):
				print("\n🔣 Building currency:")
				buildCurrency(thisFont, override=override)
				tabText += self.tabStringForExistingGlyphs(thisFont, "currency")

			if self.pref("buildLozenge"):
				print("\n🔣 Building lozenge:")
				buildLozenge(thisFont, override=override)
				tabText += self.tabStringForExistingGlyphs(thisFont, "lozenge")

			if self.pref("buildProduct"):
				print("\n🔣 Building product:")
				print("😢 Not yet implemented, sorry.")

			if self.pref("buildSummation"):
				print("\n🔣 Building summation:")
				print("😢 Not yet implemented, sorry.")

			if self.pref("buildRadical"):
				print("\n🔣 Building radical:")
				print("😢 Not yet implemented, sorry.")

			if self.pref("buildNotdef"):
				print("\n🔣 Building notdef:")
				buildNotdef(thisFont, override=override)
				tabText += self.tabStringForExistingGlyphs(thisFont, ".notdef")

			if self.pref("buildDottedcircle"):
				print("\n🔣 Building dottedCircle:")
				buildDottedCircle(thisFont, override=override)
				tabText += self.tabStringForExistingGlyphs(thisFont, "dottedCircle")

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
			print(traceback.format_exc())


BuildSymbols()
