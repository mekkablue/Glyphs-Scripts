# MenuTitle: Build Math Operators
__doc__ = """
Draws +−×÷=≠±≈¬ (optionally also <>≤≥ and ~^) from a few measurements, or from the thickness of your minus. With live preview.
"""

import math
import objc
import vanilla
from mekkablue import mekkaObject, newGlyphWithName, UpdateButton
from GlyphsApp import Glyphs, GSPath, GSNode, GSLINE, GSCURVE, GSOFFCURVE, GSMetricsTypeCapHeight, GSMetricsTypexHeight, Message
from AppKit import (
	NSAlert,
	NSAlertFirstButtonReturn,
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSLineBreakByTruncatingTail,
	NSSize,
	NSTextAlignmentRight,
	NSWindowStyleMaskResizable,
)
from Foundation import NSNumberFormatter, NSPoint

mathOperators = "+−×÷=≠±≈¬"
lessGreater = "<>≤≥"
asciiOperators = "~^"
figureNames = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
zeroCandidates = ("zero.tf", "zero.tosf", "zero")  # for ‘same as zero’, in order of preference
fallbackStroke = 80  # if the master has no horizontal stem
fallbackPlusWidth = 550  # for ‘same as zero’, if the font has no zero
minusTabScale = 0.735  # zoom of the tab for editing the minus

# Proportions of the shapes, relative to the stroke or to the length of the bars:
multiplyScale = 0.9  # bounding box of × relative to the length of the bars
chevronAngle = 30.0  # angle of the arms of < and > against the horizontal axis, in degrees
caretAngle = 45.0  # angle of the arms of ^ against the vertical axis, in degrees
slashAngle = 63.0  # angle of the slash in ≠ against the horizontal, in degrees
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


def crossShapes(horizontalLength, verticalLength, horizontalStroke, verticalStroke, centerY=0):
	"""A plus as two overlapping bars. The overlap stays, it is not merged into one contour."""
	return [
		rectangle(span(0, horizontalLength), span(centerY, horizontalStroke)),
		rectangle(span(0, verticalStroke), span(centerY, verticalLength)),
	]


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


