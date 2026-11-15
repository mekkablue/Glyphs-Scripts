# MenuTitle: Build Math Operators
__doc__ = """
Draws the math operators +−×÷=≠±≈¬ (optionally also <>≤≥ and ~^) from a few measurements: the stroke, the width of the plus, the sidebearings, and the height they are centered on. Or builds them from the stroke and length of your own minus. A live preview redraws the glyphs as you change the values.
"""

import math
import objc
import vanilla
from mekkablue import mekkaObject, newGlyphWithName, UpdateButton
from GlyphsApp import Glyphs, GSPath, GSNode, GSLINE, GSCURVE, GSOFFCURVE, GSMetricsTypeCapHeight, GSMetricsTypexHeight, Message
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSLineBreakByTruncatingTail,
	NSTextAlignmentRight,
)
from Foundation import NSNumberFormatter, NSPoint

mathOperators = "+−×÷=≠±≈¬"
lessGreater = "<>≤≥"
asciiOperators = "~^"
figureNames = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
zeroCandidates = ("zero.tf", "zero.tosf", "zero")  # for ‘same as zero’, in order of preference
fallbackStroke = 80  # if the master has no horizontal stem
minusTabScale = 0.735  # zoom of the tab for editing the minus

# Proportions of the shapes, relative to the stroke or to the length of the bars:
multiplyScale = 0.9  # bounding box of × relative to the length of the bars
chevronAngle = 30.0  # angle of the arms of < and > against the horizontal axis, in degrees
caretAngle = 45.0  # angle of the arms of ^ against the vertical axis, in degrees
slashAngle = 63.0  # angle of the slash in ≠ against the horizontal, in degrees
slashOverhang = 0.8  # how far the slash of ≠ reaches beyond the bars, in strokes
waveAmplitude = 0.09  # amplitude of the waves in ≈ and ~, relative to the length of the bars
waveHandleStart = 0.33  # Bézier handle lengths (fraction of a quarter wave) that approximate a sine wave
waveHandleEnd = 0.36
logicalNotLeg = 0.4  # length of the hook of ¬ relative to the length of the bars
kappa = 0.5522847498  # Bézier handle length for circles

scopeChoices = (
	"Current font, current master",
	"Current font, all masters",
	"All fonts, current master",
	"All fonts, all masters",
)


# ------------------------------------------------------------------------------
# Geometry. Pure functions, no Glyphs involved. A contour is a closed list of
# (x, y, isOffcurve) tuples. Shapes are built around (0, 0) and placed later.
# ------------------------------------------------------------------------------

def span(center, size):
	"""Returns integer (low, high) for a bar of that size around the center. Rounding the ends keeps the size."""
	size = int(round(size))
	low = int(round(center - size / 2.0))
	return low, low + size


def polygon(points):
	return [(x, y, False) for x, y in points]


def rectangle(xSpan, ySpan):
	return polygon(((xSpan[0], ySpan[0]), (xSpan[1], ySpan[0]), (xSpan[1], ySpan[1]), (xSpan[0], ySpan[1])))


def crossOutline(horizontalLength, verticalLength, horizontalStroke, verticalStroke, centerY=0):
	"""A plus as one 12-point contour."""
	left, right = span(0, horizontalLength)
	barLow, barHigh = span(centerY, horizontalStroke)
	stemLeft, stemRight = span(0, verticalStroke)
	bottom, top = span(centerY, verticalLength)
	return polygon((
		(left, barLow), (stemLeft, barLow), (stemLeft, bottom), (stemRight, bottom), (stemRight, barLow), (right, barLow),
		(right, barHigh), (stemRight, barHigh), (stemRight, top), (stemLeft, top), (stemLeft, barHigh), (left, barHigh),
	))


def ellipseOutline(xSpan, ySpan):
	"""Counterclockwise ellipse (a circle for equal spans), starting at the rightmost point."""
	left, right = xSpan
	bottom, top = ySpan
	centerX, centerY = (left + right) / 2.0, (bottom + top) / 2.0
	handleX, handleY = kappa * (right - left) / 2.0, kappa * (top - bottom) / 2.0
	return [
		(right, centerY, False), (right, centerY + handleY, True), (centerX + handleX, top, True),
		(centerX, top, False), (centerX - handleX, top, True), (left, centerY + handleY, True),
		(left, centerY, False), (left, centerY - handleY, True), (centerX - handleX, bottom, True),
		(centerX, bottom, False), (centerX + handleX, bottom, True), (right, centerY - handleY, True),
	]


def mapPoints(contour, function):
	return [function(x, y) + (isOffcurve, ) for x, y, isOffcurve in contour]


def translate(contour, shiftX, shiftY):
	return mapPoints(contour, lambda x, y: (x + shiftX, y + shiftY))


def mirrorHorizontally(contour):
	return mapPoints(contour, lambda x, y: (-x, y))


def rotate(contour, degrees):
	cosine, sine = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
	return mapPoints(contour, lambda x, y: (x * cosine - y * sine, x * sine + y * cosine))


def signedArea(contour):
	total = 0.0
	for index, (x1, y1, _) in enumerate(contour):
		x2, y2, _ = contour[(index + 1) % len(contour)]
		total += x1 * y2 - x2 * y1
	return total / 2.0


def counterclockwise(contour):
	"""Outer contours run counterclockwise in Glyphs. Reversing is safe because the node types follow from the neighbors."""
	return contour if signedArea(contour) > 0 else contour[::-1]


def bounds(contours):
	"""(minX, minY, maxX, maxY) of all points. Handles lie inside the curves of our shapes, so this is the bounding box."""
	xs = [x for contour in contours for x, y, _ in contour]
	ys = [y for contour in contours for x, y, _ in contour]
	return min(xs), min(ys), max(xs), max(ys)


def intersection(pointA, directionA, pointB, directionB):
	"""Intersection of two lines, each given by a point and a direction."""
	determinant = directionA[0] * directionB[1] - directionA[1] * directionB[0]
	parameter = ((pointB[0] - pointA[0]) * directionB[1] - (pointB[1] - pointA[1]) * directionB[0]) / determinant
	return pointA[0] + parameter * directionA[0], pointA[1] + parameter * directionA[1]


