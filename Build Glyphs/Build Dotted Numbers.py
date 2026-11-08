# MenuTitle: Build Dotted Numbers
__doc__ = """
Build dotted numbers from your default figures and the period.
"""

import traceback
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSGlyph, GSComponent
from mekkablue.geometry import transform

distanceBetweenComponents = 100.0

numberGlyphs = [
	"one_period",
	"two_period",
	"three_period",
	"four_period",
	"five_period",
	"six_period",
	"seven_period",
	"eight_period",
	"nine_period",
	"one_zero_period",
	"one_one_period",
	"one_two_period",
	"one_three_period",
	"one_four_period",
	"one_five_period",
	"one_six_period",
	"one_seven_period",
	"one_eight_period",
	"one_nine_period",
	"two_zero_period",
]


def unsuffixed(name):
	if "." in name:
		return name[:name.find(".")]
	else:
		return name


def measureLayerAtHeightLeftFromLeftOrRight(thisLayer, height, leftSide=True):
	try:
		leftX = thisLayer.bounds.origin.x
		rightX = leftX + thisLayer.bounds.size.width
		y = height
		returnIndex = 1
		if not leftSide:
			returnIndex = -2
		measurement = thisLayer.intersectionsBetweenPoints(NSPoint(leftX, y), NSPoint(rightX, y))[returnIndex].pointValue().x
		if leftSide:
			distance = measurement - leftX
		else:
			distance = rightX - measurement
		return distance
	except:
		return None


def minDistanceBetweenTwoLayers(comp1, comp2, interval=5.0):
	topY = min(comp1.bounds.origin.y + comp1.bounds.size.height, comp2.bounds.origin.y + comp2.bounds.size.height)
	bottomY = max(comp1.bounds.origin.y, comp2.bounds.origin.y)
	distance = topY - bottomY
	minDist = None
	for i in range(int(distance / interval)):
		height = bottomY + i * interval
		left = measureLayerAtHeightLeftFromLeftOrRight(comp1, height, leftSide=False)
		right = measureLayerAtHeightLeftFromLeftOrRight(comp2, height, leftSide=True)
		try:  # avoid gaps like in i or j
			total = left + right
			if minDist is None or minDist > total:
				minDist = total
		except TypeError:  # left or right is None
			pass
	return minDist


def placeComponentsAtDistance(thisLayer, comp1, comp2, interval=5.0, distance=10.0):
	thisMaster = thisLayer.associatedFontMaster()
	masterID = thisMaster.id
	original1 = comp1.component.layers[masterID]
	original2 = comp2.component.layers[masterID]
	minDist = minDistanceBetweenTwoLayers(original1, original2, interval=interval)
	if minDist is None:
		return  # no measurable overlap in height, leave the component where it is
	comp2shift = distance - minDist
	addedSBs = original1.RSB + original2.LSB
	comp2.x = comp1.x + original1.width - addedSBs + comp2shift


def process(thisGlyph):
	parts = unsuffixed(thisGlyph.name).split("_")
	maxWidth = thisFont.upm
	thisGlyph.leftMetricsKey = None
	thisGlyph.rightMetricsKey = None
	for thisLayer in thisGlyph.layers:
		thisLayer.clear()
		for i, part in enumerate(parts):
			ucName = "%s.case" % part
			lfName = "%s.lf" % part
			if thisGlyph.glyphInfo.subCategory == "Uppercase" or thisGlyph.glyphInfo.category == "Number":
				if thisFont.glyphs[ucName]:
					part = ucName
				elif thisFont.glyphs[lfName]:
					part = lfName
			comp = GSComponent(part)
			thisLayer.shapes.append(comp)
			if i > 0:
				placeComponentsAtDistance(thisLayer, thisLayer.components[i - 1], comp, distance=distanceBetweenComponents)

		maxWidth = max(thisLayer.bounds.size.width * 1.1, maxWidth)
	return maxWidth


def postprocess(thisGlyph, scale, shiftUp):
	for thisLayer in thisGlyph.layers:
		scaleDown = transform(scale=scale).transformStruct()
		thisLayer.applyTransform(scaleDown)
		thisLayer.applyTransform(shiftUp)
		lsb = (thisFont.upm - thisLayer.bounds.size.width) // 2.0
		thisLayer.LSB = lsb
		thisLayer.width = thisFont.upm


thisFont = Glyphs.font  # frontmost font
if thisFont is None:
	Glyphs.showMacroWindow()
	print("⚠️ Build Dotted Numbers: No font open.")
else:
	thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
	try:
		maxWidth = 0.0
		for name in numberGlyphs:
			thisGlyph = thisFont.glyphs[name]
			if not thisGlyph:
				thisGlyph = GSGlyph()
				thisGlyph.name = name
				thisFont.glyphs.append(thisGlyph)

			print(f"Processing {thisGlyph.name}")
			maxWidth = max(maxWidth, process(thisGlyph))

		scale = (thisFont.upm / maxWidth) * 0.95
		yShift = transform(shiftY=thisFont.upm * 0.06).transformStruct()

		for name in numberGlyphs:
			thisGlyph = thisFont.glyphs[name]
			postprocess(thisGlyph, scale, yShift)

	except Exception:
		Glyphs.showMacroWindow()
		print("\n⚠️ Script Error:\n")
		print(traceback.format_exc())
		print()
		raise
	finally:
		thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