def chevronPoints(run, angle, upperStroke, lowerStroke, cutThickness, innerShift=0):
	"""
	A mitered ‘>’ (tip pointing right) as a list of points. The centerlines of its arms meet at (0, 0), each arm runs
	`run` units to the left. The arms may differ in stroke. If cutThickness is more than 0, the pointy outer tip is cut
	off by a vertical line, at the place where the blunt end is that tall. The inner apex point is drawn `innerShift`
	units toward the outer apex, which lightens the joint of the arms.
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

	apexX = outerTip[0]  # where the outer apex ends, at the tip or at the cut
	if cutThickness > 0:
		# the vertical distance between the outer edges grows linearly with the distance from the outer tip:
		cutX = (outerUpper[1] - outerLower[1] + tangent * (outerUpper[0] + outerLower[0]) - cutThickness) / (2.0 * tangent)
		# never cut beyond the inner tip, that would tear the stroke apart:
		apexX = min(max(cutX, innerTip[0] + 0.05 * (outerTip[0] - innerTip[0])), outerTip[0])
	# the inner apex moves toward the outer one, but never gets close enough to tear off the joint:
	innerX = min(innerTip[0] + innerShift, apexX - 0.25 * min(upperStroke, lowerStroke))
	innerPoint = (max(innerX, innerTip[0]), innerTip[1])

	rise = run * tangent
	endUpper, endLower = (-run, rise), (-run, -rise)
	endPoints = (
		(endUpper[0] + outerUpper[0], endUpper[1] + outerUpper[1]),
		(endUpper[0] + innerUpper[0], endUpper[1] + innerUpper[1]),
		innerPoint,
		(endLower[0] + innerLower[0], endLower[1] + innerLower[1]),
		(endLower[0] + outerLower[0], endLower[1] + outerLower[1]),
	)

	if cutThickness > 0:
		upperY = outerUpper[1] + tangent * (outerUpper[0] - apexX)
		lowerY = outerLower[1] - tangent * (outerLower[0] - apexX)
		return [(apexX, upperY)] + list(endPoints) + [(apexX, lowerY)]
	return [outerTip] + list(endPoints)


def chevronOutline(angle, upperStroke, lowerStroke, cutThickness, width=None, height=None, innerShift=0):
	"""A ‘>’ of that bounding box width, or else height, centered on (0, 0). The run of the arms is found by measuring."""
	# the arm ends must be the leftmost points, otherwise the width does not grow with the run. That takes a long run at flat angles:
	probeRun = 100.0 + 2.0 * max(upperStroke, lowerStroke) / math.sin(math.radians(angle))

	def measured(run):
		points = chevronPoints(run, angle, upperStroke, lowerStroke, cutThickness, innerShift)
		xs, ys = [x for x, y in points], [y for x, y in points]
		return points, min(xs), max(xs), min(ys), max(ys)

	points, minX, maxX, minY, maxY = measured(probeRun)
	if width is not None:
		run = probeRun + width - (maxX - minX)  # width grows by one unit per unit of run
		points, minX, maxX, minY, maxY = measured(max(run, 1.0))
		if abs((maxX - minX) - width) > 0.01:
			# with thick strokes at flat angles the inner apex is the leftmost point, and the width no longer
			# grows with the run. The width never shrinks with the run, so search for it:
			low, high = 1.0, 2.0 * width + probeRun
			for _ in range(50):
				middle = (low + high) / 2.0
				points, minX, maxX, minY, maxY = measured(middle)
				if maxX - minX < width:
					low = middle
				else:
					high = middle
			points, minX, maxX, minY, maxY = measured(high)
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

	def __init__(self, plan):
		self.length = int(round(plan["length"]))
		self.stroke = int(round(plan["stroke"]))
		self.tangent = math.tan(math.radians(plan["italicAngle"]))
		self.adaptPlusMinus = plan["adaptPlusMinus"]
		self.dotDistance = int(round(plan["dotDistance"]))  # between dots and bar in ÷
		self.shapeDistance = int(round(plan["shapeDistance"]))  # between the shapes in ± ≤ ≥
		self.barDistance = int(round(plan["barDistance"]))  # between the two horizontals in = ≠ ≈
		self.overshoot = plan["overshoot"]  # of the dots in ÷
		self.kneeCap = plan["kneeCap"]  # of the inner apex in < > ≤ ≥
		self.slashOverhang = plan["slashOverhang"]  # of the slash in ≠
		self.slashStrokeChange = plan["slashStrokeChange"]  # stroke width of the slash in ≠, relative to the stroke
		self.multiplyExtension = plan["multiplyExtension"]  # of the arms of ×
		self.miter = plan["miter"] / 100.0
		self.correction = plan["correction"] / 100.0
		# a slanted vertical stem needs to be wider to look as strong as the horizontal stroke:
		self.verticalStroke = int(round(self.corrected((0, 1))))

	def slant(self, contour):
		if not self.tangent:
			return contour
		return mapPoints(contour, lambda x, y: (x + y * self.tangent, y))

	def corrected(self, direction, stroke=None):
		"""
		The thickness to draw a stroke with that direction (before slanting), so that it is as strong as the
		stroke after slanting. Slanting stretches the direction vector by `factor`, and thus thins the stroke by
		the same factor (windshield-wiper effect). Correction 0 is the pure geometric slant, 1 is full correction.
		A stroke that is not the main stroke can be given.
		"""
		directionX, directionY = direction
		length = math.hypot(directionX, directionY)
		factor = math.hypot(directionX / length + directionY / length * self.tangent, directionY / length)
		return (self.stroke if stroke is None else stroke) * (1 + self.correction * (factor - 1))


def minusShapes(p):
	return [p.slant(rectangle(span(0, p.length), span(0, p.stroke)))]


def plusShapes(p):
	return [p.slant(bar) for bar in crossShapes(p.length, p.length, p.stroke, p.verticalStroke)]


def multiplyShapes(p):
	armLength = math.sqrt(2.0) * p.length * multiplyScale - p.stroke + 2 * p.multiplyExtension
	# after rotating, the horizontal bar runs up to the right, the vertical bar up to the left:
	arms = crossShapes(armLength, armLength, p.corrected((1, 1)), p.corrected((-1, 1)))
	return [p.slant(rotate(arm, 45)) for arm in arms]


def divideShapes(p):
	shapes = minusShapes(p)
	diameter = int(round(p.stroke + 2 * p.overshoot))
	# the overshoot of the dots eats into the distance, so the distance is the one of a dot as wide as the stroke:
	offset = p.stroke / 2.0 + max(p.dotDistance - p.overshoot, 1) + diameter / 2.0
	for sign in (1, -1):
		# the dots follow the slant, but stay round:
		shapes.append(ellipseOutline(span(sign * offset * p.tangent, diameter), span(sign * offset, diameter)))
	return shapes


def equalShapes(p):
	height = 2 * p.stroke + p.barDistance
	top = int(round(height / 2.0))
	xSpan = span(0, p.length)
	return [
		p.slant(rectangle(xSpan, (top - p.stroke, top))),
		p.slant(rectangle(xSpan, (top - height, top - height + p.stroke))),
	]


def notEqualShapes(p):
	shapes = equalShapes(p)
	halfHeight = p.stroke + p.barDistance / 2.0 + p.slashOverhang  # the slash reaches beyond the bars by its overhang
	slashStroke = p.corrected((math.cos(math.radians(slashAngle)), math.sin(math.radians(slashAngle))), max(p.stroke + p.slashStrokeChange, 1))
	halfWidth = slashStroke / math.sin(math.radians(slashAngle)) / 2.0  # horizontal half width for the stroke thickness
	run = halfHeight / math.tan(math.radians(slashAngle))
	shapes.append(p.slant(polygon((
		(-run - halfWidth, -halfHeight), (-run + halfWidth, -halfHeight),
		(run + halfWidth, halfHeight), (run - halfWidth, halfHeight),
	))))
	return shapes


def plusMinusShapes(p):
	if p.adaptPlusMinus:
		stemLength = max(p.length - p.shapeDistance - p.stroke, 2 * p.stroke)  # as tall as the plus
	else:
		stemLength = p.length
	height = stemLength + p.shapeDistance + p.stroke
	top = int(round(height / 2.0))
	bottom = top - height
	plus = crossShapes(p.length, stemLength, p.stroke, p.verticalStroke, centerY=top - stemLength / 2.0)
	minus = rectangle(span(0, p.length), (bottom, bottom + p.stroke))
	return [p.slant(bar) for bar in plus] + [p.slant(minus)]


def logicalNotShapes(p):
	left, right = span(0, p.length)
	barLow, barHigh = span(0, p.stroke)
	legLow = barLow - int(round(logicalNotLeg * p.length))
	bar = rectangle((left, right), (barLow, barHigh))
	leg = rectangle((right - p.verticalStroke, right), (legLow, barHigh))  # reaches up into the bar
	return [p.slant(bar), p.slant(leg)]


def approxEqualShapes(p):
	wave, thickness = waveOutline(p.length, p.stroke)
	offset = (thickness + p.barDistance) / 2.0
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
	< or >, as wide as the bars are long, with the outer apex cut off by the Miter value. The overshoot draws the inner
	apex point toward the cut, so the joint of the arms does not get too heavy.
	"""
	upperStroke, lowerStroke = chevronStrokes(p, angle, mirrored)
	outline = chevronOutline(angle, upperStroke, lowerStroke, p.miter * p.stroke, width=p.length, innerShift=p.kneeCap)
	return mirrorHorizontally(outline) if mirrored else outline