def chevronPoints(run, angle, upperStroke, lowerStroke, cutThickness):
	"""
	A mitered ‘>’ (tip pointing right) as a list of points. The centerlines of its arms meet at (0, 0), each arm runs
	`run` units to the left. The arms may differ in stroke. If cutThickness is more than 0, the pointy outer tip is cut
	off by a vertical line, at the place where the blunt end is that tall.
	"""
	theta = math.radians(angle)
	sine, cosine = math.sin(theta), math.cos(theta)
	tangent = sine / cosine
	upperDirection, lowerDirection = (-cosine, sine), (-cosine, -sine)
	upperNormal, lowerNormal = (sine, cosine), (sine, -cosine)  # point to the outer side of the arm
	halfUpper, halfLower = upperStroke / 2.0, lowerStroke / 2.0

	def offset(normal, distance):
		return normal[0] * distance, normal[1] * distance

	outerUpper, outerLower = offset(upperNormal, halfUpper), offset(lowerNormal, halfLower)
	innerUpper, innerLower = offset(upperNormal, -halfUpper), offset(lowerNormal, -halfLower)
	outerTip = intersection(outerUpper, upperDirection, outerLower, lowerDirection)
	innerTip = intersection(innerUpper, upperDirection, innerLower, lowerDirection)

	rise = run * tangent
	endUpper, endLower = (-run, rise), (-run, -rise)
	endPoints = (
		(endUpper[0] + outerUpper[0], endUpper[1] + outerUpper[1]),
		(endUpper[0] + innerUpper[0], endUpper[1] + innerUpper[1]),
		innerTip,
		(endLower[0] + innerLower[0], endLower[1] + innerLower[1]),
		(endLower[0] + outerLower[0], endLower[1] + outerLower[1]),
	)

	if cutThickness > 0:
		# the vertical distance between the outer edges grows linearly with the distance from the outer tip:
		cutX = (outerUpper[1] - outerLower[1] + tangent * (outerUpper[0] + outerLower[0]) - cutThickness) / (2.0 * tangent)
		# never cut beyond the inner tip, that would tear the stroke apart:
		cutX = min(max(cutX, innerTip[0] + 0.05 * (outerTip[0] - innerTip[0])), outerTip[0])
		upperY = outerUpper[1] + tangent * (outerUpper[0] - cutX)
		lowerY = outerLower[1] - tangent * (outerLower[0] - cutX)
		return [(cutX, upperY)] + list(endPoints) + [(cutX, lowerY)]
	return [outerTip] + list(endPoints)


def chevronOutline(angle, upperStroke, lowerStroke, cutThickness, width=None, height=None):
	"""A ‘>’ of that bounding box width, or else height, centered on (0, 0). The run of the arms is found by measuring."""
	probeRun = 100.0

	def measured(run):
		points = chevronPoints(run, angle, upperStroke, lowerStroke, cutThickness)
		xs, ys = [x for x, y in points], [y for x, y in points]
		return points, min(xs), max(xs), min(ys), max(ys)

	points, minX, maxX, minY, maxY = measured(probeRun)
	if width is not None:
		run = probeRun + width - (maxX - minX)  # width grows by one unit per unit of run
	else:
		run = probeRun + (height - (maxY - minY)) / (2.0 * math.tan(math.radians(angle)))  # height by two tangents per unit
	points, minX, maxX, minY, maxY = measured(max(run, 1.0))
	return polygon([(x - (minX + maxX) / 2.0, y - (minY + maxY) / 2.0) for x, y in points])


def waveOutline(length, stroke):
	"""One period of a sine-like wave, as a closed outline with vertical ends, centered on (0, 0)."""
	amplitude = waveAmplitude * length
	slope = 2.0 * math.pi * amplitude / length  # at the zero crossings
	# half-compensate the thinning of the stroke on slopes:
	thickness = stroke / math.cos(math.atan(slope) / 2.0)
	half = thickness / 2.0
	quarter = length / 4.0
	xs = [-length / 2.0 + index * quarter for index in range(5)]
	rise = waveHandleStart * (math.pi / 2.0) * amplitude
	centerline = [
		(xs[0], 0, False),
		(xs[0] + waveHandleStart * quarter, rise, True), (xs[1] - waveHandleEnd * quarter, amplitude, True), (xs[1], amplitude, False),
		(xs[1] + waveHandleEnd * quarter, amplitude, True), (xs[2] - waveHandleStart * quarter, rise, True), (xs[2], 0, False),
		(xs[2] + waveHandleStart * quarter, -rise, True), (xs[3] - waveHandleEnd * quarter, -amplitude, True), (xs[3], -amplitude, False),
		(xs[3] + waveHandleEnd * quarter, -amplitude, True), (xs[4] - waveHandleStart * quarter, -rise, True), (xs[4], 0, False),
	]
	upper = [(x, y + half, isOffcurve) for x, y, isOffcurve in centerline]
	lower = [(x, y - half, isOffcurve) for x, y, isOffcurve in centerline]
	return upper + lower[::-1], thickness


class Proportions(object):
	"""The dimensions all shapes of one master are built from. Whole units; italic angle 0 draws upright."""

	def __init__(self, length, stroke, overshoot, italicAngle, adaptPlusMinus, distance, secondaryDistance, miter, correction):
		self.length = int(round(length))
		self.stroke = int(round(stroke))
		self.overshoot = overshoot
		self.tangent = math.tan(math.radians(italicAngle))
		self.distance = int(round(distance))  # between the bars of = ≠ ≈
		self.secondaryDistance = int(round(secondaryDistance))  # in ÷ ± ≤ ≥
		self.miter = miter / 100.0
		self.correction = correction / 100.0
		self.adaptPlusMinus = adaptPlusMinus
		# a slanted vertical stem needs to be wider to look as strong as the horizontal stroke:
		self.verticalStroke = int(round(self.corrected((0, 1))))

	def slant(self, contour):
		if not self.tangent:
			return contour
		return mapPoints(contour, lambda x, y: (x + y * self.tangent, y))

	def corrected(self, direction):
		"""
		The thickness to draw a stroke with that direction (before slanting), so that it is as strong as the
		stroke after slanting. Slanting stretches the direction vector by `factor`, and thus thins the stroke by
		the same factor (windshield-wiper effect). Correction 0 is the pure geometric slant, 1 is full correction.
		"""
		directionX, directionY = direction
		length = math.hypot(directionX, directionY)
		factor = math.hypot(directionX / length + directionY / length * self.tangent, directionY / length)
		return self.stroke * (1 + self.correction * (factor - 1))


def minusShapes(p):
	return [p.slant(rectangle(span(0, p.length), span(0, p.stroke)))]


def plusShapes(p):
	return [p.slant(crossOutline(p.length, p.length, p.stroke, p.verticalStroke))]


def multiplyShapes(p):
	armLength = math.sqrt(2.0) * p.length * multiplyScale - p.stroke
	# after rotating, the horizontal bar runs up to the right, the vertical bar up to the left:
	return [p.slant(rotate(crossOutline(armLength, armLength, p.corrected((1, 1)), p.corrected((-1, 1))), 45))]


def divideShapes(p):
	shapes = minusShapes(p)
	diameter = int(round(p.stroke + 2 * p.overshoot))
	# the overshoot of the dots eats into the distance, so the distance is the one of a dot as wide as the stroke:
	offset = p.stroke / 2.0 + max(p.secondaryDistance - p.overshoot, 1) + diameter / 2.0
	for sign in (1, -1):
		# the dots follow the slant, but stay round:
		shapes.append(ellipseOutline(span(sign * offset * p.tangent, diameter), span(sign * offset, diameter)))
	return shapes


