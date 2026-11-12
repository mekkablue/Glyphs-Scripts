# MenuTitle: Build Symbols
__doc__ = """
Creates an estimated glyph and draws an estimated sign in it. Does the same for bar and brokenbar, for which it respects standard stems and italic angle, and for emptyset, dottedCircle, currency, lozenge and .notdef.
"""

# TODO: product, summation, radical

import math
import traceback

import vanilla

from mekkablue import mekkaObject, newGlyphWithName, newAnchorWithName
from mekkablue.geometry import transform, italicize, offsetLayer
from GlyphsApp import Glyphs, GSPath, GSNode, GSOFFCURVE, GSCURVE, GSLINE, distance
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
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
		return glyph

	if not override:
		print(f"Glyph {glyphName} already exists. No override chosen. Skipping.")
		return None

	print(f"Overwriting existing glyph {glyphName}.")

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

	if maxWidth and maxWidth > 2:
		width = min(width, maxWidth)
	return width


def barStemWidthForMaster(font, master):
	"""Stem thickness for bar and brokenbar (and emptyset): measured on the slash if there is one, else from the master stems."""
	stemWidth = stemWidthForMaster(font, master)
	stemWidth -= stemWidth * math.cos(math.radians(master.italicAngle)) - stemWidth  # correct for italic angle

	slashLayer = slashLayerOf(font, master)
	if slashLayer:
		slashBounds = slashLayer.fastBounds()
		middle = slashBounds.origin.y + slashBounds.size.height * 0.5
		suggestedStemWidth = slashLayer.width - slashLayer.rsbAtHeight_(middle) - slashLayer.lsbAtHeight_(middle)
		if suggestedStemWidth > 0:
			stemWidth = int(suggestedStemWidth * 0.96)
	return stemWidth


def drawStrokedSkeleton(font, master, layer, penData, size, maxStemFactor, closePath):
	"""Draws the skeleton, expands it by the stem width (at most maxStemFactor of the size), and centers it in the cap height."""
	drawPenDataInLayer(layer, penData, closePath=closePath)

	stemWidth = stemWidthForMaster(font, master, maxWidth=size * maxStemFactor)
	offsetLayer(layer, stemWidth / 2, makeStroke=True, position=0.5)

	moveUp = (master.capHeight - size) * 0.5
	layer.applyTransform(transform(shiftY=moveUp).transformStruct())

	layer.cleanUpPaths()
	layer.syncMetrics()


def buildNotdef(font, override=False, backupLayers=False):
	questionGlyph = font.glyphs["question"]
	if not questionGlyph:
		print("⚠️ Error building .notdef: No question mark is available in your font. Cannot create .notdef.")
		return

	notdefGlyph = createGlyph(font, ".notdef", None, override=override, backupLayers=backupLayers)
	if not notdefGlyph:
		return

	# use the boldest question mark:
	questionLayers = [layer for layer in questionGlyph.layers if layer.isMasterLayer or layer.isSpecialLayer]
	sourceLayer = max(questionLayers, key=areaOfLayer)

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
		notdefLayer.syncMetrics()


def buildLozenge(font, override=False, backupLayers=False):
	glyph = createGlyph(font, "lozenge", "25CA", override=override, backupLayers=backupLayers)
	if not glyph:
		return
	setMetrics(glyph, kerningGroup="lozenge")

	for master in font.masters:
		layer = glyph.layers[master.id]
		size = master.capHeight * 0.7  # 70% cap height
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
		layer.shapes.append(intersector)

		layer.pathIntersect_from_error_([intersector], [layer.paths[0]], None)
		layer.syncMetrics()  # the outline changed after the first sync


def buildCurrency(font, override=False, backupLayers=False):
	glyph = createGlyph(font, "currency", "00A4", override=override, backupLayers=backupLayers)
	if not glyph:
		return
	setMetrics(glyph, kerningGroup="currency")

	for master in font.masters:
		layer = glyph.layers[master.id]
		size = master.capHeight * 0.6  # 60% cap height
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
		print(f"✅ Created estimated in master ‘{master.name}’")


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
		baseHeight = (master.xHeight + master.capHeight) * 0.5
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
		print(f"✅ Created emptyset in master ‘{master.name}’")


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
			print(f"✅ Created bar in master ‘{master.name}’")

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
			print(f"✅ Created brokenbar in master ‘{master.name}’")


def tabStringForExistingGlyphs(font, glyphNames):
	"""Returns '/name' for each glyph name that actually exists in the font, e.g. when the build failed."""
	return "".join(f"/{glyphName}" for glyphName in glyphNames if font.glyphs[glyphName])


# One entry per symbol, in the order of the checkboxes and of the build:
# (preference name, checkbox title, tooltip, build function (None: not yet implemented), glyph names)
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
		"buildDottedcircle",
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
		"buildNotdef",
		".notdef",
		"Will build the mandatory .notdef glyph based on the boldest available question mark.",
		buildNotdef,
		(".notdef", ),
	),
	(
		"buildProduct",
		"product ∏",
		"Will build product. Not yet implemented, sorry.",
		None,
		("product", ),
	),
	(
		"buildSummation",
		"summation ∑",
		"Will build summation. Not yet implemented, sorry.",
		None,
		("summation", ),
	),
	(
		"buildRadical",
		"radical √",
		"Will build radical. Not yet implemented, sorry.",
		None,
		("radical", ),
	),
)


class BuildSymbols(mekkaObject):
	prefDict = {"override": 0, "backupLayers": 0, "newTab": 1, "reuseTab": 1}
	# every implemented symbol is on by default:
	prefDict.update({symbol[0]: int(symbol[3] is not None) for symbol in SYMBOLS})

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

		for prefName, title, tooltip, builder, glyphNames in SYMBOLS:
			checkBox = vanilla.CheckBox("auto", title, value=True, callback=self.SavePreferences, sizeStyle='small')
			checkBox.setToolTip(tooltip)
			checkBox.enable(builder is not None)
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

		# Run Button:
		self.w.uncheckAllButton = vanilla.Button("auto", "Uncheck All", callback=self.checkAll)
		self.w.checkAllButton = vanilla.Button("auto", "Check All", callback=self.checkAll)
		self.w.uncheckAllButton.setToolTip("Unchecks all symbols.")
		self.w.checkAllButton.setToolTip("Checks all symbols that can be built.")
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
			"-row-[line(1)]-row-[override]-row-[newTab]-inset-[runButton]-inset-|",
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

	def checkAll(self, sender=None, onOrOff=True):
		if sender is self.w.uncheckAllButton:
			onOrOff = False
		for prefName, _, _, builder, _ in SYMBOLS:
			# symbols that are not yet implemented are never checked:
			self.setPref(prefName, onOrOff and builder is not None)
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

			# build glyphs:
			tabText = ""
			for prefName, _, _, builder, glyphNames in SYMBOLS:
				if not self.pref(prefName):
					continue
				print(f"\n🔣 Building {', '.join(glyphNames)}:")
				if builder is None:
					print("😢 Not yet implemented, sorry.")
					continue
				builder(font, override=override, backupLayers=backupLayers)
				tabText += tabStringForExistingGlyphs(font, glyphNames)

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
			print(f"Build Symbols Error: {e}")
			print(traceback.format_exc())


BuildSymbols()