def chevronFits(p, mirrored, angle):
	"""Whether a chevron at that angle can be as narrow as the bars are long. A flat chevron with a pointed apex cannot."""
	upperStroke, lowerStroke = chevronStrokes(p, angle, mirrored)
	points = chevronPoints(1.0, angle, upperStroke, lowerStroke, p.miter * p.stroke, p.kneeCap)
	xs = [x for x, y in points]
	return max(xs) - min(xs) <= p.length


def greaterShapes(p):
	return [p.slant(chevronShape(p, False))]


def lessShapes(p):
	return [p.slant(chevronShape(p, True))]


def chevronWithBar(p, mirrored):
	"""< or > with a bar underneath. Same total height as the plain chevron, so the chevron gets flatter."""
	barBlock = p.shapeDistance + p.stroke

	def heightOf(contour):
		minX, minY, maxX, maxY = bounds([contour])
		return maxY - minY

	targetHeight = heightOf(chevronShape(p, mirrored)) - barBlock
	low, high = 10.0, chevronAngle  # flatter chevrons are not worth having, the glyph gets taller instead
	while low < high and not chevronFits(p, mirrored, low):
		low += 1.0
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
	bar = rectangle(span(0, p.length), (bottom, bottom + p.stroke))
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
		p = Proportions(dict(plan, length=plan["length"] + lengthChange))
		contours = [counterclockwise(contour) for contour in shapeBuilders[character](p)]
		if character == "^":
			shiftY = plan["capHeight"] - bounds(contours)[3]  # the tip touches the cap height
		else:
			shiftY = plan["centerY"]
			if character == "±":
				shiftY = max(shiftY, -bounds(contours)[1])  # never sink under the baseline
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