def equalShapes(p):
	height = 2 * p.stroke + p.distance
	top = int(round(height / 2.0))
	xSpan = span(0, p.length)
	return [
		p.slant(rectangle(xSpan, (top - p.stroke, top))),
		p.slant(rectangle(xSpan, (top - height, top - height + p.stroke))),
	]


def notEqualShapes(p):
	shapes = equalShapes(p)
	halfHeight = p.stroke + p.distance / 2.0 + slashOverhang * p.stroke
	slashStroke = p.corrected((math.cos(math.radians(slashAngle)), math.sin(math.radians(slashAngle))))
	halfWidth = slashStroke / math.sin(math.radians(slashAngle)) / 2.0  # horizontal half width for the stroke thickness
	run = halfHeight / math.tan(math.radians(slashAngle))
	shapes.append(p.slant(polygon((
		(-run - halfWidth, -halfHeight), (-run + halfWidth, -halfHeight),
		(run + halfWidth, halfHeight), (run - halfWidth, halfHeight),
	))))
	return shapes


def plusMinusShapes(p):
	if p.adaptPlusMinus:
		stemLength = max(p.length - p.secondaryDistance - p.stroke, 2 * p.stroke)  # as tall as the plus
	else:
		stemLength = p.length
	height = stemLength + p.secondaryDistance + p.stroke
	top = int(round(height / 2.0))
	bottom = top - height
	plus = crossOutline(p.length, stemLength, p.stroke, p.verticalStroke, centerY=top - stemLength / 2.0)
	minus = rectangle(span(0, p.length), (bottom, bottom + p.stroke))
	return [p.slant(plus), p.slant(minus)]


def logicalNotShapes(p):
	left, right = span(0, p.length)
	barLow, barHigh = span(0, p.stroke)
	legLow = barLow - int(round(logicalNotLeg * p.length))
	stemLeft = right - p.verticalStroke
	return [p.slant(polygon((
		(left, barLow), (stemLeft, barLow), (stemLeft, legLow), (right, legLow), (right, barHigh), (left, barHigh),
	)))]


def approxEqualShapes(p):
	wave, thickness = waveOutline(p.length, p.stroke)
	offset = (thickness + p.distance) / 2.0
	return [p.slant(translate(wave, 0, offset)), p.slant(translate(wave, 0, -offset))]


def tildeShapes(p):
	wave, thickness = waveOutline(p.length, p.stroke)
	return [p.slant(wave)]


def chevronStrokes(p, angle, mirrored):
	"""Thickness of the upper and the lower arm of < or >, corrected for the slant."""
	directionX = math.cos(math.radians(angle)) * (1 if mirrored else -1)
	directionY = math.sin(math.radians(angle))
	return p.corrected((directionX, directionY)), p.corrected((directionX, -directionY))


def chevronShape(p, mirrored, angle=chevronAngle):
	"""
	< or >, with the apex cut off by the Miter value. The apex reaches beyond the arm ends by the overshoot, since
	a pointed shape looks shorter than it is.
	"""
	upperStroke, lowerStroke = chevronStrokes(p, angle, mirrored)
	outline = chevronOutline(angle, upperStroke, lowerStroke, p.miter * p.stroke, width=p.length + p.overshoot)
	return mirrorHorizontally(outline) if mirrored else outline


def greaterShapes(p):
	return [p.slant(chevronShape(p, False))]


def lessShapes(p):
	return [p.slant(chevronShape(p, True))]


def chevronWithBar(p, mirrored):
	"""< or > with a bar underneath. Same total height as the plain chevron, so the chevron gets flatter."""
	barBlock = p.secondaryDistance + p.stroke

	def heightOf(contour):
		minX, minY, maxX, maxY = bounds([contour])
		return maxY - minY

	targetHeight = heightOf(chevronShape(p, mirrored)) - barBlock
	low, high = 5.0, chevronAngle
	if heightOf(chevronShape(p, mirrored, low)) >= targetHeight:
		angle = low
	else:
		for _ in range(30):
			angle = (low + high) / 2.0
			if heightOf(chevronShape(p, mirrored, angle)) < targetHeight:
				low = angle
			else:
				high = angle
		angle = (low + high) / 2.0
	chevron = chevronShape(p, mirrored, angle)
	minX, minY, maxX, maxY = bounds([chevron])
	total = (maxY - minY) + barBlock
	chevron = translate(chevron, 0, total / 2.0 - (maxY - minY) / 2.0)
	bottom = int(round(-total / 2.0))
	# the bar is as long as the arms reach, so only the apex overshoots:
	barEnd = int(round(maxX if mirrored else minX + p.length))
	bar = rectangle((barEnd - p.length, barEnd), (bottom, bottom + p.stroke))
	return [p.slant(chevron), p.slant(bar)]


def lessEqualShapes(p):
	return chevronWithBar(p, True)


def greaterEqualShapes(p):
	return chevronWithBar(p, False)


def caretShapes(p):
	"""A chevron pointing up, as wide as the bars are long. Built as ‘>’ and rotated, so its arms run down to the sides."""
	theta = math.radians(caretAngle)
	upperStroke = p.corrected((-math.sin(theta), -math.cos(theta)))
	lowerStroke = p.corrected((math.sin(theta), -math.cos(theta)))
	return [p.slant(rotate(chevronOutline(caretAngle, upperStroke, lowerStroke, 0, height=p.length), 90))]


shapeBuilders = {
	"+": plusShapes,
	"−": minusShapes,
	"×": multiplyShapes,
	"÷": divideShapes,
	"=": equalShapes,
	"≠": notEqualShapes,
	"±": plusMinusShapes,
	"≈": approxEqualShapes,
	"¬": logicalNotShapes,
	"<": lessShapes,
	">": greaterShapes,
	"≤": lessEqualShapes,
	"≥": greaterEqualShapes,
	"~": tildeShapes,
	"^": caretShapes,
}


def placedShapes(character, plan):
	"""
	The contours of the operator for one master: centered in the width, on the center height, rounded to whole units.
	Everything is built and centered by its bounding box, so LSB and RSB are equal (RSB =|).
	A bounding box with the wrong parity cannot be centered on whole units, so we try a bar one unit shorter or longer.
	"""
	width = plan["width"]
	for lengthChange in (0, -1, 1):
		p = Proportions(
			plan["length"] + lengthChange, plan["stroke"], plan["overshoot"], plan["italicAngle"], plan["adaptPlusMinus"],
			plan["distance"], plan["secondaryDistance"], plan["miter"], plan["correction"],
		)
		contours = [counterclockwise(contour) for contour in shapeBuilders[character](p)]
		if character == "^":
			shiftY = plan["capHeight"] - bounds(contours)[3]  # the tip touches the cap height
		else:
			shiftY = plan["centerY"]
		contours = [mapPoints(contour, lambda x, y: (round(x), round(y + shiftY))) for contour in contours]
		minX, minY, maxX, maxY = bounds(contours)
		if (width - (maxX - minX)) % 2 == 0:
			break
	shiftX = (width - minX - maxX) / 2.0
	return [translate(contour, shiftX, 0) for contour in contours]


