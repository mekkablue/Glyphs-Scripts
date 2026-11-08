# MenuTitle: Build Parenthesized Glyphs
__doc__ = """
Creates parenthesized letters and numbers: one.paren, two.paren, three.paren, four.paren, five.paren, six.paren, seven.paren, eight.paren, nine.paren, one_zero.paren, one_one.paren, one_two.paren, one_three.paren, one_four.paren, one_five.paren, one_six.paren, one_seven.paren, one_eight.paren, one_nine.paren, two_zero.paren, a.paren, b.paren, c.paren, d.paren, e.paren, f.paren, g.paren, h.paren, i.paren, j.paren, k.paren, l.paren, m.paren, n.paren, o.paren, p.paren, q.paren, r.paren, s.paren, t.paren, u.paren, v.paren, w.paren, x.paren, y.paren, z.paren.
"""

import traceback
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSComponent, Message
from mekkablue import newGlyphWithName
from mekkablue.geometry import transform

distanceBetweenComponents = 95.0
parenShiftForLetters = 40.0

parenGlyphs = [
	"one.paren", "two.paren", "three.paren", "four.paren", "five.paren", "six.paren", "seven.paren", "eight.paren", "nine.paren", "one_zero.paren", "one_one.paren",
	"one_two.paren", "one_three.paren", "one_four.paren", "one_five.paren", "one_six.paren", "one_seven.paren", "one_eight.paren", "one_nine.paren", "two_zero.paren", "a.paren",
	"b.paren", "c.paren", "d.paren", "e.paren", "f.paren", "g.paren", "h.paren", "i.paren", "j.paren", "k.paren", "l.paren", "m.paren", "n.paren", "o.paren", "p.paren", "q.paren",
	"r.paren", "s.paren", "t.paren", "u.paren", "v.paren", "w.paren", "x.paren", "y.paren", "z.paren"
]


def measureLayerAtHeightFromLeftOrRight(thisLayer, height, leftSide=True):
	thisLayer = thisLayer.copyDecomposedLayer()
	if thisLayer.bounds is None:  # empty layer
		return None
	leftX = thisLayer.bounds.origin.x
	rightX = leftX + thisLayer.bounds.size.width
	returnIndex = 1 if leftSide else -2
	measurements = thisLayer.intersectionsBetweenPoints(NSPoint(leftX, height), NSPoint(rightX, height))
	if len(measurements) > 2:
		measurement = measurements[returnIndex].pointValue().x
		if leftSide:
			return measurement - leftX
		return rightX - measurement
	return None


def minDistanceBetweenTwoLayers(comp1, comp2, interval=5.0):
	topY = min(comp1.bounds.origin.y + comp1.bounds.size.height, comp2.bounds.origin.y + comp2.bounds.size.height)
	bottomY = max(comp1.bounds.origin.y, comp2.bounds.origin.y)
	distance = topY - bottomY
	minDist = None
	for i in range(int(distance / interval)):
		height = bottomY + i * interval
		left = measureLayerAtHeightFromLeftOrRight(comp1, height, leftSide=False)
		right = measureLayerAtHeightFromLeftOrRight(comp2, height, leftSide=True)
		if left is None or right is None:  # avoid gaps like in i or j
			continue
		total = left + right
		if minDist is None or minDist > total:
			minDist = total
	return minDist


def placeComponentsAtDistance(thisLayer, comp1, comp2, interval=5.0, distance=10.0):
	thisMaster = thisLayer.associatedFontMaster()
	masterID = thisMaster.id
	original1 = comp1.component.layers[masterID]
	original2 = comp2.component.layers[masterID]
	minDist = minDistanceBetweenTwoLayers(original1, original2, interval=interval)
	if minDist is not None:
		comp2shift = distance - minDist
		addedSBs = original1.RSB + original2.LSB
		comp2.x = comp1.x + original1.width - addedSBs + comp2shift


def unsuffixed(name):
	if "." in name:
		return name[:name.find(".")]
	else:
		return name


def process(thisGlyph):
	parts = ["parenleft"] + unsuffixed(thisGlyph.name).split("_") + ["parenright"]
	maxWidth = thisFont.upm
	thisGlyph.leftMetricsKey = None
	thisGlyph.rightMetricsKey = None
	for thisLayer in thisGlyph.layers:
		thisLayer.clear()
		for i, part in enumerate(parts):
			ucName = f"{part}.case"
			lfName = f"{part}.lf"
			if thisGlyph.glyphInfo.subCategory == "Uppercase" or thisGlyph.glyphInfo.category == "Number":
				if thisFont.glyphs[ucName]:
					part = ucName
				elif thisFont.glyphs[lfName]:
					part = lfName
			comp = GSComponent(part)
			thisLayer.shapes.append(comp)
			if i > 0:
				placeComponentsAtDistance(thisLayer, thisLayer.components[i - 1], comp, distance=distanceBetweenComponents)

		maxWidth = max(thisLayer.bounds.size.width * 0.97, maxWidth)
	return maxWidth


def postprocess(thisGlyph, scale, shiftUp):
	for thisLayer in thisGlyph.layers:
		scaleDown = transform(scale=scale).transformStruct()
		thisLayer.applyTransform(scaleDown)
		thisLayer.applyTransform(shiftUp)
		lsb = (thisFont.upm - thisLayer.bounds.size.width) // 2.0
		thisLayer.LSB = lsb
		thisLayer.width = thisFont.upm

		if thisLayer.components[1].component.category == "Letter":
			thisLayer.components[0].x -= parenShiftForLetters
			thisLayer.components[2].x += parenShiftForLetters


thisFont = Glyphs.font  # frontmost font
if thisFont is None:
	Message(title="No font open", message="This script requires a font open in Glyphs.", OKButton=None)
else:
	thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
	try:
		maxWidth = 0.0
		for name in parenGlyphs:
			thisGlyph = thisFont.glyphs[name]
			if not thisGlyph:
				thisGlyph = newGlyphWithName(name)
				thisFont.glyphs.append(thisGlyph)

			print(f"Processing {thisGlyph.name}")
			# undo grouping (beginUndo/endUndo) causes crashes
			maxWidth = max(maxWidth, process(thisGlyph))

		print(maxWidth)
		scale = (thisFont.upm / maxWidth) * 0.95
		yShift = transform(shiftY=thisFont.upm * 0.08).transformStruct()

		for name in parenGlyphs:
			postprocess(thisFont.glyphs[name], scale, yShift)

	except Exception:
		Glyphs.showMacroWindow()
		print("\n⚠️ Script Error:\n")
		print(traceback.format_exc())
		raise
	finally:
		thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