def decimalFormatter(minimum=None, maximum=None):
	"""Number formatter that accepts decimals, optionally within a range."""
	formatter = NSNumberFormatter.alloc().init()
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
		"dotDistance": 100,
		"shapeDistance": 100,
		"barDistance": 100,
		"dotOvershoot": 10,
		"kneeCap": 10,
		"slashOverhang": 80,
		"slashStroke": 0,
		"multiplyExtension": 0,
		"miter": 80,
		"italic": True,
		"wiper": 100,
		"angleAdjustment": -1,
		"adaptPlusMinus": True,
		"includeLessGreater": False,
		"includeAscii": False,
		"overwrite": True,
		"backup": True,
		"scope": 0,
	}

	def __init__(self):
		windowWidth = 500
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
			"Draws the math operators with the widths, sidebearings and heights below. Changes show live in the font.",
			sizeStyle="small",
			selectable=True,
		)

		self.w.drawMode = vanilla.VerticalRadioGroup("auto", ("Draw from scratch", "Take from minus"), callback=self.SavePreferences, sizeStyle="small")
		self.w.drawMode.setToolTip("From scratch: the stroke comes from the field below. From minus: the stroke is the thickness of your minus. The minus itself is redrawn like all other operators, so only its thickness counts.")

		tooltipText = "The operators that are drawn. Tick the boxes behind them to draw the less and greater symbols, and asciitilde and asciicircum as well."
		self.w.drawLabel = vanilla.TextBox("auto", "Draw", sizeStyle="small")
		self.w.drawLabel.setToolTip(tooltipText)
		self.w.operatorsText = vanilla.TextBox("auto", mathOperators, sizeStyle="small")
		self.w.operatorsText.setToolTip(tooltipText)

		tooltipText = "Width of the plus. All other operators get the same width, and RSB =|."
		self.w.widthLabel = vanilla.TextBox("auto", "Width", sizeStyle="small")
		self.w.widthLabel.setToolTip(tooltipText)
		self.w.widthMode = vanilla.PopUpButton("auto", ("Number", "Same as zero", "Same as glyph…"), callback=self.SavePreferences, sizeStyle="small")
		self.w.widthMode.setToolTip("Number: width in units. Same as zero: width of zero.tf, or else zero.tosf, or else zero, in each master (%i if the font has no zero). Same as glyph: width of the glyph in the field." % fallbackPlusWidth)
		self.w.plusWidth = SteppingEditText("auto", "600", formatter=integerFormatter(1), callback=self.SavePreferences, sizeStyle="small")
		self.w.plusWidth.setToolTip("Width of the plus in units. Use the arrow keys to step.")
		self.w.plusWidthGlyph = vanilla.EditText("auto", "zero.tf", callback=self.SavePreferences, sizeStyle="small")
		self.w.plusWidthGlyph.setToolTip("Name of the glyph whose width the plus takes.")

		tooltipText = "The operators are vertically centered on this height. The caret ^ is the exception: its tip touches the cap height."
		self.w.centerLabel = vanilla.TextBox("auto", "Center on", sizeStyle="small")
		self.w.centerLabel.setToolTip(tooltipText)
		self.w.centerMode = vanilla.PopUpButton("auto", ("Half cap height", "Half x-height", "Center of figures", "Center of glyphs"), callback=self.SavePreferences, sizeStyle="small")
		self.w.centerMode.setToolTip(tooltipText)
		self.w.figureStyle = vanilla.PopUpButton("auto", ["zero" + suffix for suffix in self.figureSuffixes], callback=self.SavePreferences, sizeStyle="small")
		self.w.figureStyle.setToolTip("Which figures to average: the vertical centers of their bounding boxes.")
		self.w.centerGlyphs = vanilla.EditText("auto", "n, zero, eight", callback=self.SavePreferences, sizeStyle="small")
		self.w.centerGlyphs.setToolTip("Comma-separated glyph names. The average of the vertical centers of their bounding boxes is the center height.")

		tooltipText = "Distance between the shape and the edge of the glyph, on each side, in units."
		self.w.sidebearingLabel = vanilla.TextBox("auto", "Sidebearings", sizeStyle="small")
		self.w.sidebearingLabel.setToolTip(tooltipText)
		self.w.sidebearing = SteppingEditText("auto", "70", formatter=integerFormatter(0), callback=self.SavePreferences, sizeStyle="small")
		self.w.sidebearing.setToolTip(tooltipText)
		self.w.sidebearingText = vanilla.TextBox("auto", "units, left and right", sizeStyle="small")

		tooltipText = "Stroke thickness in units. Preset with the first horizontal stem of the current master. Not used if you take the thickness from the minus."
		self.w.strokeLabel = vanilla.TextBox("auto", "Stroke", sizeStyle="small")
		self.w.strokeLabel.setToolTip(tooltipText)
		self.w.stroke = SteppingEditText("auto", "80", formatter=integerFormatter(1), callback=self.SavePreferences, sizeStyle="small")
		self.w.stroke.setToolTip(tooltipText)
		self.w.resetStroke = UpdateButton("auto", callback=self.resetStroke)
		self.w.resetStroke.setToolTip("Resets the stroke to the first horizontal stem of the current master.")
		self.w.strokeText = vanilla.TextBox("auto", "units, first horizontal stem", sizeStyle="small")

		# distances and corrections: one row each, the fields are labeled with the glyphs they are for
		def addField(name, glyphs, value, tooltipText, minimum, maximum=999):
			"""A stepping field wide enough for three figures, with a mini label behind it that names the glyphs it is for."""
			if glyphs:
				label = vanilla.TextBox("auto", glyphs, sizeStyle="small")
				label.setToolTip(tooltipText)
				setattr(self.w, name + "Label", label)
			field = SteppingEditText("auto", str(value), formatter=integerFormatter(minimum, maximum), callback=self.SavePreferences, sizeStyle="small")
			field.setToolTip(tooltipText)
			setattr(self.w, name, field)

		tooltipText = "Distances between shapes, in units, from edge to edge: for the dots in ÷, for the two horizontals in = ≠ ≈, and for the shapes in ± ≤ ≥."
		self.w.distancesLabel = vanilla.TextBox("auto", "Distances", sizeStyle="small")
		self.w.distancesLabel.setToolTip(tooltipText)
		addField("dotDistance", "÷", 100, "Space between the dots and the bar in ÷, from edge to edge, in units. The overshoot of the dots is subtracted: the distance is the one of a dot that is as wide as the stroke.", 1)
		addField("barDistance", "=", 100, "Space between the two horizontals in = ≠ ≈, from edge to edge, in units.", 1)
		addField("shapeDistance", "±≤≥", 100, "Space between the plus and the minus in ±, and between the chevron and the bar in ≤ ≥, from edge to edge, in units.", 1)

		tooltipText = "Optical corrections, in units: the overshoot of the dots in ÷, the extra extension of ×, the knee caps of < > ≤ ≥, and the overhang and the stroke width of the slash in ≠."
		self.w.correctionsLabel = vanilla.TextBox("auto", "Corrections", sizeStyle="small")
		self.w.correctionsLabel.setToolTip(tooltipText)
		addField("dotOvershoot", "÷", 10, "Overshoot of the dots in ÷: each dot is as wide as the stroke plus twice this value, so the circles do not look smaller than the bar.", 0)
		addField("multiplyExtension", "×", 0, "Extra extension of ×: each end of each arm is extended by this many units (negative: shortened), since diagonals look shorter than horizontals.", -99, 99)
		addField("kneeCap", "<>≤≥", 10, "Knee cap of < > ≤ ≥: the inner apex point is drawn this many units toward the cut-off outer apex, to lighten the joint of the arms. The shape itself does not overshoot the bars.", 0)
		addField("slashOverhang", None, 80, "Overhang of the slash in ≠: how far it reaches beyond the outer edges of the two bars, in units.", 0)
		addField("slashStroke", None, 0, "Stroke width change of the slash in ≠, in units, added to the stroke (negative: thinner).", -99, 99)
		self.w.slashLabel = vanilla.TextBox("auto", "≠", sizeStyle="small")
		self.w.slashLabel.setToolTip("The slash in ≠. First field: how far it reaches beyond the bars. Second field: change of its stroke width. Both in units.")

		tooltipText = "Cuts off the pointed apex of < > ≤ ≥ with a vertical line (parallel to the italic angle in slanted masters), so that the blunt end is this percentage of the stroke tall. 0 keeps the sharp point."
		self.w.miterLabel = vanilla.TextBox("auto", "Miter", sizeStyle="small")
		self.w.miterLabel.setToolTip(tooltipText)
		self.w.miter = SteppingEditText("auto", "80", formatter=integerFormatter(0, 200), callback=self.SavePreferences, sizeStyle="small")
		self.w.miter.setToolTip(tooltipText)
		self.w.miterText = vanilla.TextBox("auto", "% of the stroke, in <>≤≥", sizeStyle="small")

		tooltipText = "Slanting thins strokes that are neither horizontal nor vertical, like the arms of × (windshield-wiper effect). This corrects the thickness of vertical and diagonal strokes in + × ≠ ± ¬ < > ≤ ≥ and ^. 100 is full correction, 0 is the pure geometric slant."
		self.w.wiper = SteppingEditText("auto", "100", formatter=integerFormatter(0, 100), callback=self.SavePreferences, sizeStyle="small")
		self.w.wiper.setToolTip(tooltipText)
		self.w.wiperText = vanilla.TextBox("auto", "% windshield wiper correction", sizeStyle="small")
		self.w.wiperText.setToolTip(tooltipText)

		tooltipText = "Added to the italic angle of each slanted master, in degrees: a negative value slants the operators less than the font. Upright masters stay upright."
		self.w.angleAdjustment = SteppingEditText("auto", "-1", formatter=decimalFormatter(-45, 45), callback=self.SavePreferences, sizeStyle="small")
		self.w.angleAdjustment.setToolTip(tooltipText)
		self.w.angleText = vanilla.TextBox("auto", "° angle adjustment", sizeStyle="small")
		self.w.angleText.setToolTip(tooltipText)
		self.w.italicLabel = vanilla.TextBox("auto", "Italic angle", sizeStyle="small")
		self.w.italicLabel.setToolTip("Slants the operators like the font, with corrections for the loss of stroke weight.")

		self.w.italic = vanilla.CheckBox("auto", "Respect italic angle", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.italic.setToolTip("Slants the shapes by the italic angle of each master (plus the angle adjustment), and corrects the stroke weight for the slant. Off: all operators are upright, and the two fields behind are disabled.")
		self.w.adaptPlusMinus = vanilla.CheckBox("auto", "Adapt ± height", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.adaptPlusMinus.setToolTip("Adapt height in ±: shortens the vertical stroke of the plus in ±, so that ± is as tall as the plus. Off: ± is a full plus with a minus underneath, and taller than the plus.")
		self.w.includeLessGreater = vanilla.CheckBox("auto", lessGreater, value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeLessGreater.setToolTip("Also draws less, greater, lessequal and greaterequal.")
		self.w.includeAscii = vanilla.CheckBox("auto", asciiOperators, value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeAscii.setToolTip("Also draws asciitilde and asciicircum.")

		self.w.overwrite = vanilla.CheckBox("auto", "Overwrite existing", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwrite.setToolTip("Replaces the outlines of operators that already have some. Off: layers with outlines are left alone, and only empty layers are drawn. Layers drawn by this script in this session can always be redrawn by the live preview.")
		self.w.backup = vanilla.CheckBox("auto", "Backup in background", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.backup.setToolTip("Before a layer is overwritten for the first time in this session, copies its outlines into the background. Does nothing if the background already holds something.")
		self.w.clearBackgroundsButton = vanilla.Button("auto", "Clear backgrounds", callback=self.clearBackgrounds, sizeStyle="small")
		self.w.clearBackgroundsButton.setToolTip("Empties the background of the operators in the scope (the glyphs of the Draw row), in the masters of the scope. Asks for confirmation first.")

		tooltipText = "Which fonts and masters are drawn. Stroke, sidebearings and overshoot are the same in all masters of the scope."
		self.w.scopeLabel = vanilla.TextBox("auto", "Scope", sizeStyle="small")
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
		for hint in (self.w.sidebearingText, self.w.strokeText, self.w.miterText):
			hint.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		# the status line shortens instead of widening the window:
		self.w.status.getNSTextField().setLineBreakMode_(NSLineBreakByTruncatingTail)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		# the description wraps: it takes the width it is given instead of demanding one long line
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# the labels end at one x-position:
		labelNames = ("drawLabel", "widthLabel", "centerLabel", "sidebearingLabel", "strokeLabel", "distancesLabel", "correctionsLabel", "miterLabel", "italicLabel", "scopeLabel")
		widestLabel = "sidebearingLabel"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		for labelName in ("dotDistanceLabel", "barDistanceLabel", "shapeDistanceLabel", "dotOvershootLabel", "multiplyExtensionLabel", "kneeCapLabel", "slashLabel"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
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
			"H:|-inset-[distancesLabel]-gap-[dotDistance(fieldWidth)]-tight-[dotDistanceLabel]-pair-[barDistance(fieldWidth)]-tight-[barDistanceLabel]-pair-[shapeDistance(fieldWidth)]-tight-[shapeDistanceLabel]-pair-[adaptPlusMinus]-(>=inset)-|",
			"H:|-inset-[correctionsLabel]-gap-[dotOvershoot(fieldWidth)]-tight-[dotOvershootLabel]-pair-[multiplyExtension(fieldWidth)]-tight-[multiplyExtensionLabel]-pair-[kneeCap(fieldWidth)]-tight-[kneeCapLabel]-pair-[slashOverhang(fieldWidth)]-tight-[slashStroke(fieldWidth)]-tight-[slashLabel]-(>=inset)-|",
			"H:|-inset-[miterLabel]-gap-[miter(60)]-gap-[miterText]-(>=inset)-|",
			"H:|-inset-[italicLabel]-gap-[italic]-(>=inset)-|",
			"H:[wiper(60)]-gap-[wiperText]-(>=inset)-|",
			"H:[angleAdjustment(60)]-gap-[angleText]-(>=inset)-|",
			"H:|-inset-[drawLabel]-gap-[operatorsText]-gap-[includeLessGreater]-gap-[includeAscii]-(>=inset)-|",
			"H:|-inset-[scopeLabel]-gap-[scope]-inset-|",
			"H:|-inset-[status]-inset-|",
			"H:|-inset-[tabButton]-(>=inset)-[drawButton(>=70)]-inset-|",
			(
				"V:|-inset-[descriptionText(42)]-row-[drawMode(radioHeight)]-section-[includeLessGreater]-row-[widthMode]-row-[centerMode]-section-[sidebearing]-row-[stroke]-row-[dotDistance]-row-[dotOvershoot]-row-[miter]"
				"-section-[italic]-row-[wiper]-row-[angleAdjustment]-section-[scope]-section-[overwrite]-checkRow-[backup]-section-[status]-inset-[drawButton]-inset-|"
			),
			"V:[tabButton]-inset-|",
			aligned("widthMode", "centerMode", "width"),
			# the two italic fields are indented like the checkbox
			aligned("wiper", "italic", "leading"),
			aligned("angleAdjustment", "italic", "leading"),
			# the first three fields of both lines stand above each other. The mini labels keep their natural width, so every gap
			# between an element and the next is the same. Only the labels of the columns above each other share a width:
			aligned("dotOvershootLabel", "dotDistanceLabel", "width"),
			aligned("multiplyExtensionLabel", "barDistanceLabel", "width"),
			# the button sits next to the last radio button, the one for the minus:
			aligned("editMinusButton", "drawMode", "bottom"),
			"H:[backup]-gap-[clearBackgroundsButton]-(>=inset)-|",
			aligned("clearBackgroundsButton", "backup", "centerY"),
			# everything in the Draw row sits on the vertical center of its first checkbox
			aligned("drawLabel", "includeLessGreater", "centerY"),
			aligned("operatorsText", "includeLessGreater", "centerY"),
			aligned("includeAscii", "includeLessGreater", "centerY"),
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
			("dotDistance", ("distancesLabel", "dotDistanceLabel", "barDistance", "barDistanceLabel", "shapeDistance", "shapeDistanceLabel", "adaptPlusMinus")),
			("dotOvershoot", ("correctionsLabel", "dotOvershootLabel", "multiplyExtension", "multiplyExtensionLabel", "kneeCap", "kneeCapLabel", "slashOverhang", "slashStroke", "slashLabel")),
			("miter", ("miterLabel", "miterText")),
			("italic", ("italicLabel", )),
			("wiper", ("wiperText", )),
			("angleAdjustment", ("angleText", )),
			("scope", ("scopeLabel", )),
		)
		for fieldName, otherNames in rowFields:
			for otherName in otherNames:
				rules.append(aligned(otherName, fieldName, "centerY"))
		self.w.addAutoPosSizeRules(rules, metrics={"inset": 15, "gap": 8, "row": 8, "section": 12, "checkRow": 5, "tight": 5, "pair": 7, "fieldWidth": 35, "radioHeight": self.w.drawMode.getFittingHeight()})

		# the stroke is a property of the font, not of this script, so it is preset and not remembered:
		self.w.stroke.set(str(self.presetStroke(font)))

		self.LoadPreferences()
		storedSuffix = self.pref("figureStyle")
		if storedSuffix in self.figureSuffixes:
			self.w.figureStyle.set(self.figureSuffixes.index(storedSuffix))
		self.updateUI()

		self.draw()  # show the current values right away; the previous outlines go to the background if that option is on
		self.w.open()
		self.w.makeKey()

		# make the window horizontally resizable, but keep the height that Auto Layout determined.
		# (Content sizes set directly on the NSWindow, so the title bar is not counted twice.)
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()
		contentSize = nsWindow.contentView().frame().size
		nsWindow.setContentMinSize_(NSSize(contentSize.width, contentSize.height))
		nsWindow.setContentMaxSize_(NSSize(contentSize.width + 1000, contentSize.height))

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
		for field in (self.w.wiper, self.w.angleAdjustment):
			field.enable(self.w.italic.get())

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

	def clearBackgrounds(self, sender):
		"""Empties the background of the operators in the scope, after asking."""
		settings = self.settings()
		if settings is None:
			self.setStatus("⚠️ Please enter numbers in the fields.")
			return
		layers = []
		for font, masterIDs in self.targets(settings["scope"]):
			for character in settings["characters"]:
				glyph = font.glyphs[Glyphs.niceGlyphName(character)]
				if glyph is None:
					continue
				for master in font.masters:
					if masterIDs is None or master.id in masterIDs:
						layer = glyph.layers[master.id]
						if len(layer.background.shapes) > 0:
							layers.append((glyph, layer))
		if not layers:
			self.setStatus("ℹ️ No backgrounds to clear.")
			return
		alert = NSAlert.alloc().init()
		alert.setMessageText_("Clear backgrounds?")
		alert.setInformativeText_("This empties the background of %i layers of the operators in the scope, including backups made by this script. This cannot be undone easily.\n\nContinue?" % len(layers))
		alert.addButtonWithTitle_("Clear")
		alert.addButtonWithTitle_("Cancel")
		if alert.runModal() != NSAlertFirstButtonReturn:
			return
		for glyph, layer in layers:
			layer.background.clear()
			self.backedUp.discard((glyph.name, layer.layerId))  # a later draw may back up again
		self.setStatus("✅ Cleared %i backgrounds." % len(layers))

	def lacksMinus(self, font, masterIDs):
		minusGlyph = font.glyphs["minus"]
		for master in font.masters:
			if masterIDs is None or master.id in masterIDs:
				if minusGlyph is None or len(minusGlyph.layers[master.id].shapes) == 0:
					return True
		return False

	def showMinus(self, font):
		"""Selects the tab with the minus in the font (or opens it), with the minus open for editing, the select tool active, zoomed and centered."""
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
		font.tool = "SelectTool"  # ready for moving points
		tab.scale = minusTabScale
		tab.initialZoom()

	# ------------------------------------------------------------------ Settings and plans

	def settings(self, forceFromScratch=False):
		"""Returns the settings as a dictionary, or None while the fields hold no valid numbers."""
		try:
			settings = {
				"stroke": int(round(float(self.w.stroke.get()))),
				"sidebearing": int(round(float(self.pref("sidebearing")))),
				"dotDistance": int(round(float(self.pref("dotDistance")))),
				"shapeDistance": int(round(float(self.pref("shapeDistance")))),
				"barDistance": int(round(float(self.pref("barDistance")))),
				"overshoot": int(round(float(self.pref("dotOvershoot")))),
				"kneeCap": int(round(float(self.pref("kneeCap")))),
				"slashOverhang": int(round(float(self.pref("slashOverhang")))),
				"slashStrokeChange": int(round(float(self.pref("slashStroke")))),
				"multiplyExtension": int(round(float(self.pref("multiplyExtension")))),
				"miter": float(self.pref("miter")),
				"wiper": float(self.pref("wiper")),
				"angleAdjustment": float(self.pref("angleAdjustment")),
				"plusWidth": int(round(float(self.pref("plusWidth")))),
			}
		except (TypeError, ValueError):
			return None
		distances = (settings["dotDistance"], settings["shapeDistance"], settings["barDistance"])
		corrections = (settings["overshoot"], settings["kneeCap"], settings["slashOverhang"])
		if settings["stroke"] < 1 or settings["plusWidth"] < 1 or settings["sidebearing"] < 0 or min(distances) < 1 or min(corrections) < 0 or settings["miter"] < 0 or not 0 <= settings["wiper"] <= 100 or not -45 <= settings["angleAdjustment"] <= 45:
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
		if widthMode == 1:
			return fallbackPlusWidth, None  # no zero at all
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
		italicAngle = 0.0
		if settings["italic"] and master.italicAngle:  # upright masters stay upright
			italicAngle = master.italicAngle + settings["angleAdjustment"]
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
			"dotDistance": settings["dotDistance"],
			"shapeDistance": settings["shapeDistance"],
			"barDistance": settings["barDistance"],
			"overshoot": settings["overshoot"],
			"kneeCap": settings["kneeCap"],
			"slashOverhang": settings["slashOverhang"],
			"slashStrokeChange": settings["slashStrokeChange"],
			"multiplyExtension": settings["multiplyExtension"],
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
