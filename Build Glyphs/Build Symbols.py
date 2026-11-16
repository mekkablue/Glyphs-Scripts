# MenuTitle: Build Symbols
__doc__ = """
Creates an estimated glyph and draws an estimated sign in it. Does the same for bar and brokenbar, for which it respects standard stems and italic angle, and for emptyset, dottedCircle, currency, lozenge, product, summation, radical, dagger, daggerdbl and .notdef. Stem widths are measured on the slash, else taken from the master stems, else defaulted, so it also works in an empty font.
"""

import math
import traceback

import vanilla

from mekkablue import mekkaObject, newGlyphWithName, newAnchorWithName
from mekkablue.geometry import transform, italicize, offsetLayer
from GlyphsApp import Glyphs, GSPath, GSNode, GSOFFCURVE, GSCURVE, GSLINE, distance, intersectPaths
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSPoint

# handle length for a circle drawn with four Bézier segments, relative to its radius:
CIRCLE_HANDLE = 4.0 * (2.0**0.5 - 1.0) / 3.0
# slightly longer handles, as in the .notdef circle and the dots of the dottedCircle:
DOT_HANDLE = 0.58

# estimated ℮ as pen data (see drawPenDataInLayer): a tuple of paths,
# each path being a start point followed by line (x, y) and curve ((x, y), (x, y), (x, y)) segments
ESTIMATED_PENDATA = (
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


# glyphs that createGlyph() has handed out in the current run, with an open undo group each:
BUILT_GLYPHS = []
# stem widths measured in the current run, so the slash is measured once per master and not once per symbol:
MEASUREMENTS = {}


def endUndoGroups():
	"""Closes the undo group of every glyph built in this run, so the whole run is one undo step."""
	for glyph in BUILT_GLYPHS:
		glyph.endUndo()
	BUILT_GLYPHS.clear()


def circleAtCenter(center=NSPoint(0, 0), radius=50, bcp=CIRCLE_HANDLE):
	"""Returns a closed GSPath with a circle of this radius around the center."""
	circle = GSPath()
	x = center.x
	y = center.y
	handle = radius * bcp
	segments = (
		((x + handle, y - radius), (x + radius, y - handle), (x + radius, y)),
		((x + radius, y + handle), (x + handle, y + radius), (x, y + radius)),
		((x - handle, y + radius), (x - radius, y + handle), (x - radius, y)),
		((x - radius, y - handle), (x - handle, y - radius), (x, y - radius)),
	)
	for firstHandle, secondHandle, onCurve in segments:
		for handlePosition in (firstHandle, secondHandle):
			handleNode = GSNode()
			handleNode.type = GSOFFCURVE
			handleNode.position = NSPoint(*handlePosition)
			circle.nodes.append(handleNode)

		onCurveNode = GSNode()
		onCurveNode.type = GSCURVE
		onCurveNode.smooth = True
		onCurveNode.position = NSPoint(*onCurve)
		circle.nodes.append(onCurveNode)

	circle.closed = True
	return circle


def createGlyph(font, glyphName, unicodeValue, override=False, backupLayers=False, defaultWidth=500):
	"""
	Returns the new (or, with override, cleared) glyph in the font,
	or None if the glyph exists and may not be overwritten.
	"""
	glyph = font.glyphs[glyphName]
	if not glyph:
		glyph = newGlyphWithName(glyphName)
		if unicodeValue:
			glyph.unicode = unicodeValue
		font.glyphs.append(glyph)
		glyph.updateGlyphInfo()
		glyph.beginUndo()
		BUILT_GLYPHS.append(glyph)
		return glyph

	if not override:
		print(f"\t⚠️ {glyphName}: already exists and overwriting is off, skipped")
		return None

	print(f"\t☑️ {glyphName}: exists, overwriting")

	# create backups of layers (if wanted), and clear them:
	backups = []
	for layer in glyph.layers:
		if not (layer.isMasterLayer or layer.isSpecialLayer):
			continue

		if backupLayers:
			if not layer.shapes:
				print(f"- Layer ‘{layer.name or '(empty)'}’ is empty. No backup needed.")
			else:
				layerCopy = layer.copy()
				layerCopy.background = layer.copyDecomposedLayer()
				layerCopy.name = f"Backup: {layer.name}"
				backups.append(layerCopy)
				print(f"- Creating backup of layer: {layer.name or '(empty)'}")

		layer.clear()
		layer.anchors.clear()  # layer.clear() does not remove the anchors
		layer.background.clear()
		layer.leftMetricsKey = None
		layer.rightMetricsKey = None
		layer.width = defaultWidth

	# add collected backup layers (after the loop):
	for backup in backups:
		glyph.layers.append(backup)

	# remove special layers:
	for index in range(len(glyph.layers) - 1, -1, -1):
		if glyph.layers[index].isSpecialLayer:
			del glyph.layers[index]

	# an existing glyph may lack the Unicode value, category or script:
	if unicodeValue and not glyph.unicode:
		glyph.unicode = unicodeValue
	glyph.updateGlyphInfo(changeName=False)

	glyph.beginUndo()
	BUILT_GLYPHS.append(glyph)
	return glyph


def setMetrics(glyph, leftKey="=50", rightKey="=|", kerningGroup=None):
	"""Sets metrics keys and, if given, the kerning group on both sides of the glyph."""
	if leftKey:
		glyph.leftMetricsKey = leftKey
	if rightKey:
		glyph.rightMetricsKey = rightKey
	if kerningGroup:
		glyph.leftKerningGroup = kerningGroup
		glyph.rightKerningGroup = kerningGroup


def capHeightOf(master):
	"""Returns the cap height of the master; if it is not set, 140% of the x-height; if that is not set either, 700."""
	if master.capHeight and master.capHeight > 0:
		return master.capHeight
	if master.xHeight and master.xHeight > 0:
		return master.xHeight * 1.4
	return 700.0


def zeroGlyphOf(font):
	"""Returns the first available zero (lining, tabular, default) of the font, or None."""
	for zeroName in ("zero.lf", "zero.tf", "zero"):
		if font.glyphs[zeroName]:
			return font.glyphs[zeroName]
	return None


def slashLayerOf(font, master):
	"""Returns the slash layer for the master, or None if there is no slash or it is empty."""
	slashGlyph = font.glyphs["slash"]
	if slashGlyph:
		slashLayer = slashGlyph.layers[master.id]
		if slashLayer.fastBounds().size.height > 0:
			return slashLayer
	return None


def drawPenDataInLayer(layer, penData, closePath=True):
	"""Draws paths in the layer. Each path is a start point, followed by line (2 coordinates) or curve (3 points) segments."""
	for path in penData:
		pen = layer.getPen()
		pen.moveTo(path[0])
		for segment in path[1:]:
			if len(segment) == 2:  # lineto (2 coordinates: x,y)
				pen.lineTo(segment)
			elif len(segment) == 3:  # curveto (3 x/y tuples)
				pen.curveTo(segment[0], segment[1], segment[2])
			else:
				print(f"Path drawing error. Could not process this segment: {segment}\n")
		if closePath:
			pen.closePath()
		pen.endPath()

	# clean up:
	layer.cleanUpPaths()


def areaOfLayer(layer):
	layerCopy = layer.copyDecomposedLayer()
	layerCopy.removeOverlap()
	return sum(shape.area() for shape in layerCopy.shapes)


def verticalStemOfMaster(font, master):
	"""Returns the first vertical stem value set in the master, or None."""
	if Glyphs.versionNumber >= 4:
		# Glyphs 4: the stems of the master line up with font.stems, which flags each as horizontal or vertical
		for index, stem in enumerate(font.stems):
			if not stem.horizontal and master.stems[index]:
				return master.stems[index]
	elif master.verticalStems:
		# Glyphs 3 and earlier
		return master.verticalStems[0]
	return None


def stemWidthForMaster(font, master, default=60, maxWidth=None):
	"""Stem thickness measured on the slash; else 80% of the master’s vertical stem; else the default. Never more than maxWidth."""
	key = ("stem", master.id, default)
	if key not in MEASUREMENTS:
		MEASUREMENTS[key] = measureStemWidth(font, master, default)
	width = MEASUREMENTS[key]
	if maxWidth and maxWidth > 2:
		width = min(width, maxWidth)
	return width


def measureStemWidth(font, master, default):
	"""The uncached measurement behind stemWidthForMaster()."""
	width = None
	slash = slashLayerOf(font, master)
	if slash:
		try:
			bounds = slash.fastBounds()
			slashLeft = bounds.origin.x
			slashRight = slashLeft + bounds.size.width
			slashBottom = bounds.origin.y
			slashTop = slashBottom + bounds.size.height
			middleHeight = (slashBottom + slashTop) / 2
			measureStart = NSPoint(slashLeft, middleHeight)
			measureEnd = NSPoint(slashRight, middleHeight)
			intersections = list(slash.intersectionsBetweenPoints(measureStart, measureEnd))
			slashStemWidth = distance(intersections[1].pointValue(), intersections[2].pointValue())  # hypotenuse
			angleRAD = math.atan((slashTop - slashBottom) / (slashRight - slashLeft))
			width = ((slashStemWidth * math.cos(angleRAD)) + slashStemWidth) * 0.5
		except (IndexError, ZeroDivisionError):
			print("⚠️ Error measuring slash, will try master stem width instead.")

	if width is None:
		verticalStem = verticalStemOfMaster(font, master)
		if verticalStem:
			width = verticalStem * 0.8

	if width is None:
		print(f"⚠️ Error measuring stem width: No vertical stems set in master ‘{master.name}’. Will default to {default}.")
		width = default
	return width


def barStemWidthForMaster(font, master):
	"""Stem thickness for bar and brokenbar (and emptyset): measured on the slash if there is one, else from the master stems."""
	key = ("barStem", master.id)
	if key in MEASUREMENTS:
		return MEASUREMENTS[key]

	# a stem of this thickness, slanted by the italic angle, is wider than that when cut horizontally:
	stemWidth = stemWidthForMaster(font, master) / math.cos(math.radians(master.italicAngle))

	slashLayer = slashLayerOf(font, master)
	if slashLayer:
		slashBounds = slashLayer.fastBounds()
		middle = slashBounds.origin.y + slashBounds.size.height * 0.5
		suggestedStemWidth = slashLayer.width - slashLayer.rsbAtHeight_(middle) - slashLayer.lsbAtHeight_(middle)
		if suggestedStemWidth > 0:
			stemWidth = int(suggestedStemWidth * 0.96)
	MEASUREMENTS[key] = stemWidth
	return stemWidth


def drawStrokedSkeleton(font, master, layer, penData, size, maxStemFactor, closePath):
	"""Draws the skeleton, expands it by the stem width (at most maxStemFactor of the size), and centers it in the cap height."""
	drawPenDataInLayer(layer, penData, closePath=closePath)

	stemWidth = stemWidthForMaster(font, master, maxWidth=size * maxStemFactor)
	offsetLayer(layer, stemWidth / 2, makeStroke=True, position=0.5)

	moveUp = (capHeightOf(master) - size) * 0.5
	layer.applyTransform(transform(shiftY=moveUp).transformStruct())

	layer.cleanUpPaths()
	layer.syncMetrics()


def notdefFrameInLayer(font, master, layer):
	"""Draws the tofu rectangle in the layer: a frame of cap height, with the stem width of the master."""
	height = capHeightOf(master)
	width = height * 0.6
	stem = stemWidthForMaster(font, master, maxWidth=width * 0.2)
	drawPenDataInLayer(
		layer,
		(
			((0.0, 0.0), (width, 0.0), (width, height), (0.0, height)),  # outer frame, counterclockwise
			((stem, stem), (stem, height - stem), (width - stem, height - stem), (width - stem, stem)),  # counter, clockwise
		),
	)


def buildNotdef(font, override=False, backupLayers=False):
	# use the boldest question mark, if there is one with outlines:
	sourceLayer = None
	questionGlyph = font.glyphs["question"]
	if questionGlyph:
		questionLayers = [layer for layer in questionGlyph.layers if (layer.isMasterLayer or layer.isSpecialLayer) and layer.shapes]
		if questionLayers:
			sourceLayer = max(questionLayers, key=areaOfLayer)
	if sourceLayer is None:
		print("⚠️ No question mark with outlines in your font. Will build a simple .notdef frame instead.")

	notdefGlyph = createGlyph(font, ".notdef", None, override=override, backupLayers=backupLayers)
	if not notdefGlyph:
		return

	if sourceLayer is None:
		setMetrics(notdefGlyph, leftKey="=40")
		for master in font.masters:
			notdefLayer = notdefGlyph.layers[master.id]
			notdefFrameInLayer(font, master, notdefLayer)
			notdefLayer.syncMetrics()
		return

	# build .notdef from question mark and circle:
	questionmarkLayer = sourceLayer.copyDecomposedLayer()
	questionmarkLayer.applyTransform(transform(scale=0.8).transformStruct())
	bounds = questionmarkLayer.fastBounds()
	center = NSPoint(bounds.origin.x + 0.5 * bounds.size.width, bounds.origin.y + 0.5 * bounds.size.height)
	side = max(bounds.size.width, bounds.size.height) * 1.5
	questionmarkLayer.shapes.append(circleAtCenter(center=center, radius=side * 0.5, bcp=DOT_HANDLE))
	questionmarkLayer.correctPathDirection()

	# create glyph:
	setMetrics(notdefGlyph, leftKey="=40")
	for master in font.masters:
		notdefLayer = notdefGlyph.layers[master.id]
		for path in questionmarkLayer.paths:
			notdefLayer.shapes.append(path.copy())
		notdefFrameInLayer(font, master, notdefLayer.background)  # tofu rectangle as reference in the background
		notdefLayer.syncMetrics()


def buildLozenge(font, override=False, backupLayers=False):
	glyph = createGlyph(font, "lozenge", "25CA", override=override, backupLayers=backupLayers)
	if not glyph:
		return
	setMetrics(glyph, kerningGroup="lozenge")

	for master in font.masters:
		layer = glyph.layers[master.id]
		size = capHeightOf(master) * 0.7  # 70% cap height
		skeleton = (
			(  # fin
				(size * 0.3, size * 1.0),
				(size * 0.0, size * 0.5),
				(size * 0.3, size * 0.0),
				(size * 0.6, size * 0.5),
			),
		)
		drawStrokedSkeleton(font, master, layer, skeleton, size, maxStemFactor=0.6 * 0.3, closePath=True)

		# cut off caps:
		midTop = sum(path.fastBounds().origin.y + path.fastBounds().size.height for path in layer.paths) / 2.0
		midBottom = sum(path.fastBounds().origin.y for path in layer.paths) / 2.0
		intersector = GSPath()
		for coordinate in ((0, midBottom), (layer.width, midBottom), (layer.width, midTop), (0, midTop)):
			intersector.nodes.append(GSNode(NSPoint(*coordinate)))
		intersector.closed = True

		outlines = list(layer.paths)
		trimmedOutlines = intersectPaths([intersector], outlines)
		if trimmedOutlines is None:
			print(f"\t⚠️ lozenge: could not cut off the caps in master ‘{master.name}’")
		else:
			for outline in outlines:
				layer.shapes.remove(outline)
			for outline in trimmedOutlines:
				layer.shapes.append(outline)
		layer.syncMetrics()  # the outline changed after the first sync


def buildCurrency(font, override=False, backupLayers=False):
	glyph = createGlyph(font, "currency", "00A4", override=override, backupLayers=backupLayers)
	if not glyph:
		return
	setMetrics(glyph, kerningGroup="currency")

	for master in font.masters:
		layer = glyph.layers[master.id]
		size = capHeightOf(master) * 0.6  # 60% cap height
		skeleton = (
			(  # circle
				(size * 0.500, size * 0.173),
				((size * 0.680, size * 0.173), (size * 0.827, size * 0.320), (size * 0.827, size * 0.500)),
				((size * 0.827, size * 0.680), (size * 0.680, size * 0.827), (size * 0.500, size * 0.827)),
				((size * 0.320, size * 0.827), (size * 0.173, size * 0.680), (size * 0.173, size * 0.500)),
				((size * 0.173, size * 0.320), (size * 0.320, size * 0.173), (size * 0.500, size * 0.173)),
			),
			(  # fin
				(size * 1.000, size * 1.000), (size * 0.741, size * 0.741),
			),
			(  # fin
				(size * 0.000, size * 0.000), (size * 0.259, size * 0.259),
			),
			(  # fin
				(size * 0.000, size * 1.000), (size * 0.259, size * 0.741),
			),
			(  # fin
				(size * 1.000, size * 0.000), (size * 0.741, size * 0.259),
			),
		)
		drawStrokedSkeleton(font, master, layer, skeleton, size, maxStemFactor=0.5 * 0.3, closePath=False)


def buildEstimated(font, override=False, backupLayers=False):
	glyph = createGlyph(font, "estimated", "212E", override=override, backupLayers=backupLayers)
	if not glyph:
		return
	setMetrics(glyph, leftKey="=40", kerningGroup="estimated")

	zeroGlyph = zeroGlyphOf(font)
	for master in font.masters:
		layer = glyph.layers[master.id]
		drawPenDataInLayer(layer, ESTIMATED_PENDATA)

		# scale estimated to match zero:
		if zeroGlyph:
			zeroBounds = zeroGlyph.layers[master.id].fastBounds()
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
					layer.applyTransform(estimatedCorrection.transformStruct())

		layer.cleanUpPaths()
		layer.syncMetrics()


def buildEmptyset(font, override=False, backupLayers=False):
	glyph = createGlyph(font, "emptyset", "2205", override=override, backupLayers=backupLayers)
	if not glyph:
		return
	setMetrics(glyph)

	zeroGlyph = zeroGlyphOf(font)  # for measuring the overshoot
	diagonalFactor = 2.0**0.5  # diagonal of a square bounding box, in units of its side
	for master in font.masters:
		layer = glyph.layers[master.id]

		# height: average of x-height and cap height, plus overshoot at bottom and top:
		overshoot = 5.0
		if zeroGlyph:
			zeroBounds = zeroGlyph.layers[master.id].bounds
			if zeroBounds is not None and zeroBounds.size.height > 0:
				overshoot = abs(min(-5.0, zeroBounds.origin.y))
		baseHeight = (master.xHeight + capHeightOf(master)) * 0.5
		height = baseHeight + 2 * overshoot
		radius = height * 0.5
		center = NSPoint(radius, baseHeight * 0.5)

		# stem thickness as for bar and brokenbar, but at most 18% of the height:
		stemWidth = min(barStemWidthForMaster(font, master), height * 0.18)

		# circle with 57% handles; the stroke grows only inward.
		# Outer circle runs counterclockwise, inner circle clockwise (counter):
		layer.shapes.append(circleAtCenter(center=center, radius=radius, bcp=0.57))
		innerCircle = circleAtCenter(center=center, radius=radius - stemWidth, bcp=0.57)
		innerCircle.reverse()
		layer.shapes.append(innerCircle)

		# slash at 45° through the center of the circle, with the same thickness (counterclockwise,
		# overlapping the circle on purpose, so no overlaps are removed):
		slashLength = (height + 2 * height * diagonalFactor) / 3.0
		halfLength = slashLength * 0.5
		halfWidth = stemWidth * 0.5
		slash = GSPath()
		for lengthSign, widthSign in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
			along = lengthSign * halfLength
			across = widthSign * halfWidth
			node = GSNode()
			node.type = GSLINE
			node.position = NSPoint(center.x + (along - across) / diagonalFactor, center.y + (along + across) / diagonalFactor)
			slash.nodes.append(node)
		slash.closed = True
		layer.shapes.append(slash)

		layer.syncMetrics()


def buildDottedCircle(font, override=False, backupLayers=False):
	glyph = createGlyph(font, "dottedCircle", "25CC", override=override, backupLayers=backupLayers)
	if not glyph:
		return
	setMetrics(glyph)

	steps = 12
	anchorNames = ["top", "bottom"]
	if font.glyphs["ogonekcomb"]:
		anchorNames.append("ogonekcomb")

	for master in font.masters:
		layer = glyph.layers[master.id]
		factor = layer.ascender * 0.74 / 2
		for step in range(steps):
			angle = step * 2 * math.pi / steps
			dot = circleAtCenter(
				center=NSPoint(factor * math.sin(angle), factor * math.cos(angle) + layer.ascender / 2),
				radius=2 * factor / steps,
				bcp=DOT_HANDLE,
			)
			layer.shapes.append(dot)

		# update metrics:
		layer.cleanUpPaths()
		layer.syncMetrics()

		for anchorName in anchorNames:
			anchorY = layer.ascender if anchorName == "top" else 0.0
			layer.anchors.append(newAnchorWithName(anchorName, NSPoint(layer.width / 2, anchorY)))


def buildBars(font, override=False, backupLayers=False):
	barGlyph = createGlyph(font, "bar", "007C", override=override, backupLayers=backupLayers)
	brokenbarGlyph = createGlyph(font, "brokenbar", "00A6", override=override, backupLayers=backupLayers)
	if not (barGlyph or brokenbarGlyph):
		return

	if barGlyph:
		setMetrics(barGlyph, leftKey=None, kerningGroup="bar")
	if brokenbarGlyph:
		setMetrics(brokenbarGlyph, leftKey="=bar", kerningGroup="bar")

	# default vertical extent: from the lowest descender to the highest ascender of all masters
	lowestDescender = min(master.descender for master in font.masters)
	highestAscender = max(master.ascender for master in font.masters)
	for master in font.masters:
		descender = lowestDescender
		ascender = highestAscender
		italicAngle = master.italicAngle
		pivot = master.xHeight * 0.5
		stemWidth = barStemWidthForMaster(font, master)

		slashLayer = slashLayerOf(font, master)
		if slashLayer:
			slashBounds = slashLayer.fastBounds()
			descender = slashBounds.origin.y
			ascender = descender + slashBounds.size.height

		sidebearing = max((350 - stemWidth) * 0.5, 60.0)
		gap = max(250 - stemWidth, 120.0)

		def corner(x, y):
			point = italicize(NSPoint(x, y), italicAngle=italicAngle, pivotalY=pivot)
			return (point.x, point.y)

		left = sidebearing
		right = sidebearing + stemWidth
		bottomLeft, bottomRight = corner(left, descender), corner(right, descender)
		topLeft, topRight = corner(left, ascender), corner(right, ascender)

		if barGlyph:
			barLayer = barGlyph.layers[master.id]
			drawPenDataInLayer(barLayer, ((bottomLeft, bottomRight, topRight, topLeft), ))
			barLayer.RSB = sidebearing
			barLayer.syncMetrics()

		if brokenbarGlyph:
			gapBottomY = ((ascender + descender) - gap) * 0.5
			gapTopY = ((ascender + descender) + gap) * 0.5
			gapBottomLeft, gapBottomRight = corner(left, gapBottomY), corner(right, gapBottomY)
			gapTopLeft, gapTopRight = corner(left, gapTopY), corner(right, gapTopY)

			brokenbarLayer = brokenbarGlyph.layers[master.id]
			drawPenDataInLayer(
				brokenbarLayer,
				(
					(bottomLeft, bottomRight, gapBottomRight, gapBottomLeft),
					(gapTopLeft, gapTopRight, topRight, topLeft),
				),
			)
			brokenbarLayer.RSB = sidebearing
			brokenbarLayer.syncMetrics()


def bigSymbolBoxOfMaster(master):
	"""Returns (bottom, height) of the box for product, summation and radical: 110% cap height, centered on half the cap height."""
	capHeight = capHeightOf(master)
	height = capHeight * 1.1
	return capHeight * 0.5 - height * 0.5, height


def daggerBoxOfMaster(master):
	"""Returns (bottom, height) of the box for dagger and daggerdbl: 60% cap height, butted up against the cap height."""
	capHeight = capHeightOf(master)
	height = capHeight * 0.6
	return capHeight - height, height


def mappedPenData(penData, mapPoint):
	"""Returns the pen data with every point replaced by mapPoint(point)."""
	result = []
	for path in penData:
		mappedPath = [mapPoint(path[0])]
		for segment in path[1:]:
			if len(segment) == 3:  # curve: three points
				mappedPath.append(tuple(mapPoint(point) for point in segment))
			else:  # line: one point
				mappedPath.append(mapPoint(segment))
		result.append(tuple(mappedPath))
	return tuple(result)


def crossPenData(width, height, stem, bar, barCenters):
	"""A stem and one overlapping crossbar rectangle at each of the heights in barCenters. Origin bottom left, counterclockwise."""
	stemLeft = (width - stem) * 0.5
	stemRight = stemLeft + stem
	rectangles = [((stemLeft, 0.0), (stemRight, 0.0), (stemRight, height), (stemLeft, height))]
	for center in barCenters:
		rectangles.append(((0.0, center - bar * 0.5), (width, center - bar * 0.5), (width, center + bar * 0.5), (0.0, center + bar * 0.5)))
	return tuple(rectangles)


def daggerPenData(width, height, stem, bar):
	"""† as two overlapping rectangles: a stem with a crossbar in its upper third."""
	return crossPenData(width, height, stem, bar, (height * 0.68, ))


def daggerdblPenData(width, height, stem, bar):
	"""‡ as three overlapping rectangles: a stem with two crossbars."""
	return crossPenData(width, height, stem, bar, (height * 0.36, height * 0.74))


def productPenData(width, height, stem, bar):
	"""∏ as three overlapping rectangles: a bar on top, and two legs that end in the middle of the bar. Origin bottom left, counterclockwise."""
	overhang = bar * 0.6
	legTop = height - bar * 0.5  # halfway through the bar, equidistant to its edges
	legLeft = overhang
	legRight = width - overhang - stem
	return (
		((0.0, height - bar), (width, height - bar), (width, height), (0.0, height)),
		((legLeft, 0.0), (legLeft + stem, 0.0), (legLeft + stem, legTop), (legLeft, legTop)),
		((legRight, 0.0), (legRight + stem, 0.0), (legRight + stem, legTop), (legRight, legTop)),
	)


def summationPenData(width, height, stem, bar):
	"""
	∑ as one contour: two bars, joined by two diagonals meeting in a knee at two thirds of the width.
	Where the outlines meet at an inner corner they overshoot and are closed by a short segment (“opened corner”),
	so each corner holds a small triangle of overlap: at the knee two edges reach `overshoot` beyond their crossing and are joined
	vertically; at the bar corners the bar underside reaches to the left, and the diagonal into the middle of the bar.
	Origin bottom left, counterclockwise.
	"""
	diagonal = stem * 1.3  # horizontal thickness of the diagonals
	middle = height * 0.5
	cornerHeight = bar * 0.8  # the vertical segments at the left end are a bit shorter than the stroke
	overshoot = bar * 0.75
	kneeX = width * 2.0 / 3.0
	slope = (kneeX - diagonal) / (middle - cornerHeight)  # horizontal run per unit of height of the diagonals

	def leftEdgeX(y):  # outer left edge of the upper diagonal (extended beyond its ends)
		return (height - cornerHeight - y) * slope

	def rightEdgeX(y):  # right edge of the upper diagonal, parallel to the left edge
		return leftEdgeX(y) + diagonal

	cornerMiddleX = rightEdgeX(height - bar * 0.5)
	barReachX = cornerMiddleX - bar * 0.5  # where the underside of the bar ends, at 45° from the point in the middle of the bar
	kneeCutX = leftEdgeX(middle - overshoot)

	return ((
		(0.0, height),
		(0.0, height - cornerHeight),
		(kneeCutX, middle - overshoot),
		(kneeCutX, middle + overshoot),
		(0.0, cornerHeight),
		(0.0, 0.0),
		(width, 0.0),
		(width, bar),
		(barReachX, bar),
		(cornerMiddleX, bar * 0.5),
		(kneeX, middle),
		(cornerMiddleX, height - bar * 0.5),
		(barReachX, height - bar),
		(width, height - bar),
		(width, height),
	), )


def radicalPenData(width, height, stem, bar):
	"""
	√ as one contour: the downstroke, and the upstroke with the bar on top. All strokes have parallel edges.
	The inner corners are opened as in the summation: the edge of the downstroke and the edge of the upstroke overshoot where they cross
	and are joined by a short horizontal segment; at the bar, the underside reaches to the left, and the upstroke into the middle of the bar.
	Origin bottom left, counterclockwise.
	"""
	heavy = stem * 1.3  # horizontal thickness of the downstroke
	light = stem * 0.7  # horizontal thickness of the upstroke
	overshoot = bar * 0.75
	downTop = height * 0.5  # height of the flat top of the downstroke
	footLeft = width * 0.26
	upstrokeTopLeft = width * 0.52

	def upstrokeLeftX(y):
		return footLeft + (upstrokeTopLeft - footLeft) * y / height

	def downstrokeRightX(y):
		return footLeft * (1.0 - y / downTop) + heavy

	# height where the right edge of the downstroke crosses the left edge of the upstroke:
	crossing = heavy / (footLeft / downTop + (upstrokeTopLeft - footLeft) / height)
	cutHeight = crossing - overshoot

	cornerMiddleX = upstrokeLeftX(height - bar * 0.5) + light
	barReachX = cornerMiddleX - bar * 0.5

	return ((
		(footLeft, 0.0),
		(footLeft + light, 0.0),
		(cornerMiddleX, height - bar * 0.5),
		(barReachX, height - bar),
		(width, height - bar),
		(width, height),
		(upstrokeTopLeft, height),
		(upstrokeLeftX(cutHeight), cutHeight),
		(downstrokeRightX(cutHeight), cutHeight),
		(heavy, downTop),
		(0.0, downTop),
	), )


def buildPolygonSymbol(
	font, glyphName, unicodeValue, penDataFunction, boxFunction, widthFactor, maxStemFactor, override=False, backupLayers=False, rightKey="=|"
):
	"""
	Builds a polygon symbol in every master. boxFunction(master) returns (bottom, height); the width is a factor of the height;
	the stem is measured as for the other symbols, but at most maxStemFactor of the height.
	"""
	glyph = createGlyph(font, glyphName, unicodeValue, override=override, backupLayers=backupLayers)
	if not glyph:
		return
	setMetrics(glyph, rightKey=rightKey, kerningGroup=glyphName)

	for master in font.masters:
		layer = glyph.layers[master.id]
		bottom, height = boxFunction(master)
		width = height * widthFactor
		stem = stemWidthForMaster(font, master, maxWidth=height * maxStemFactor)
		bar = stem * 0.85  # horizontals are lighter than verticals

		def place(point):
			slanted = italicize(NSPoint(point[0], point[1] + bottom), italicAngle=master.italicAngle, pivotalY=master.xHeight * 0.5)
			return (slanted.x, slanted.y)

		drawPenDataInLayer(layer, mappedPenData(penDataFunction(width, height, stem, bar), place))
		layer.correctPathDirection()
		layer.syncMetrics()


def buildProduct(font, override=False, backupLayers=False):
	buildPolygonSymbol(font, "product", "220F", productPenData, bigSymbolBoxOfMaster, 0.66, 0.12, override=override, backupLayers=backupLayers)


def buildSummation(font, override=False, backupLayers=False):
	buildPolygonSymbol(font, "summation", "2211", summationPenData, bigSymbolBoxOfMaster, 0.527, 0.12, override=override, backupLayers=backupLayers)


def buildDaggers(font, override=False, backupLayers=False):
	buildPolygonSymbol(font, "dagger", "2020", daggerPenData, daggerBoxOfMaster, 0.6, 0.15, override=override, backupLayers=backupLayers)
	buildPolygonSymbol(font, "daggerdbl", "2021", daggerdblPenData, daggerBoxOfMaster, 0.6, 0.15, override=override, backupLayers=backupLayers)


def buildRadical(font, override=False, backupLayers=False):
	buildPolygonSymbol(font, "radical", "221A", radicalPenData, bigSymbolBoxOfMaster, 0.5, 0.1, override=override, backupLayers=backupLayers, rightKey="=0")


def tabStringForExistingGlyphs(font, glyphNames):
	"""Returns '/name' for each glyph name that actually exists in the font, e.g. when the build failed."""
	return "".join(f"/{glyphName}" for glyphName in glyphNames if font.glyphs[glyphName])


# One entry per symbol, in the order of the checkboxes and of the build:
# (preference name, checkbox title, tooltip, build function, glyph names)
SYMBOLS = (
	(
		"buildEstimated",
		"estimated ℮",
		"Will build estimated ℮ and scale it to the size of your lining zero, if available.",
		buildEstimated,
		("estimated", ),
	),
	(
		"buildBars",
		"bar | brokenbar ¦",
		"Will model bar | and brokenbar ¦ after your slash /, or if there is no slash, use the master’s stem values for their width. Without a slash, they extend from the lowest descender to the highest ascender of all masters.",
		buildBars,
		("bar", "brokenbar"),
	),
	(
		"buildEmptyset",
		"emptyset ∅",
		"Will build emptyset ∅: a circle with a slash, with the stem thickness of bar and brokenbar (but at most 18% of the height). Its height is the average of x-height and cap height plus the overshoot of your zero.",
		buildEmptyset,
		("emptyset", ),
	),
	(
		"buildDottedCircle",
		"dottedCircle ◌",
		"Will build dottedCircle ◌.",
		buildDottedCircle,
		("dottedCircle", ),
	),
	(
		"buildCurrency",
		"currency ¤",
		"Will build currency.",
		buildCurrency,
		("currency", ),
	),
	(
		"buildLozenge",
		"lozenge ◊",
		"Will build lozenge.",
		buildLozenge,
		("lozenge", ),
	),
	(
		"buildDaggers",
		"dagger † | daggerdbl ‡",
		"Will build dagger † and daggerdbl ‡ as simple crosses of overlapping rectangles (two and three): 60% of the cap height, butted up against the cap height, with the stem width of your slash or master stems. Respects the italic angle.",
		buildDaggers,
		("dagger", "daggerdbl"),
	),
	(
		"buildNotdef",
		".notdef",
		"Will build the mandatory .notdef glyph based on the boldest available question mark.",
		buildNotdef,
		(".notdef", ),
	),
	(
		"buildProduct",
		"product ∏",
		"Will build product ∏: three overlapping rectangles, 110% cap height, stems measured as for bar (slash, else master stems), horizontals at 85% of the stem. Respects the italic angle.",
		buildProduct,
		("product", ),
	),
	(
		"buildSummation",
		"summation ∑",
		"Will build summation ∑: one contour with opened corners (small triangles of overlap), 110% cap height, stems measured as for bar (slash, else master stems), horizontals at 85% of the stem. Respects the italic angle.",
		buildSummation,
		("summation", ),
	),
	(
		"buildRadical",
		"radical √",
		"Will build radical √: one contour with opened corners (small triangles of overlap), 110% cap height, stems measured as for bar (slash, else master stems), horizontals at 85% of the stem. Respects the italic angle.",
		buildRadical,
		("radical", ),
	),
)


class BuildSymbols(mekkaObject):
	prefDict = {"override": 0, "backupLayers": 0, "newTab": 1, "reuseTab": 1}
	prefDict.update({symbol[0]: 1 for symbol in SYMBOLS})  # every symbol is on by default

	def __init__(self):
		# Window 'self.w':
		windowWidth = 434
		windowHeight = 1  # Auto Layout grows the window to the required size
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Build Symbols",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		self.w.descriptionText = vanilla.TextBox("auto", "Create the following symbols automatically. See tooltips for requirements.", sizeStyle='small', selectable=True)

		for prefName, title, tooltip, _, _ in SYMBOLS:
			checkBox = vanilla.CheckBox("auto", title, value=True, callback=self.SavePreferences, sizeStyle='small')
			checkBox.setToolTip(tooltip)
			setattr(self.w, prefName, checkBox)

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

		# Status line:
		self.w.statusText = vanilla.TextBox("auto", "🔮 Will build up to – glyphs.", sizeStyle="small")
		self.w.statusText.setToolTip("Before you run: how many glyphs the checked symbols will build at most (existing glyphs are skipped unless you overwrite them). While running: the glyphs being built. Afterwards: how many glyphs were built.")
		self.w.statusText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.uncheckAllButton = vanilla.Button("auto", "Uncheck All", callback=self.checkAll)
		self.w.checkAllButton = vanilla.Button("auto", "Check All", callback=self.checkAll)
		self.w.uncheckAllButton.setToolTip("Unchecks all symbols.")
		self.w.checkAllButton.setToolTip("Checks all symbols.")
		self.w.runButton = vanilla.Button("auto", "Build", callback=self.BuildSymbolsMain)
		self.w.runButton.setToolTip("Builds the checked symbols in the frontmost font.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes and square buttons do not resist vertical stretching by default.
		# With every control hugging vertically and no flexible gap in the chain below,
		# the window takes exactly the height Auto Layout needs -- NSLayoutPriorityWindowSizeStayPut
		# is the level above which a constraint outranks "keep the window size".
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the symbol checkboxes form a grid, filled row by row:
		columnCount = 4
		symbolNames = [symbol[0] for symbol in SYMBOLS]
		gridRows = [symbolNames[index:index + columnCount] for index in range(0, len(symbolNames), columnCount)]
		rowRules = []
		for row in gridRows:
			rowRule = "H:|-inset-" + "-gap-".join(f"[{name}]" for name in row)
			if len(row) == columnCount:
				rowRule += "-(>=inset)-|"
			rowRules.append(rowRule)

		# one vertical chain per column; equal row heights keep the rows aligned.
		# The first two columns continue into the options below the separator line:
		columnTails = (
			"-row-[line(1)]-row-[override]-row-[newTab]-inset-[statusText]-row-[runButton]-inset-|",
			"-row-[line]-row-[backupLayers]-row-[reuseTab]",
		)
		columnRules = []
		for columnIndex in range(columnCount):
			column = [row[columnIndex] for row in gridRows if columnIndex < len(row)]
			columnTail = columnTails[columnIndex] if columnIndex < len(columnTails) else ""
			columnRules.append("V:|-row-[descriptionText]-row-" + "-row-".join(f"[{name}]" for name in column) + columnTail)

		# one shared width per grid column, so the checkboxes line up across the rows:
		widthRules = [{"view1": getattr(self.w, name), "attribute1": "width", "view2": getattr(self.w, symbolNames[0]), "attribute2": "width"} for name in symbolNames[1:]]
		widthRules.append({"view1": self.w.newTab, "attribute1": "width", "view2": self.w.override, "attribute2": "width"})

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[line]-inset-|",
				"H:|-inset-[statusText]-inset-|",
				"H:|-inset-[override]-gap-[backupLayers]-inset-|",
				"H:|-inset-[newTab]-gap-[reuseTab]-inset-|",
				"H:|-inset-[uncheckAllButton(>=70)]-gap-[checkAllButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:[uncheckAllButton]-inset-|",
				"V:[checkAllButton]-inset-|",
			] + rowRules + columnRules + widthRules,
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

		# prediction in the status line:
		glyphCount = sum(len(glyphNames) for prefName, _, _, _, glyphNames in SYMBOLS if getattr(self.w, prefName).get())
		self.w.statusText.set(f"🔮 Will build up to {glyphCount} glyph{'' if glyphCount == 1 else 's'}.")

	def setStatus(self, text):
		"""Sets the status line and redraws it right away, so it shows while the script is busy."""
		self.w.statusText.set(text)
		self.w.statusText.getNSTextField().display()

	def checkAll(self, sender=None, onOrOff=True):
		if sender is self.w.uncheckAllButton:
			onOrOff = False
		for prefName, _, _, _, _ in SYMBOLS:
			self.setPref(prefName, onOrOff)
		self.LoadPreferences()

	def BuildSymbolsMain(self, sender):
		try:
			Glyphs.clearLog()  # clears macro window log

			# update settings to the latest user input:
			self.SavePreferences()

			font = Glyphs.font  # frontmost font
			if font is None:
				Glyphs.showMacroWindow()
				print("⚠️ Build Symbols: No font open.")
				self.setStatus("⚠️ No font open.")
				return

			print(f"Build Symbols Report for {font.familyName}")
			if font.filepath:
				print(font.filepath)
			else:
				print("⚠️ File not yet saved.")
			print()

			# retrieve user settings:
			override = self.pref("override")
			backupLayers = self.pref("backupLayers")
			newTab = self.pref("newTab")
			reuseTab = self.pref("reuseTab")

			# build glyphs, as one undo step and without interface updates in between:
			tabText = ""
			builtCount = 0
			MEASUREMENTS.clear()
			BUILT_GLYPHS.clear()
			font.disableUpdateInterface()
			try:
				for prefName, _, _, builder, glyphNames in SYMBOLS:
					if not self.pref(prefName):
						continue
					print(f"\n🔣 Building {', '.join(glyphNames)}:")
					self.setStatus(f"🔠 {', '.join(glyphNames)}")
					builtBefore = len(BUILT_GLYPHS)
					builder(font, override=override, backupLayers=backupLayers)
					for glyph in BUILT_GLYPHS[builtBefore:]:
						print(f"\t✅ {glyph.name}: built in {len(font.masters)} master{'' if len(font.masters) == 1 else 's'}")
					builtCount += len(BUILT_GLYPHS) - builtBefore
					tabText += tabStringForExistingGlyphs(font, glyphNames)
			finally:
				endUndoGroups()
				font.enableUpdateInterface()
			self.setStatus(f"✅ Built {builtCount} glyph{'' if builtCount == 1 else 's'}.")

			# Floating notification:
			Glyphs.showNotification(
				f"{font.familyName}: symbols built",
				"Script ‘Build Symbols’ is finished.",
			)

			if newTab and tabText:
				if reuseTab and font.currentTab:
					# reuses current tab:
					font.currentTab.text = tabText
				else:
					# opens new Edit tab:
					font.newTab(tabText)

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			self.setStatus("❌ Error. See Macro Window.")
			print(f"Build Symbols Error: {e}")
			print(traceback.format_exc())


BuildSymbols()