# ------------------------------------------------------------------------------
# Glyphs helpers
# ------------------------------------------------------------------------------

class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def integerFormatter(minimum=None, maximum=None):
	"""Number formatter that only accepts integers, optionally within a range."""
	formatter = NSNumberFormatter.alloc().init()
	formatter.setAllowsFloats_(False)
	if minimum is not None:
		formatter.setMinimum_(minimum)
	if maximum is not None:
		formatter.setMaximum_(maximum)
	return formatter


def metricPosition(font, master, metricType):
	"""Returns the position of the (unfiltered) metric of that type in the master, or None."""
	for metric in font.metrics:
		if metric.type == metricType and metric.filter is None:
			return master.metrics[metric.id].position
	return None


def firstHorizontalStem(font, master):
	"""The first horizontal stem of the master, or None."""
	for index, stem in enumerate(font.stems):
		if stem.horizontal:
			value = master.stems[index]
			if value and value > 0:
				return value
	return None


def figureSuffixesOfFont(font):
	"""Suffixes of all zero glyphs (‘’, ‘.tf’, ‘.tosf’, …), tabular ones first."""
	suffixes = [glyph.name[len("zero"):] for glyph in font.glyphs if glyph.name == "zero" or glyph.name.startswith("zero.")]
	preferred = {".tf": 0, ".tosf": 1, "": 2}
	return sorted(suffixes, key=lambda suffix: (preferred.get(suffix, 3), suffix)) or [""]


def pathFromContour(contour):
	"""A closed GSPath. An on-curve node is a curve node if it follows a handle, and smooth if handles are on both sides."""
	path = GSPath()
	count = len(contour)
	for index, (x, y, isOffcurve) in enumerate(contour):
		previousIsOffcurve = contour[index - 1][2]
		nextIsOffcurve = contour[(index + 1) % count][2]
		if isOffcurve:
			nodeType = GSOFFCURVE
		else:
			nodeType = GSCURVE if previousIsOffcurve else GSLINE
		node = GSNode(NSPoint(x, y), type=nodeType)
		if not isOffcurve and previousIsOffcurve and nextIsOffcurve:
			node.smooth = True
		path.nodes.append(node)
	path.closed = True
	return path


