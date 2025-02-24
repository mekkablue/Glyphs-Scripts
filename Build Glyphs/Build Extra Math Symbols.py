# MenuTitle: Build Extra Math Symbols
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates lessoverequal, greateroverequal, bulletoperator, rightanglearc, righttriangle, sphericalangle, measuredangle, sunWithRays, positionIndicator, diameterSign, viewdataSquare, control.
"""

from GlyphsApp import Glyphs, GSGlyph, GSComponent
from mekkablue.geometry import transform, centerOfRect

thisFont = Glyphs.font  # frontmost font
selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs


def getZeroGlyph(thisFont):
	# find zero:
	zeroGlyph = thisFont.glyphs["zero.lf"]
	if not zeroGlyph:
		zeroGlyph = thisFont.glyphs["zero.tf"]
		if not zeroGlyph:
			zeroGlyph = thisFont.glyphs["zero"]
	return zeroGlyph


def overequal(Layer):
	Layer.clear()
	comp1 = GSComponent("equal")
	Layer.components.append(comp1)
	verticaloffset = comp1.bounds.origin.y
	tMatrix = transform(shiftY=-verticaloffset).transformStruct()
	comp1.applyTransform(tMatrix)
	topedge = comp1.bounds.origin.y + comp1.bounds.size.height
	distance = comp1.bounds.size.height * 0.2

	if "less" in Layer.parent.name:
		rightedge = comp1.bounds.origin.x + comp1.bounds.size.width
		comp2 = GSComponent("less")
		Layer.components.append(comp2)
		xShift = rightedge - (comp2.bounds.origin.x + comp2.bounds.size.width)
		yShift = topedge + distance - comp2.bounds.origin.y
		tMatrix = transform(shiftX=xShift, shiftY=yShift).transformStruct()
		comp2.applyTransform(tMatrix)

		Layer.parent.rightMetricsKey = "=equal"
		Layer.parent.leftMetricsKey = None  # "=equal"

	if "greater" in Layer.parent.name:
		leftedge = comp1.bounds.origin.x
		comp2 = GSComponent("greater")
		Layer.components.append(comp2)
		xShift = leftedge - comp2.bounds.origin.x
		yShift = topedge + distance - comp2.bounds.origin.y
		tMatrix = transform(shiftX=xShift, shiftY=yShift).transformStruct()
		comp2.applyTransform(tMatrix)

		Layer.parent.leftMetricsKey = "=equal"

	Layer.parent.widthMetricsKey = "=equal"
	Layer.syncMetrics()
	Layer.syncMetrics()


def getGlyphWithName(glyphName, thisFont):
	thisGlyph = thisFont.glyphs[glyphName]
	if thisGlyph:
		return thisGlyph
	else:
		newGlyph = GSGlyph(glyphName)
		thisFont.glyphs.append(newGlyph)
		newGlyph.updateGlyphInfo()
		return newGlyph


def drawPenDataInLayer(thisLayer, penData):
	# make sure it is empty:
	thisLayer.clear()

	# draw outer circle:
	for thisPath in penData:
		pen = thisLayer.getPen()
		pen.moveTo(thisPath[0])
		for thisSegment in thisPath[1:]:
			if len(thisSegment) == 2:  # lineto
				pen.lineTo(thisSegment)
			elif len(thisSegment) == 3:  # curveto
				pen.curveTo(thisSegment[0], thisSegment[1], thisSegment[2])
			else:
				print("%s: Path drawing error. Could not process this segment: %s\n" % (glyphName, thisSegment))
		pen.closePath()
		pen.endPath()


thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	# over equal:
	for glyphName in ("lessoverequal", "greateroverequal"):
		thisGlyph = getGlyphWithName(glyphName, thisFont)
		# thisGlyph.beginUndo()  # undo grouping causes crashes
		for thisMaster in thisFont.masters:
			masterID = thisMaster.id
			thisLayer = thisGlyph.layers[masterID]
			overequal(thisLayer)
		# thisGlyph.endUndo()  # undo grouping causes crashes

	# bullet operator:
	thisGlyph = getGlyphWithName("bulletoperator", thisFont)
	thisGlyph.leftMetricsKey = "=plus"
	thisGlyph.rightMetricsKey = "=plus"
	zeroGlyph = getZeroGlyph(thisFont)
	for thisMaster in thisFont.masters:
		masterID = thisMaster.id
		thisLayer = thisGlyph.layers[masterID]
		thisLayer.clear()
		# add period component:
		dot = GSComponent("period")
		thisLayer.components.append(dot)
		# determine shift:
		dotCenter = centerOfRect(dot.bounds)
		zeroCenter = centerOfRect(zeroGlyph.layers[masterID].bounds)
		shiftUp = zeroCenter.y - dotCenter.y
		# shift:
		tMatrix = transform(shiftY=shiftUp).transformStruct()
		dot.applyTransform(tMatrix)
		thisLayer.syncMetrics()

	# path drawings:
	penDrawings = {
		"rightanglearc:0": (
			((50.0, 600.0), (50.0, 0.0), (100.0, 0.0), (100.0, 600.0), (50.0, 600.0)), ((50.0, 50.0), (50.0, 0.0), (622.0, 0.0), (622.0, 50.0), (50.0, 50.0)),
			((98.0, 368.0), ((290.0, 368.0), (418.0, 240.0), (418.0, 48.0)), (468.0, 48.0), ((468.0, 270.0), (320.0, 418.0), (98.0, 418.0)), (98.0, 368.0))
		),
		"rightanglearc:1": (
			((50.0, 600.0), (50.0, 0.0), (150.0, 0.0), (150.0, 600.0), (50.0, 600.0)), ((50.0, 100.0), (50.0, 0.0), (622.0, 0.0), (622.0, 100.0), (50.0, 100.0)),
			((148.0, 338.0), ((305.0, 338.0), (388.0, 255.0), (388.0, 98.0)), (488.0, 98.0), ((488.0, 311.0), (361.0, 438.0), (148.0, 438.0)), (148.0, 338.0))
		),
		"righttriangle:0": (
			((50.0, 0.0), (652.0, 0.0), (652.0, 633.0), (50.0, 0.0)),
			((602.0, 50.0), (114.0, 50.0), (106.0, 26.0), (626.0, 573.0), (602.0, 565.0), (602.0, 50.0)),
		),
		"righttriangle:1": (
			((50.0, 0.0), (652.0, 0.0), (652.0, 633.0), (50.0, 0.0)),
			((552.0, 100.0), (158.0, 100.0), (126.0, 26.0), (626.0, 553.0), (552.0, 518.0), (552.0, 100.0)),
		),
		"sphericalangle:0": (
			((584.0, 71.0), (141.0, 272.0), (141.0, 244.0), (584.0, 445.0), (564.0, 491.0), (50.0, 258.0), (564.0, 25.0), (584.0, 71.0)),
			((351.0, 481.0), ((476.0, 358.0), (476.0, 157.0), (351.0, 34.0)), (387.0, -2.0), ((531.0, 141.0), (532.0, 374.0), (387.0, 517.0)), (351.0, 481.0)),
		),
		"sphericalangle:1": (
			((615.0, 89.0), (206.0, 274.0), (206.0, 232.0), (615.0, 417.0), (573.0, 509.0), (50.0, 253.0), (573.0, -3.0), (615.0, 89.0)),
			((360.0, 463.0), ((469.0, 325.0), (469.0, 180.0), (360.0, 42.0)), (448.0, -20.0), ((590.0, 159.0), (590.0, 346.0), (448.0, 525.0)), (360.0, 463.0)),
		),
		"measuredangle:0": (
			((50.0, 75.0), (602.0, 75.0), (602.0, 125.0), (142.0, 125.0), (151.0, 102.0), (498.0, 415.0), (464.0, 453.0), (50.0, 75.0)),
			((466.0, 7.0), (516.0, 7.0), ((516.0, 211.0), (441.0, 355.0), (307.0, 439.0)), (278.0, 398.0), ((399.0, 325.0), (466.0, 196.0), (466.0, 7.0))),
		),
		"measuredangle:1": (
			((50.0, 60.0), (639.0, 60.0), (639.0, 150.0), (240.0, 150.0), (253.0, 126.0), (547.0, 383.0), (481.0, 457.0), (50.0, 60.0)),
			((463.0, -7.0), (573.0, -7.0), ((573.0, 201.0), (490.0, 368.0), (345.0, 467.0)), (276.0, 379.0), ((396.0, 300.0), (463.0, 169.0), (463.0, -7.0))),
		),
		"sunWithRays:0": (
			(
				(387.0, 116.0), ((500.0, 117.0), (592.0, 210.0), (592.0, 322.0)), ((592.0, 435.0), (500.0, 528.0), (387.0, 528.0)),
				((273.0, 528.0), (180.0, 435.0), (180.0, 322.0)), ((180.0, 208.0), (273.0, 115.0), (387.0, 116.0))
			),
			(
				(387.0, 161.0), ((295.0, 161.0), (225.0, 230.0), (225.0, 322.0)), ((225.0, 413.0), (295.0, 482.0), (387.0, 482.0)),
				((478.0, 482.0), (547.0, 413.0), (547.0, 322.0)), ((547.0, 230.0), (478.0, 161.0), (387.0, 161.0))
			),
			((50.0, 348.0), (50.0, 297.0), (205.0, 297.0), (205.0, 348.0), (50.0, 348.0)),
			((567.0, 348.0), (567.0, 297.0), (722.0, 297.0), (722.0, 348.0), (567.0, 348.0)),
			((166.0, 579.0), (130.0, 543.0), (239.0, 434.0), (275.0, 470.0), (166.0, 579.0)),
			((534.0, 211.0), (498.0, 175.0), (607.0, 66.0), (643.0, 102.0), (534.0, 211.0)),
			((412.0, 660.0), (361.0, 660.0), (361.0, 506.0), (412.0, 506.0), (412.0, 660.0)),
			((412.0, 139.0), (361.0, 139.0), (361.0, -15.0), (412.0, -15.0), (412.0, 139.0)),
			((643.0, 543.0), (607.0, 579.0), (498.0, 470.0), (534.0, 434.0), (643.0, 543.0)),
			((275.0, 175.0), (239.0, 211.0), (130.0, 102.0), (166.0, 66.0), (275.0, 175.0)),
		),
		"sunWithRays:1": (
			(
				(402.0, 116.0), ((515.0, 117.0), (607.0, 210.0), (607.0, 322.0)), ((607.0, 435.0), (515.0, 528.0), (402.0, 528.0)),
				((288.0, 528.0), (195.0, 435.0), (195.0, 322.0)), ((195.0, 208.0), (288.0, 115.0), (402.0, 116.0))
			),
			(
				(402.0, 211.0), ((338.0, 211.0), (290.0, 258.0), (290.0, 322.0)), ((290.0, 385.0), (338.0, 432.0), (402.0, 432.0)),
				((464.0, 432.0), (512.0, 385.0), (512.0, 322.0)), ((512.0, 258.0), (464.0, 211.0), (402.0, 211.0))
			),
			((50.0, 363.0), (50.0, 282.0), (235.0, 282.0), (235.0, 363.0), (50.0, 363.0)),
			((567.0, 363.0), (567.0, 282.0), (752.0, 282.0), (752.0, 363.0), (567.0, 363.0)),
			((181.0, 600.0), (124.0, 543.0), (254.0, 413.0), (311.0, 470.0), (181.0, 600.0)),
			((549.0, 232.0), (492.0, 175.0), (622.0, 45.0), (679.0, 102.0), (549.0, 232.0)),
			((442.0, 675.0), (361.0, 675.0), (361.0, 491.0), (442.0, 491.0), (442.0, 675.0)),
			((442.0, 154.0), (361.0, 154.0), (361.0, -30.0), (442.0, -30.0), (442.0, 154.0)),
			((679.0, 543.0), (622.0, 600.0), (492.0, 470.0), (549.0, 413.0), (679.0, 543.0)),
			((311.0, 175.0), (254.0, 232.0), (124.0, 102.0), (181.0, 45.0), (311.0, 175.0)),
		),
		"positionIndicator:0": (
			((50.0, 311.0), (50.0, 281.0), (750.0, 281.0), (750.0, 311.0), (50.0, 311.0)),
			((415.0, 646.0), (385.0, 646.0), (385.0, -54.0), (415.0, -54.0), (415.0, 646.0)),
			(
				(400.0, 67.0), ((533.0, 67.0), (629.0, 163.0), (629.0, 296.0)), ((629.0, 429.0), (533.0, 525.0), (400.0, 525.0)), ((267.0, 525.0), (171.0, 429.0), (171.0, 296.0)),
				((171.0, 163.0), (267.0, 67.0), (400.0, 67.0))
			),
			(
				(400.0, 102.0), ((287.0, 102.0), (206.0, 183.0), (206.0, 296.0)), ((206.0, 409.0), (287.0, 490.0), (400.0, 490.0)),
				((513.0, 490.0), (594.0, 409.0), (594.0, 296.0)), ((594.0, 183.0), (513.0, 102.0), (400.0, 102.0))
			),
		),
		"positionIndicator:1": (
			((50.0, 321.0), (50.0, 271.0), (750.0, 271.0), (750.0, 321.0), (50.0, 321.0)),
			((425.0, 646.0), (375.0, 646.0), (375.0, -54.0), (425.0, -54.0), (425.0, 646.0)),
			(
				(400.0, 62.0), ((536.0, 62.0), (634.0, 160.0), (634.0, 296.0)), ((634.0, 432.0), (536.0, 530.0), (400.0, 530.0)), ((264.0, 530.0), (166.0, 432.0), (166.0, 296.0)),
				((166.0, 160.0), (264.0, 62.0), (400.0, 62.0))
			),
			(
				(400.0, 112.0), ((287.0, 112.0), (216.0, 183.0), (216.0, 296.0)), ((216.0, 409.0), (287.0, 480.0), (400.0, 480.0)),
				((513.0, 480.0), (584.0, 409.0), (584.0, 296.0)), ((584.0, 183.0), (513.0, 112.0), (400.0, 112.0))
			),
		),
		"diameterSign:0": (
			(
				(321.0, -5.0), ((471.0, -5.0), (590.0, 114.0), (590.0, 266.0)), ((590.0, 416.0), (471.0, 535.0), (321.0, 535.0)), ((169.0, 535.0), (50.0, 416.0), (50.0, 266.0)),
				((50.0, 114.0), (169.0, -5.0), (321.0, -5.0))
			),
			(
				(321.0, 35.0), ((191.0, 35.0), (90.0, 136.0), (90.0, 266.0)), ((90.0, 394.0), (191.0, 495.0), (321.0, 495.0)), ((449.0, 495.0), (550.0, 394.0), (550.0, 266.0)),
				((550.0, 136.0), (449.0, 35.0), (321.0, 35.0))
			),
			((84.0, 1.0), (584.0, 501.0), (556.0, 529.0), (56.0, 29.0), (84.0, 1.0)),
		),
		"diameterSign:1": (
			(
				(341.0, -5.0), ((502.0, -5.0), (630.0, 124.0), (630.0, 286.0)), ((630.0, 447.0), (502.0, 575.0), (341.0, 575.0)), ((179.0, 575.0), (50.0, 447.0), (50.0, 286.0)),
				((50.0, 123.0), (178.0, -5.0), (341.0, -5.0))
			),
			(
				(341.0, 75.0), ((222.0, 75.0), (130.0, 167.0), (130.0, 286.0)), ((130.0, 403.0), (223.0, 495.0), (341.0, 495.0)), ((458.0, 495.0), (550.0, 403.0), (550.0, 286.0)),
				((550.0, 168.0), (458.0, 75.0), (341.0, 75.0))
			),
			((118.0, 7.0), (618.0, 507.0), (562.0, 563.0), (62.0, 63.0), (118.0, 7.0)),
		),
		"viewdataSquare:0": (
			((50.0, 430.0), (748.0, 430.0), (748.0, 468.0), (50.0, 468.0), (50.0, 430.0)),
			((230.0, -50.0), (268.0, -50.0), (268.0, 648.0), (230.0, 648.0), (230.0, -50.0)),
			((50.0, 130.0), (748.0, 130.0), (748.0, 168.0), (50.0, 168.0), (50.0, 130.0)),
			((530.0, -50.0), (568.0, -50.0), (568.0, 648.0), (530.0, 648.0), (530.0, -50.0)),
		),
		"viewdataSquare:1": (
			((50.0, 410.0), (748.0, 410.0), (748.0, 478.0), (50.0, 478.0), (50.0, 410.0)),
			((220.0, -50.0), (288.0, -50.0), (288.0, 648.0), (220.0, 648.0), (220.0, -50.0)),
			((50.0, 120.0), (748.0, 120.0), (748.0, 188.0), (50.0, 188.0), (50.0, 120.0)),
			((510.0, -50.0), (578.0, -50.0), (578.0, 648.0), (510.0, 648.0), (510.0, -50.0)),
		),

		# butted to the top of zero:
		"control:0": (
			((118.0, 411.0), (292.0, 585.0), (467.0, 411.0), (495.0, 439.0), (292.0, 641.0), (90.0, 439.0), (118.0, 411.0)),
			),
		"control:1": (
			((132.0, 397.0), (292.0, 557.0), (453.0, 397.0), (509.0, 453.0), (292.0, 669.0), (76.0, 453.0), (132.0, 397.0)),
			),

		#  # center of xHeight:
		# "downArrowHead:0" : (
		# 	((312.0, 320.0), (179.0, 155.0), (213.0, 155.0), (80.0, 320.0), (50.0, 294.0), (196.0, 119.0), (342.0, 294.0), (312.0, 320.0)),
		# ),
		# "downArrowHead:1" : (
		# 	((325.0, 343.0), (189.0, 173.0), (245.0, 173.0), (110.0, 343.0), (50.0, 291.0), (217.0, 99.0), (385.0, 291.0), (325.0, 343.0)),
		# )
	}

	for fullName in penDrawings:
		masterIndex = 0
		parts = fullName.split(":")
		penDrawing = parts[0]
		if len(parts) == 2:
			masterIndex = int(parts[1])

		thisMaster = thisFont.masters[masterIndex]
		thisGlyph = getGlyphWithName(penDrawing, thisFont)
		thisGlyph.rightMetricsKey = "=|"
		thisLayer = thisGlyph.layers[thisMaster.id]
		otherBackgroundLayer = thisGlyph.layers[thisFont.masters[1 - masterIndex].id].background
		drawPenDataInLayer(thisLayer, penDrawings[fullName])
		drawPenDataInLayer(otherBackgroundLayer, penDrawings[fullName])
		thisLayer.LSB = thisLayer.RSB
		thisLayer.cleanUpPaths()

		if penDrawing == "control":
			currentTop = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
			zero = getZeroGlyph(thisFont).layers[thisMaster.id]
			zeroTop = zero.bounds.origin.y + zero.bounds.size.height
			upShift = transform(shiftY=(zeroTop - currentTop)).transformStruct()
			thisLayer.applyTransform(upShift)

			downArrow = getGlyphWithName("downArrowHead", thisFont)
			downArrowLayer = downArrow.layers[thisMaster.id]
			downArrowLayer.clear()
			for origPath in thisLayer.paths:
				downArrowLayer.paths.append(origPath.copy())
			shift = transform(shiftX=-centerOfRect(thisLayer.bounds).x, shiftY=-thisMaster.capHeight * 0.5).transformStruct()
			rotate = transform(rotate=180).transformStruct()
			shiftBack = transform(shiftX=downArrowLayer.width * 0.5, shiftY=thisMaster.xHeight).transformStruct()
			for t in (shift, rotate, shiftBack):
				downArrowLayer.applyTransform(t)

			metricKey = "=%s" % penDrawing
			downArrow.leftMetricsKey = metricKey
			downArrow.rightMetricsKey = metricKey
			downArrowLayer.updateMetrics()
			downArrowLayer.LSB = thisLayer.LSB
			downArrowLayer.RSB = thisLayer.RSB

		elif penDrawing == "diameterSign":
			# copy drawings to emptyset:
			emptyset = getGlyphWithName("emptyset", thisFont)
			emptysetLayer = emptyset.layers[thisMaster.id]
			emptysetLayer.clear()
			emptysetLayer.background.clear()
			for thisPath in thisLayer.paths:
				emptysetLayer.paths.append(thisPath.copy())
			for thisPath in thisLayer.background.paths:
				emptysetLayer.background.paths.append(thisPath.copy())

			# scale to zero
			zero = getZeroGlyph(thisFont).layers[thisMaster.id]
			zoomFactor = zero.bounds.size.height / thisLayer.bounds.size.height
			zoom = transform(scale=zoomFactor).transformStruct()
			emptysetLayer.applyTransform(zoom)

			# zoom background as well:
			try:
				zoomFactor = zero.bounds.size.height / thisLayer.background.bounds.size.height
				zoom = transform(scale=zoomFactor).transformStruct()
				emptysetLayer.background.applyTransform(zoom)
			except:
				print("ERROR: could not zoom background")

			metricKey = "=%s" % penDrawing
			emptyset.leftMetricsKey = metricKey
			emptyset.rightMetricsKey = metricKey
			emptysetLayer.updateMetrics()
			emptysetLayer.LSB = thisLayer.LSB
			emptysetLayer.RSB = thisLayer.RSB

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