class BuildMathOperators(mekkaObject):
	prefDict = {
		"drawMode": 0,
		"widthMode": 1,
		"plusWidth": 600,
		"plusWidthGlyph": "zero.tf",
		"centerMode": 0,
		"centerGlyphs": "n, zero, eight",
		"sidebearing": 70,
		"overshoot": 10,
		"distance": 100,
		"distance2": 100,
		"miter": 80,
		"wiper": 100,
		"italic": True,
		"adaptPlusMinus": True,
		"includeLessGreater": False,
		"includeAscii": False,
		"overwrite": True,
		"backup": True,
		"scope": 0,
	}

	def __init__(self):
		windowWidth = 480
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Build Math Operators",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)
		self.backedUp = set()  # layers whose previous outlines we already looked at in this session
		self.drawnLayers = set()  # layers drawn by this script in this session: the live preview may always redraw them
		font = Glyphs.font
		self.figureSuffixes = figureSuffixesOfFont(font)

		self.w.descriptionText = vanilla.TextBox(
			"auto",
			"Draws +−×÷=≠±≈¬ with the widths, sidebearings and heights below. Changes show live in the font.",
			sizeStyle="small",
			selectable=True,
		)

		self.w.drawMode = vanilla.VerticalRadioGroup("auto", ("Draw from scratch", "Take from minus"), callback=self.SavePreferences, sizeStyle="small")
		self.w.drawMode.setToolTip("From scratch: the stroke comes from the field below. From minus: the stroke is the thickness of your minus. The minus itself is redrawn like all other operators, so only its thickness counts.")

		tooltipText = "Width of the plus. All other operators get the same width, and RSB =|."
		self.w.widthLabel = vanilla.TextBox("auto", "Plus width:", sizeStyle="small")
		self.w.widthLabel.setToolTip(tooltipText)
		self.w.widthMode = vanilla.PopUpButton("auto", ("Number", "Same as zero", "Same as glyph…"), callback=self.SavePreferences, sizeStyle="small")
		self.w.widthMode.setToolTip("Number: width in units. Same as zero: width of zero.tf, or else zero.tosf, or else zero, in each master. Same as glyph: width of the glyph in the field.")
		self.w.plusWidth = SteppingEditText("auto", "600", formatter=integerFormatter(1), callback=self.SavePreferences, sizeStyle="small")
		self.w.plusWidth.setToolTip("Width of the plus in units. Use the arrow keys to step.")
		self.w.plusWidthGlyph = vanilla.EditText("auto", "zero.tf", callback=self.SavePreferences, sizeStyle="small")
		self.w.plusWidthGlyph.setToolTip("Name of the glyph whose width the plus takes.")

		tooltipText = "The operators are vertically centered on this height. The caret ^ is the exception: its tip touches the cap height."
		self.w.centerLabel = vanilla.TextBox("auto", "Center on:", sizeStyle="small")
		self.w.centerLabel.setToolTip(tooltipText)
		self.w.centerMode = vanilla.PopUpButton("auto", ("Half cap height", "Half x-height", "Center of figures", "Center of glyphs"), callback=self.SavePreferences, sizeStyle="small")
		self.w.centerMode.setToolTip(tooltipText)
		self.w.figureStyle = vanilla.PopUpButton("auto", ["zero" + suffix for suffix in self.figureSuffixes], callback=self.SavePreferences, sizeStyle="small")
		self.w.figureStyle.setToolTip("Which figures to average: the vertical centers of their bounding boxes.")
		self.w.centerGlyphs = vanilla.EditText("auto", "n, zero, eight", callback=self.SavePreferences, sizeStyle="small")
		self.w.centerGlyphs.setToolTip("Comma-separated glyph names. The average of the vertical centers of their bounding boxes is the center height.")

		tooltipText = "Distance between the shape and the edge of the glyph, on each side, in units."
		self.w.sidebearingLabel = vanilla.TextBox("auto", "Sidebearings:", sizeStyle="small")
		self.w.sidebearingLabel.setToolTip(tooltipText)
		self.w.sidebearing = SteppingEditText("auto", "70", formatter=integerFormatter(0), callback=self.SavePreferences, sizeStyle="small")
		self.w.sidebearing.setToolTip(tooltipText)
		self.w.sidebearingText = vanilla.TextBox("auto", "units, left and right", sizeStyle="small")

		tooltipText = "Stroke thickness in units. Preset with the first horizontal stem of the current master. Not used if you take the thickness from the minus."
		self.w.strokeLabel = vanilla.TextBox("auto", "Stroke:", sizeStyle="small")
		self.w.strokeLabel.setToolTip(tooltipText)
		self.w.stroke = SteppingEditText("auto", "80", formatter=integerFormatter(1), callback=self.SavePreferences, sizeStyle="small")
		self.w.stroke.setToolTip(tooltipText)
		self.w.resetStroke = UpdateButton("auto", callback=self.resetStroke)
		self.w.resetStroke.setToolTip("Resets the stroke to the first horizontal stem of the current master.")
		self.w.strokeText = vanilla.TextBox("auto", "units, first horizontal stem", sizeStyle="small")

		tooltipText = "Optical compensation, in units. Each dot of ÷ is as wide as the stroke plus twice this value, so the circles do not look smaller than the bar. The apex of < > ≤ ≥ reaches this far beyond the ends of its arms."
		self.w.overshootLabel = vanilla.TextBox("auto", "Overshoot:", sizeStyle="small")
		self.w.overshootLabel.setToolTip(tooltipText)
		self.w.overshoot = SteppingEditText("auto", "10", formatter=integerFormatter(0), callback=self.SavePreferences, sizeStyle="small")
		self.w.overshoot.setToolTip(tooltipText)
		self.w.overshootText = vanilla.TextBox("auto", "units, dots in ÷, apex of <>≤≥", sizeStyle="small")

		tooltipText = "Space between the bars of = ≠ ≈, from edge to edge, in units."
		self.w.distanceLabel = vanilla.TextBox("auto", "Distance:", sizeStyle="small")
		self.w.distanceLabel.setToolTip(tooltipText)
		self.w.distance = SteppingEditText("auto", "100", formatter=integerFormatter(1), callback=self.SavePreferences, sizeStyle="small")
		self.w.distance.setToolTip(tooltipText)
		self.w.distanceText = vanilla.TextBox("auto", "units, between the bars of = ≠ ≈", sizeStyle="small")

		tooltipText = "Space between the plus and the minus in ±, between the chevron and the bar in ≤ ≥, and between the dots and the minus in ÷. In units, from edge to edge. In ÷ the overshoot of the dots is subtracted: the distance is the one of a dot that is as wide as the stroke."
		self.w.distance2Label = vanilla.TextBox("auto", "Distance 2:", sizeStyle="small")
		self.w.distance2Label.setToolTip(tooltipText)
		self.w.distance2 = SteppingEditText("auto", "100", formatter=integerFormatter(1), callback=self.SavePreferences, sizeStyle="small")
		self.w.distance2.setToolTip(tooltipText)
		self.w.distance2Text = vanilla.TextBox("auto", "units, in ÷ ± ≤ ≥", sizeStyle="small")

		tooltipText = "Cuts off the pointed apex of < > ≤ ≥ with a vertical line (parallel to the italic angle in slanted masters), so that the blunt end is this percentage of the stroke tall. 0 keeps the sharp point."
		self.w.miterLabel = vanilla.TextBox("auto", "Miter:", sizeStyle="small")
		self.w.miterLabel.setToolTip(tooltipText)
		self.w.miter = SteppingEditText("auto", "80", formatter=integerFormatter(0, 200), callback=self.SavePreferences, sizeStyle="small")
		self.w.miter.setToolTip(tooltipText)
		self.w.miterText = vanilla.TextBox("auto", "% of the stroke, in <>≤≥", sizeStyle="small")

		tooltipText = "Slanting thins strokes that are neither horizontal nor vertical, like the arms of × (windshield-wiper effect). This corrects the thickness of vertical and diagonal strokes in + × ≠ ± ¬ < > ≤ ≥ and ^. 100 is full correction, 0 is the pure geometric slant. Without ‘Respect italic angle’ all operators are upright."
		self.w.wiperLabel = vanilla.TextBox("auto", "Wiper correction:", sizeStyle="small")
		self.w.wiperLabel.setToolTip(tooltipText)
		self.w.wiper = SteppingEditText("auto", "100", formatter=integerFormatter(0, 100), callback=self.SavePreferences, sizeStyle="small")
		self.w.wiper.setToolTip(tooltipText)
		self.w.wiperText = vanilla.TextBox("auto", "% (100 = full, 0 = pure slant)", sizeStyle="small")

		self.w.italic = vanilla.CheckBox("auto", "Respect italic angle", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.italic.setToolTip("Slants the shapes by the italic angle of each master, and widens vertical strokes so that they keep the thickness of the horizontal ones. Off: upright shapes.")
		self.w.adaptPlusMinus = vanilla.CheckBox("auto", "Adapt height in ±", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.adaptPlusMinus.setToolTip("Shortens the vertical stroke of the plus in ±, so that ± is as tall as the plus. Off: ± is a full plus with a minus underneath, and taller than the plus.")
		self.w.includeLessGreater = vanilla.CheckBox("auto", "Include %s" % lessGreater, value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeLessGreater.setToolTip("Also draws less, greater, lessequal and greaterequal.")
		self.w.includeAscii = vanilla.CheckBox("auto", "Include %s" % asciiOperators, value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeAscii.setToolTip("Also draws asciitilde and asciicircum.")

		self.w.overwrite = vanilla.CheckBox("auto", "Overwrite existing", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwrite.setToolTip("Replaces the outlines of operators that already have some. Off: layers with outlines are left alone, and only empty layers are drawn. Layers drawn by this script in this session can always be redrawn by the live preview.")
		self.w.backup = vanilla.CheckBox("auto", "Backup in background", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.backup.setToolTip("Before a layer is overwritten for the first time in this session, copies its outlines into the background. Does nothing if the background already holds something.")

		tooltipText = "Which fonts and masters are drawn. Stroke, sidebearings and overshoot are the same in all masters of the scope."
		self.w.scopeLabel = vanilla.TextBox("auto", "Scope:", sizeStyle="small")
		self.w.scopeLabel.setToolTip(tooltipText)
		self.w.scope = vanilla.PopUpButton("auto", scopeChoices, callback=self.SavePreferences, sizeStyle="small")
		self.w.scope.setToolTip(tooltipText)

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")

		self.w.editMinusButton = vanilla.Button("auto", "Edit minus", callback=self.editMinus, sizeStyle="small")
		self.w.editMinusButton.setToolTip("Switches to ‘Take from minus’ and shows the minus in a tab for editing, in all fonts of the scope (an existing minus tab is reused). Change the thickness of the minus, then click Draw to redraw all operators with it.")
		self.w.tabButton = vanilla.Button("auto", "Open Tab", callback=self.openTab)
		self.w.tabButton.setToolTip("Opens a new Edit tab with the operators.")
		self.w.drawButton = vanilla.Button("auto", "Draw", callback=self.drawButtonCallback)
		self.w.drawButton.setToolTip("Draws all operators with the current values, and reports in the Macro Window.")
		self.w.setDefaultButton(self.w.drawButton)

		# secondary info text takes a semantic color:
		for hint in (self.w.sidebearingText, self.w.strokeText, self.w.overshootText, self.w.distanceText, self.w.distance2Text, self.w.miterText, self.w.wiperText):
			hint.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		# the status line shortens instead of widening the window:
		self.w.status.getNSTextField().setLineBreakMode_(NSLineBreakByTruncatingTail)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		# the description wraps: it takes the width it is given instead of demanding one long line
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# the labels end at one x-position:
		labelNames = ("widthLabel", "centerLabel", "sidebearingLabel", "strokeLabel", "overshootLabel", "distanceLabel", "distance2Label", "miterLabel", "wiperLabel", "scopeLabel")
		widestLabel = "wiperLabel"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		# the fields behind the popups: the one for glyph names stretches, the number does not
		self.w.plusWidth.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.plusWidthGlyph.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.centerGlyphs.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.figureStyle.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and buttons stretch vertically by default; hugging makes the window as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		def aligned(viewName, otherName, attribute):
			return {"view1": getattr(self.w, viewName), "attribute1": attribute, "view2": getattr(self.w, otherName), "attribute2": attribute}

		rules = [
			"H:|-inset-[descriptionText]-inset-|",
			"H:|-inset-[drawMode]-gap-[editMinusButton]-(>=inset)-|",
			"H:|-inset-[widthLabel]-gap-[widthMode]-gap-[plusWidth(>=60)]-gap-[plusWidthGlyph(>=90)]-inset-|",
			"H:|-inset-[centerLabel]-gap-[centerMode]-gap-[figureStyle(>=60)]-gap-[centerGlyphs(>=90)]-inset-|",
			"H:|-inset-[sidebearingLabel]-gap-[sidebearing(60)]-gap-[sidebearingText]-(>=inset)-|",
			"H:|-inset-[strokeLabel]-gap-[stroke(60)]-gap-[resetStroke]-gap-[strokeText]-(>=inset)-|",
			"H:|-inset-[overshootLabel]-gap-[overshoot(60)]-gap-[overshootText]-(>=inset)-|",
			"H:|-inset-[distanceLabel]-gap-[distance(60)]-gap-[distanceText]-(>=inset)-|",
			"H:|-inset-[distance2Label]-gap-[distance2(60)]-gap-[distance2Text]-(>=inset)-|",
			"H:|-inset-[miterLabel]-gap-[miter(60)]-gap-[miterText]-(>=inset)-|",
			"H:|-inset-[wiperLabel]-gap-[wiper(60)]-gap-[wiperText]-(>=inset)-|",
			"H:|-inset-[italic]-gap-[includeLessGreater]-(>=inset)-|",
			"H:|-inset-[adaptPlusMinus]-gap-[includeAscii]-(>=inset)-|",
			"H:|-inset-[scopeLabel]-gap-[scope]-inset-|",
			"H:|-inset-[status]-inset-|",
			"H:|-inset-[tabButton]-(>=inset)-[drawButton(>=70)]-inset-|",
			(
				"V:|-inset-[descriptionText(42)]-row-[drawMode(radioHeight)]-section-[widthMode]-row-[centerMode]-section-[sidebearing]-row-[stroke]-row-[overshoot]-row-[distance]-row-[distance2]-row-[miter]-row-[wiper]"
				"-section-[italic]-checkRow-[adaptPlusMinus]-section-[scope]-section-[overwrite]-checkRow-[backup]-section-[status]-inset-[drawButton]-inset-|"
			),
			"V:[tabButton]-inset-|",
			aligned("widthMode", "centerMode", "width"),
			# the button sits next to the last radio button, the one for the minus:
			aligned("editMinusButton", "drawMode", "bottom"),
			# two columns of options; the second column follows the widest checkbox of the first
			aligned("adaptPlusMinus", "italic", "width"),
			aligned("includeLessGreater", "italic", "centerY"),
			aligned("includeAscii", "adaptPlusMinus", "centerY"),
			aligned("includeAscii", "includeLessGreater", "leading"),
			# the overwrite options sit under the Scope popup
			aligned("overwrite", "scope", "leading"),
			aligned("backup", "scope", "leading"),
			aligned("plusWidth", "figureStyle", "width"),
			aligned("plusWidthGlyph", "centerGlyphs", "width"),
		]
		rules += [aligned(labelName, widestLabel, "width") for labelName in labelNames if labelName != widestLabel]
		# everything in a row sits on the vertical center of its field:
		rowFields = (
			("widthMode", ("widthLabel", "plusWidth", "plusWidthGlyph")),
			("centerMode", ("centerLabel", "figureStyle", "centerGlyphs")),
			("sidebearing", ("sidebearingLabel", "sidebearingText")),
			("stroke", ("strokeLabel", "resetStroke", "strokeText")),
			("overshoot", ("overshootLabel", "overshootText")),
			("distance", ("distanceLabel", "distanceText")),
			("distance2", ("distance2Label", "distance2Text")),
			("miter", ("miterLabel", "miterText")),
			("wiper", ("wiperLabel", "wiperText")),
			("scope", ("scopeLabel", )),
		)
		for fieldName, otherNames in rowFields:
			for otherName in otherNames:
				rules.append(aligned(otherName, fieldName, "centerY"))
		self.w.addAutoPosSizeRules(rules, metrics={"inset": 15, "gap": 8, "row": 8, "section": 12, "checkRow": 5, "radioHeight": self.w.drawMode.getFittingHeight()})

		# the stroke is a property of the font, not of this script, so it is preset and not remembered:
		self.w.stroke.set(str(self.presetStroke(font)))

		self.LoadPreferences()
		storedSuffix = self.pref("figureStyle")
		if storedSuffix in self.figureSuffixes:
			self.w.figureStyle.set(self.figureSuffixes.index(storedSuffix))
		self.updateUI()

		self.w.open()
		self.w.makeKey()

	# ------------------------------------------------------------------ UI

	def updateUI(self, sender=None):
		fromScratch = self.w.drawMode.get() == 0
		for field in (self.w.stroke, self.w.resetStroke):
			field.enable(fromScratch)
		widthMode = self.w.widthMode.get()
		self.w.plusWidth.enable(widthMode == 0)
		self.w.plusWidthGlyph.enable(widthMode == 2)
		centerMode = self.w.centerMode.get()
		self.w.figureStyle.enable(centerMode == 2)
		self.w.centerGlyphs.enable(centerMode == 3)
		self.w.backup.enable(self.w.overwrite.get())
		self.w.wiper.enable(self.w.italic.get())

	def SavePreferences(self, sender=None):
		super().SavePreferences(sender)
		self.setPref("figureStyle", self.figureSuffix())
		# live preview:
		self.draw()

	def setStatus(self, text):
		"""Sets the status line and redraws it right away, so it shows while the script is busy."""
		self.w.status.set(text)
		self.w.status.getNSTextField().display()

	def figureSuffix(self):
		index = self.w.figureStyle.get()
		if 0 <= index < len(self.figureSuffixes):
			return self.figureSuffixes[index]
		return ""

	def presetStroke(self, font):
		stem = firstHorizontalStem(font, font.selectedFontMaster)
		return int(round(stem)) if stem else fallbackStroke

	def resetStroke(self, sender=None):
		font = Glyphs.font
		if font:
			self.w.stroke.set(str(self.presetStroke(font)))
			self.draw()

	def drawButtonCallback(self, sender):
		super().SavePreferences(sender)  # take the current UI state, but do not preview twice
		self.setPref("figureStyle", self.figureSuffix())
		self.draw(report=True)

	def tabText(self):
		lines = [mathOperators]
		if self.w.includeLessGreater.get():
			lines.append(lessGreater)
		if self.w.includeAscii.get():
			lines.append(asciiOperators)
		return "\n".join("".join("/%s" % Glyphs.niceGlyphName(character) for character in line) for line in lines)

	def openTab(self, sender):
		font = Glyphs.font
		if font:
			font.newTab(self.tabText())

	def editMinus(self, sender):
		font = Glyphs.font
		if not font:
			return
		# fonts without a minus in the masters of the scope have nothing to edit yet, so start with a drawn minus there:
		lacking = [scopeFont for scopeFont, masterIDs in self.targets(self.prefInt("scope")) if self.lacksMinus(scopeFont, masterIDs)]
		if lacking:
			self.draw(forceFromScratch=True, onlyFonts=lacking)
		self.w.drawMode.set(1)
		self.SavePreferences()
		# every font of the scope shows its minus, the current font last so that it stays in front:
		fonts = sorted((scopeFont for scopeFont, masterIDs in self.targets(self.prefInt("scope"))), key=lambda scopeFont: scopeFont == font)
		for scopeFont in fonts:
			self.showMinus(scopeFont)

	def lacksMinus(self, font, masterIDs):
		minusGlyph = font.glyphs["minus"]
		for master in font.masters:
			if masterIDs is None or master.id in masterIDs:
				if minusGlyph is None or len(minusGlyph.layers[master.id].shapes) == 0:
					return True
		return False

	def showMinus(self, font):
		"""Selects the tab with the minus in the font (or opens it), with the minus open for editing, zoomed and centered."""
		tab = None
		for existingTab in font.tabs:
			if existingTab.text.strip() in ("/minus", "−"):
				tab = existingTab
				break
		if tab is None:
			tab = font.newTab("/minus")
		else:
			font.currentTab = tab
		tab.textCursor = 0  # the minus is the active layer
		tab.scale = minusTabScale
		tab.initialZoom()

	# ------------------------------------------------------------------ Settings and plans

	def settings(self, forceFromScratch=False):
		"""Returns the settings as a dictionary, or None while the fields hold no valid numbers."""
		try:
			settings = {
				"stroke": int(round(float(self.w.stroke.get()))),
				"sidebearing": int(round(float(self.pref("sidebearing")))),
				"overshoot": int(round(float(self.pref("overshoot")))),
				"distance": int(round(float(self.pref("distance")))),
				"secondaryDistance": int(round(float(self.pref("distance2")))),
				"miter": float(self.pref("miter")),
				"wiper": float(self.pref("wiper")),
				"plusWidth": int(round(float(self.pref("plusWidth")))),
			}
		except (TypeError, ValueError):
			return None
		if settings["stroke"] < 1 or settings["plusWidth"] < 1 or settings["sidebearing"] < 0 or settings["overshoot"] < 0 or settings["distance"] < 1 or settings["secondaryDistance"] < 1 or settings["miter"] < 0 or not 0 <= settings["wiper"] <= 100:
			return None
		settings["takeFromMinus"] = self.prefInt("drawMode") == 1 and not forceFromScratch
		settings["widthMode"] = self.prefInt("widthMode")
		settings["plusWidthGlyph"] = str(self.pref("plusWidthGlyph")).strip()
		settings["centerMode"] = self.prefInt("centerMode")
		settings["centerGlyphs"] = str(self.pref("centerGlyphs"))
		settings["figureSuffix"] = self.figureSuffix()
		settings["overwrite"] = self.prefBool("overwrite")
		settings["backup"] = self.prefBool("backup") and settings["overwrite"]
		settings["italic"] = self.prefBool("italic")
		settings["adaptPlusMinus"] = self.prefBool("adaptPlusMinus")
		characters = mathOperators
		if self.prefBool("includeLessGreater"):
			characters += lessGreater
		if self.prefBool("includeAscii"):
			characters += asciiOperators
		settings["characters"] = characters
		settings["scope"] = self.prefInt("scope")
		return settings

	def targets(self, scope):
		"""Returns (font, master IDs) tuples according to the scope. Master IDs are None for all masters."""
		fonts = list(Glyphs.fonts) if scope in (2, 3) else ([Glyphs.font] if Glyphs.font else [])
		return [(font, None if scope in (1, 3) else {font.selectedFontMaster.id}) for font in fonts]

	def widthOf(self, font, master, settings):
		"""Returns (width, problem)."""
		widthMode = settings["widthMode"]
		if widthMode == 0:
			return settings["plusWidth"], None
		if widthMode == 1:
			names = zeroCandidates
		else:
			names = (settings["plusWidthGlyph"], )
		for name in names:
			glyph = font.glyphs[name] if name else None
			if glyph is not None:
				return int(round(glyph.layers[master.id].width)), None
		return None, "no %s to take the width from" % " or ".join(name for name in names if name)

	def centerOf(self, font, master, settings):
		"""Returns (center height, problem)."""
		centerMode = settings["centerMode"]
		if centerMode in (0, 1):
			metricType = GSMetricsTypeCapHeight if centerMode == 0 else GSMetricsTypexHeight
			height = metricPosition(font, master, metricType)
			if height is None:
				return None, "no %s metric" % ("cap height" if centerMode == 0 else "x-height")
			return int(round(height / 2.0)), None
		if centerMode == 2:
			names = [figure + settings["figureSuffix"] for figure in figureNames]
			required = False
		else:
			names = [name.strip() for name in settings["centerGlyphs"].split(",") if name.strip()]
			required = True
		middles = []
		for name in names:
			glyph = font.glyphs[name]
			if glyph is None:
				if required:
					return None, "no glyph %s to center on" % name
				continue
			layer = glyph.layers[master.id]
			if len(layer.shapes) > 0:
				middles.append(layer.bounds.origin.y + layer.bounds.size.height / 2.0)
		if not middles:
			return None, "no outlines in %s to center on" % (", ".join(names) or "an empty list")
		return int(round(sum(middles) / len(middles))), None

	def planMaster(self, font, master, settings):
		"""Returns (plan, problem): all measurements needed to draw the operators in this master."""
		italicAngle = master.italicAngle if settings["italic"] else 0.0
		overhang = abs(math.tan(math.radians(italicAngle)))  # a slanted bar is wider than it is long

		width, problem = self.widthOf(font, master, settings)
		if problem:
			return None, problem
		centerY, problem = self.centerOf(font, master, settings)
		if problem:
			return None, problem
		capHeight = metricPosition(font, master, GSMetricsTypeCapHeight)
		if capHeight is None and "^" in settings["characters"]:
			return None, "no cap height metric for the caret"

		if settings["takeFromMinus"]:
			minusGlyph = font.glyphs["minus"]
			minusLayer = minusGlyph.layers[master.id] if minusGlyph is not None else None
			if minusLayer is None or len(minusLayer.shapes) == 0:
				return None, "the minus has no outlines. Draw it first, or draw from scratch"
			stroke = int(round(minusLayer.bounds.size.height))  # only the thickness counts, the minus is redrawn
		else:
			stroke = settings["stroke"]
		length = int(round(width - 2 * settings["sidebearing"] - stroke * overhang))
		if length < 2 * stroke:
			return None, "width %i leaves bars of only %i units for a stroke of %i" % (width, length, stroke)

		return {
			"width": width,
			"centerY": centerY,
			"capHeight": capHeight,
			"stroke": stroke,
			"length": length,
			"overshoot": settings["overshoot"],
			"distance": settings["distance"],
			"secondaryDistance": settings["secondaryDistance"],
			"miter": settings["miter"],
			"correction": settings["wiper"],
			"italicAngle": italicAngle,
			"adaptPlusMinus": settings["adaptPlusMinus"],
		}, None

	# ------------------------------------------------------------------ Drawing

	def backUp(self, glyph, layer):
		"""Once per session, copies the outlines into the background, unless the background holds something already."""
		key = (glyph.name, layer.layerId)
		if key in self.backedUp:
			return
		self.backedUp.add(key)
		if len(layer.shapes) == 0 or len(layer.background.shapes) > 0:
			return
		for shape in layer.shapes:
			layer.background.shapes.append(shape.copy())
		layer.background.decomposeComponents()

	def drawFont(self, font, masterIDs, settings, report):
		"""Draws the operators in the masters of the font. All masters or none, so they stay compatible. Returns (layer count, problems)."""
		masters = [master for master in font.masters if masterIDs is None or master.id in masterIDs]
		plans, problems = [], []
		for master in masters:
			plan, problem = self.planMaster(font, master, settings)
			if problem:
				problems.append("%s: %s" % (master.name, problem))
			else:
				plans.append((master, plan))
		if problems:
			return 0, 0, problems

		glyphs = {}
		for character in settings["characters"]:
			glyphName = Glyphs.niceGlyphName(character)
			glyph = font.glyphs[glyphName]
			if glyph is None:
				font.glyphs.append(newGlyphWithName(glyphName))
				glyph = font.glyphs[glyphName]
				if report:
					print("\t🔠 Created %s" % glyphName)
			glyphs[character] = glyph

		count = 0
		skipped = 0
		keyed = set()
		font.disableUpdateInterface()
		try:
			for master, plan in plans:
				for character, glyph in glyphs.items():
					self.setStatus("🔠 %s" % glyph.name)
					layer = glyph.layers[master.id]
					if not settings["overwrite"] and len(layer.shapes) > 0 and layer.layerId not in self.drawnLayers:
						skipped += 1  # has outlines that are not ours
						if report:
							print("\t☑️ %s (%s): has outlines, skipped" % (glyph.name, master.name))
						continue
					if glyph.name not in keyed:
						keyed.add(glyph.name)
						# the same keys in all masters; the width comes from the plus:
						glyph.leftMetricsKey = None
						glyph.rightMetricsKey = "=|"
						glyph.widthMetricsKey = None
					self.drawnLayers.add(layer.layerId)
					if settings["backup"]:
						self.backUp(glyph, layer)
					layer.shapes = None
					for contour in placedShapes(character, plan):
						layer.shapes.append(pathFromContour(contour))
					if character == "≠":
						layer.removeOverlap()  # the slash crosses both bars
						layer.roundCoordinates()
					layer.width = plan["width"]
					layer.updateMetrics()
					layer.syncMetrics()
					count += 1
				if report:
					print("\t✅ %s: width %i, stroke %i, bars %i, centered on %i" % (master.name, plan["width"], plan["stroke"], plan["length"], plan["centerY"]))
		finally:
			font.enableUpdateInterface()
		if font.currentTab:
			font.currentTab.redraw()
		return count, skipped, []

	def draw(self, report=False, forceFromScratch=False, onlyFonts=None):
		"""Draws the operators in the scope. Quiet for the live preview, with a report for the Draw button."""
		settings = self.settings(forceFromScratch)
		if settings is None:
			self.setStatus("⚠️ Please enter numbers in the fields.")
			return
		targets = self.targets(settings["scope"])
		if onlyFonts is not None:
			targets = [(font, masterIDs) for font, masterIDs in targets if font in onlyFonts]
		if not targets:
			self.setStatus("⚠️ No font open.")
			return

		if report:
			Glyphs.clearLog()
			print("Build Math Operators\n")
		self.setStatus("🛠️ Drawing…")
		total, skipped, firstProblem = 0, 0, None
		for font, masterIDs in targets:
			if report:
				fileName = font.filepath.lastPathComponent() if font.filepath else f"{font.familyName} (unsaved)"
				print(f"📄 {fileName}")
			count, skippedCount, problems = self.drawFont(font, masterIDs, settings, report)
			total += count
			skipped += skippedCount
			for problem in problems:
				firstProblem = firstProblem or f"{font.familyName}: {problem}"
				if report:
					print(f"\t⚠️ {problem}")
			if problems and report:
				print("\t⚠️ Nothing changed in this font, so that all its masters stay compatible.")
		if firstProblem:
			self.setStatus(f"⚠️ {firstProblem}")
		else:
			self.setStatus(f"✅ Drew {total} layers" + (f", skipped {skipped} with outlines." if skipped else "."))
			if report:
				Glyphs.showNotification("Build Math Operators", "Drew %i layers. Details in Macro Window." % total)


font = Glyphs.font
if font:
	BuildMathOperators()
else:
	Message(title="No Font Open", message="Build Math Operators needs a font. Please open one and run the script again.", OKButton=None)
