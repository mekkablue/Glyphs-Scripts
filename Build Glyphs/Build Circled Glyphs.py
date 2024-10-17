# MenuTitle: Build Circled Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Builds circled numbers and letters (U+24B6...24EA and U+2460...2473) from _part.circle and the letters and figures.
"""

from Foundation import NSPoint
from AppKit import NSRect, NSSize
import math
import vanilla
from GlyphsApp import Glyphs, GSGlyph, GSComponent, GSAnchor, GSOFFCURVE, Message
from mekkablue import mekkaObject
from mekkablue.geometry import transform, centerOfRect, offsetLayer

circledNumbers = (
	"zero.circled",
	"one.circled",
	"two.circled",
	"three.circled",
	"four.circled",
	"five.circled",
	"six.circled",
	"seven.circled",
	"eight.circled",
	"nine.circled",
	"one_zero.circled",
	"one_one.circled",
	"one_two.circled",
	"one_three.circled",
	"one_four.circled",
	"one_five.circled",
	"one_six.circled",
	"one_seven.circled",
	"one_eight.circled",
	"one_nine.circled",
	"two_zero.circled",
)

circledUC = (
	"A.circled",
	"B.circled",
	"C.circled",
	"D.circled",
	"E.circled",
	"F.circled",
	"G.circled",
	"H.circled",
	"I.circled",
	"J.circled",
	"K.circled",
	"L.circled",
	"M.circled",
	"N.circled",
	"O.circled",
	"P.circled",
	"Q.circled",
	"R.circled",
	"S.circled",
	"T.circled",
	"U.circled",
	"V.circled",
	"W.circled",
	"X.circled",
	"Y.circled",
	"Z.circled",
)

circledLC = (
	"a.circled",
	"b.circled",
	"c.circled",
	"d.circled",
	"e.circled",
	"f.circled",
	"g.circled",
	"h.circled",
	"i.circled",
	"j.circled",
	"k.circled",
	"l.circled",
	"m.circled",
	"n.circled",
	"o.circled",
	"p.circled",
	"q.circled",
	"r.circled",
	"s.circled",
	"t.circled",
	"u.circled",
	"v.circled",
	"w.circled",
	"x.circled",
	"y.circled",
	"z.circled",
)


def combinedBounds(rects):
	bottomLeft = NSPoint(1000.0, 100.0)
	topRight = NSPoint(0.0, 0.0)
	for thisRect in rects:
		bottomLeft.x = min(thisRect.origin.x, bottomLeft.x)
		bottomLeft.y = min(thisRect.origin.y, bottomLeft.y)
		topRight.x = max(topRight.x, thisRect.origin.x + thisRect.size.width)
		topRight.y = max(topRight.y, thisRect.origin.y + thisRect.size.height)
	combinedRect = NSRect()
	combinedRect.origin = bottomLeft
	combinedRect.size = NSSize(topRight.x - bottomLeft.x, topRight.y - bottomLeft.y)
	return combinedRect


def measureLayerAtHeightFromLeftOrRight(thisLayer, height, leftSide=True):
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


def minDistanceBetweenTwoLayers(comp1, comp2, interval=5.0):
	topY = min(comp1.bounds.origin.y + comp1.bounds.size.height, comp2.bounds.origin.y + comp2.bounds.size.height)
	bottomY = max(comp1.bounds.origin.y, comp2.bounds.origin.y)
	distance = topY - bottomY
	minDist = None
	for i in range(int(distance / interval)):
		height = bottomY + i * interval
		left = measureLayerAtHeightFromLeftOrRight(comp1, height, leftSide=False)
		right = measureLayerAtHeightFromLeftOrRight(comp2, height, leftSide=True)
		total = left + right
		if minDist is None or minDist > total:
			minDist = total

	if minDist is None:
		minDist = 0.0
	return minDist


def placeComponentsAtDistance(thisLayer, comp1, comp2, interval=5.0, distance=10.0):
	if comp1 is not None:
		thisMaster = thisLayer.associatedFontMaster()
		masterID = thisMaster.id
		original1 = comp1.component.layers[masterID]
		original2 = comp2.component.layers[masterID]
		minDist = minDistanceBetweenTwoLayers(original1, original2, interval=interval)
		comp2shift = distance - minDist
		addedSBs = original1.RSB + original2.LSB
		comp2.x = comp1.x + original1.width - addedSBs + comp2shift


def buildCircledGlyph(thisGlyph, circleName, scaleFactors, minDistanceBetweenTwoLayers=90.0, suffix=None):
	isBlack = "black" in circleName.lower()

	thisFont = thisGlyph.font
	thisGlyph.widthMetricsKey = None  # "=%i" % thisFont.upm)
	thisGlyph.leftMetricsKey = "=40"
	thisGlyph.rightMetricsKey = "=|"

	for i, thisMaster in enumerate(thisFont.masters):
		figureHeight = None
		scaleFactor = scaleFactors[i]
		if isBlack:
			scaleFactor = max(0.6, scaleFactor)
		circleGlyph = thisFont.glyphs[circleName]
		circleLayer = circleGlyph.layers[thisMaster.id]
		circleScaleFactor = thisFont.upm * 0.92 / max(thisFont.upm * 0.66, circleLayer.bounds.size.width)

		# prepare layer
		thisLayer = thisGlyph.layers[thisMaster.id]
		thisLayer.clear()

		# add circle:
		assumedCenter = NSPoint(thisFont.upm * 0.5, thisFont.upm * 0.3)  # hardcoded
		circleComponent = GSComponent(circleName)
		thisLayer.components.append(circleComponent)

		# scale circle:
		circleScale = transform(scale=circleScaleFactor).transformStruct()
		circleComponent.applyTransform(circleScale)

		# move circle:
		circleBounds = thisLayer.components[0].bounds
		circleCenter = centerOfRect(circleBounds)
		xShift = assumedCenter.x - circleCenter.x
		yShift = assumedCenter.y - circleCenter.y
		circleShift = transform(shiftX=xShift, shiftY=yShift).transformStruct()
		circleComponent.applyTransform(circleShift)

		# update metrics:
		thisLayer.updateMetrics()
		thisLayer.syncMetrics()

		# find number and letter components to add:
		suffixlessName = thisGlyph.name
		if "." in suffixlessName:
			suffixlessName = thisGlyph.name[:thisGlyph.name.find(".")]
		componentNames = suffixlessName.split("_")

		# add one component in the center:
		if componentNames:
			advance = 0
			for j, compName in enumerate(componentNames):
				lfName = "%s.lf" % compName
				osfName = "%s.osf" % compName

				namesToCheck = [compName]
				extraSuffixes = (".osf", ".lf")
				for extraSuffix in extraSuffixes:
					namesToCheck.insert(0, compName + extraSuffix)
				if suffix:
					for existingName in namesToCheck[:]:
						namesToCheck.insert(0, existingName + suffix)

				for nameToCheck in namesToCheck:
					if thisFont.glyphs[nameToCheck]:
						compName = nameToCheck
						break

				innerComponent = GSComponent(compName)
				innerComponent.automaticAlignment = False
				thisLayer.components.append(innerComponent)
				innerComponent.position = NSPoint(advance, 0.0)

				if j > 0:
					innerComponent.disableAlignment = True
					placeComponentsAtDistance(
						thisLayer,
						thisLayer.components[-2],
						thisLayer.components[-1],  # same as innerComponent
						distance=minDistanceBetweenTwoLayers
					)

				originalLayerWidth = thisFont.glyphs[compName].layers[thisMaster.id].width
				advance += originalLayerWidth

			collectedBounds = []
			for i in range(1, len(thisLayer.components)):
				collectedBounds.append(thisLayer.components[i].bounds)

			compCenter = centerOfRect(combinedBounds(collectedBounds))
			centerAnchor = thisLayer.anchorForName_traverseComponents_("#center", True)
			if centerAnchor:
				circleCenter = centerAnchor.position
			else:
				circleCenter = centerOfRect(circleComponent.bounds)

			# scale and move it in place:
			shift = transform(shiftX=-compCenter.x, shiftY=-compCenter.y).transformStruct()
			scaleToFit = transform(scale=scaleFactor * circleScaleFactor).transformStruct()
			backshift = transform(shiftX=circleCenter.x, shiftY=circleCenter.y).transformStruct()

			compensateStroke = []
			for i in range(1, len(thisLayer.components)):
				innerComponent = thisLayer.components[i]

				# optically shift so top anchor is in center:
				originalLayer = topAnchor = innerComponent.component.layers[thisMaster.id]
				topAnchor = originalLayer.anchors["top"]
				if topAnchor:
					anchorCenter = topAnchor.x
					boundsCenter = centerOfRect(originalLayer.bounds).x
					opticalCorrection = boundsCenter - anchorCenter
					if opticalCorrection != 0.0:
						threshold = 35.0
						if abs(opticalCorrection) > threshold:
							posNeg = opticalCorrection / abs(opticalCorrection)
							rest = abs(opticalCorrection) - threshold
							opticalCorrection = posNeg * (threshold + rest * 1 / rest**0.3)
							print("--", opticalCorrection)
						opticalShift = transform(shiftX=opticalCorrection).transformStruct()
						innerComponent.applyTransform(opticalShift)

				innerComponent.applyTransform(shift)
				innerComponent.applyTransform(scaleToFit)
				innerComponent.applyTransform(backshift)

				# move components closer to center:
				# move = 15.0
				# hOffset = circleCenter.x - centerOfRect(innerComponent.bounds).x
				# if abs(hOffset) > move:
				# 	hOffset = (hOffset/abs(hOffset))*move
				# if hOffset != 0.0:
				# 	moveCloser = transform(shiftX=hOffset).transformStruct()
				# 	innerComponent.applyTransform(moveCloser)

				# compensatory shift:
				if thisGlyph.name in ("two_zero.circled", "one_nine.circled", "one_zero.circled"):
					compensate = transform(shiftX=10.0).transformStruct()
					innerComponent.applyTransform(compensate)

				if innerComponent.component.glyphInfo.category == "Number":
					if figureHeight is None:
						figureHeight = innerComponent.position.y
					else:
						innerComponent.position.y = figureHeight

				compensateStroke.append(innerComponent)

			# make slightly bolder:
			isNumber = False
			for i in range(len(compensateStroke))[::-1]:
				componentToDecompose = compensateStroke[i]
				if componentToDecompose.component.category == "Number":
					isNumber = True
				thisLayer.decomposeComponent_(componentToDecompose)

			offsetLayer(thisLayer, 4.0)  # 4.0 if isNumber else 3.0)
			if thisLayer.paths and isBlack:
				thisLayer.removeOverlap()
				for thisPath in thisLayer.paths:

					# set first node (make compatible again after remove overlap):
					lowestY = thisPath.bounds.origin.y
					lowestNodes = [n for n in thisPath.nodes if n.y <= lowestY]
					if len(lowestNodes) == 0:
						lowestNode = sorted(lowestNodes, key=lambda node: node.y)[0]
					elif len(lowestNodes) == 1:
						lowestNode = lowestNodes[0]
					elif len(lowestNodes) > 1:
						lowestNode = sorted(lowestNodes, key=lambda node: node.x)[0]
					while lowestNode.type == GSOFFCURVE:
						lowestNode = lowestNode.nextNode
					thisPath.makeNodeFirst_(lowestNode)

					# reverse (white on black):
					thisPath.reverse()

			thisLayer.anchors = None
			for thisComp in thisLayer.components:
				if thisComp.componentName == circleName:
					thisComp.locked = True


def buildCirclePart(thisFont, glyphName, isBlack=False):
	partCircle = (
		(
			(353.0, 0.0), ((152.0, 0.0), (0.0, 150.0), (0.0, 348.0)), ((0.0, 549.0), (152.0, 700.0), (353.0, 700.0)), ((556.0, 700.0), (708.0, 549.0), (708.0, 348.0)),
			((708.0, 149.0), (556.0, 0.0), (353.0, 0.0))
		),
	)

	thisGlyph = thisFont.glyphs[glyphName]
	if not thisGlyph:
		thisGlyph = GSGlyph()
		thisGlyph.name = glyphName
		thisFont.glyphs.append(thisGlyph)
		thisGlyph.leftMetricsKey = "=40"
		thisGlyph.rightMetricsKey = "=|"
		print("Generated %s" % glyphName)

	thisGlyph.export = False

	# draw in every layer:
	for thisLayer in thisGlyph.layers:
		# make sure it is empty:
		thisLayer.clear()

		# draw outer circle:
		for thisPath in partCircle:
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

		# scale:
		refHeight = thisFont.upm - 80
		actualHeight = thisLayer.bounds.size.height
		scaleFactor = refHeight / actualHeight
		thisLayer.applyTransform(transform(scale=scaleFactor).transformStruct())

		# shift to align with capHeight:
		refY = thisLayer.associatedFontMaster().capHeight * 0.5
		actualY = thisLayer.bounds.origin.y + thisLayer.bounds.size.height * 0.5
		shift = refY - actualY
		thisLayer.applyTransform(transform(shiftY=shift).transformStruct())

		if not isBlack:

			# inner circle, scaled down:
			currentHeight = thisLayer.bounds.size.height
			outerCircle = thisLayer.paths[0]
			innerCircle = outerCircle.copy()
			thisLayer.paths.append(innerCircle)

			# get stems
			hstems = []
			vstems = []

			masterStems = thisLayer.associatedFontMaster().stems
			if not thisFont.stems:
				Message(title="Error: no stems set", message="The script requires H and V stems set in Font Info > Masters.", OKButton=None)
				break

			for i, stem in enumerate(thisFont.stems):
				if stem.horizontal:
					hstems.append(masterStems[i])
				else:
					vstems.append(masterStems[i])

			# scale down inner circle:
			stemSize = 50.0
			if hstems and vstems:
				stemSize = (hstems[0] + vstems[0]) * 0.25

			maximumStemSize = currentHeight * 0.28
			stemSize = min(maximumStemSize, stemSize)
			smallerBy = stemSize * 2 * 1.06
			newHeight = currentHeight - smallerBy
			scaleFactor = newHeight / currentHeight
			scale = transform(scale=scaleFactor).transformStruct()

			centerX = innerCircle.bounds.origin.x + innerCircle.bounds.size.width * 0.5
			centerY = innerCircle.bounds.origin.y + innerCircle.bounds.size.height * 0.5
			shift = transform(shiftX=-centerX, shiftY=-centerY).transformStruct()
			shiftBack = transform(shiftX=centerX, shiftY=centerY).transformStruct()

			innerCircle.applyTransform(shift)
			innerCircle.applyTransform(scale)
			innerCircle.applyTransform(shiftBack)

		# tidy up paths and set width:
		thisLayer.correctPathDirection()
		thisLayer.cleanUpPaths()
		thisLayer.updateMetrics()
		thisLayer.syncMetrics()

		# add anchor:
		centerX = thisLayer.bounds.origin.x + thisLayer.bounds.size.width * 0.5
		centerY = thisLayer.bounds.origin.y + thisLayer.bounds.size.height * 0.5
		centerAnchor = GSAnchor()
		centerAnchor.name = "#center"
		centerAnchor.position = NSPoint(centerX, centerY)
		thisLayer.anchors.append(centerAnchor)


def boxArea(thisLayer):
	return thisLayer.bounds.size.width * thisLayer.bounds.size.height


class BuildCircledGlyphs(mekkaObject):
	prefDict = {
		"buildUC": 0,
		"buildLC": 0,
		"buildBlackUC": 0,
		"buildBlackLC": 0,
		"buildCircledNumbers": 1,
		"buildBlackCircledNumbers": 0,
		"minDistanceBetweenFigures": "90",
		"suffixesCheckbox": 0,
		"suffixes": "ss02, ss06",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 230
		windowHeight = 251
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Build Circled Glyphs",  # window title
			minSize=(windowWidth, windowHeight + 19),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize + 19),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), u"Builds the following glyphs:", sizeStyle='small', selectable=True)
		self.w.descriptionText.getNSTextField().setToolTip_("Hint: if the letter or figure glyph contains #center anchors, the anchor position will be preferred for positioning the letter or figure inside the circle.")
		linePos += lineHeight

		self.w.buildUC = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), u"Uppercase circled letters", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildUC.getNSButton().setToolTip_("ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂ︎ⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ")
		linePos += lineHeight

		self.w.buildLC = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), u"Lowercase circled letters", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildLC.getNSButton().setToolTip_("ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ")
		linePos += lineHeight

		self.w.buildCircledNumbers = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), u"Circled numbers 0-20", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildCircledNumbers.getNSButton().setToolTip_("🄋①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳")
		linePos += lineHeight

		self.w.buildBlackUC = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), u"Black uppercase circled letters", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildBlackUC.getNSButton().setToolTip_("🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩")
		linePos += lineHeight

		self.w.buildBlackLC = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), u"Black lowercase circled letters ⚠️", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildBlackLC.getNSButton().setToolTip_("Do not exist in Unicode. You will have to make them accessible through OpenType features.")
		linePos += lineHeight

		self.w.buildBlackCircledNumbers = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), u"Black circled numbers 0-20", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.buildBlackCircledNumbers.getNSButton().setToolTip_("⓿❶❷❸❹❺❻❼❽❾❿⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴")
		linePos += lineHeight

		self.w.minDistanceBetweenFiguresText = vanilla.TextBox((inset, linePos + 2, 145, 14), u"Distance between figures:", sizeStyle='small', selectable=True)
		self.w.minDistanceBetweenFigures = vanilla.EditText((inset + 145, linePos - 1, -inset, 19), "90", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.suffixesCheckbox = vanilla.CheckBox((inset + 2, linePos, 110, 20), "Include Suffixes:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.suffixes = vanilla.EditText((inset + 110, linePos, -inset, 19), "ss06, ss02", callback=self.SavePreferences, sizeStyle='small')
		self.w.suffixes.getNSTextField().setToolTip_("Will look if there is a base glyph with a dot suffix, and build the circled glyph with the same suffix. Separate multiple suffixes with a comma. E.g. You have an A and an A.ss06, then you get A.blackCircled and A.blackCircled.ss06, provided you enter ss06 here.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Build", callback=self.BuildCircledGlyphsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def turnBlack(self, glyphNames):
		searchFor = ".circled"
		replaceWith = ".blackCircled"
		blackGlyphNames = [n.replace(searchFor, replaceWith) for n in glyphNames if n.endswith(searchFor)]
		return blackGlyphNames

	def BuildCircledGlyphsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			minDistanceBetweenFigures = 90.0
			thisFont = Glyphs.font  # frontmost font

			buildUC = self.pref("buildUC")
			buildLC = self.pref("buildLC")
			buildCircledNumbers = self.pref("buildCircledNumbers")
			buildBlackUC = self.pref("buildBlackUC")
			buildBlackLC = self.pref("buildBlackLC")
			buildBlackCircledNumbers = self.pref("buildBlackCircledNumbers")
			minDistanceBetweenFigures = self.prefFloat("minDistanceBetweenFigures")
			shouldIncludeSuffixes = self.pref("suffixesCheckbox")
			suffixes = self.pref("suffixes")
			if shouldIncludeSuffixes:
				suffixes = [("." + x.strip()).replace("..", ".") for x in suffixes.split(",")]
			else:
				suffixes = ()

			circledGlyphNames = []
			if buildUC:
				circledGlyphNames.extend(circledUC)
			if buildLC:
				circledGlyphNames.extend(circledLC)
			if buildCircledNumbers:
				circledGlyphNames.extend(circledNumbers)
			if buildBlackUC:
				circledGlyphNames.extend(self.turnBlack(circledUC))
			if buildBlackLC:
				circledGlyphNames.extend(self.turnBlack(circledLC))
			if buildBlackCircledNumbers:
				circledGlyphNames.extend(self.turnBlack(circledNumbers))

			if not thisFont:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			elif circledGlyphNames:
				print("Build Circled Glyphs Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
				try:
					print("Building: %s\n" % ", ".join(circledGlyphNames))

					# add circles if present not in font already:
					circleName = "_part.circle"
					if not thisFont.glyphs[circleName]:
						buildCirclePart(thisFont, circleName)
					circleGlyph = thisFont.glyphs[circleName]

					blackCircleGlyph = None
					if buildBlackUC or buildBlackLC or buildBlackCircledNumbers:
						blackCircleName = "_part.blackCircle"
						if not thisFont.glyphs[blackCircleName]:
							buildCirclePart(thisFont, blackCircleName, isBlack=True)
						blackCircleGlyph = thisFont.glyphs[blackCircleName]

					# determining scale of inscribed letters:
					scaleFactors = []
					for thisMaster in thisFont.masters:
						radius = circleGlyph.layers[thisMaster.id].paths[1].bounds.size.width * 0.5
						maxArea = 0.0
						biggestLayer = None
						for glyphName in circledGlyphNames:
							if "." in glyphName:
								glyphName = glyphName[:glyphName.find(".")]

							glyphNames = [glyphName]
							if suffixes:
								for suffix in suffixes:
									glyphNames.append("%s%s" % (glyphName, suffix))

							for glyphName in glyphNames:
								thisGlyph = thisFont.glyphs[glyphName]
								if thisGlyph:
									thisLayer = thisGlyph.layers[thisMaster.id]
									thisArea = boxArea(thisLayer)
									if thisArea > maxArea:
										maxArea = thisArea
										biggestLayer = thisLayer

						if biggestLayer:
							height = biggestLayer.bounds.size.height
							width = biggestLayer.bounds.size.width
						else:
							# fallback values
							height, width = 700.0, 500.0
							print("⚠️ Warning: could not determine bounds of relevant layers, resorting to defaults. Are the glyphs empty?")

						angleInRadians = math.atan2(height, width * 1.4 + minDistanceBetweenFigures)
						scaledHeight = math.sin(angleInRadians) * radius * 2 * 0.9
						scaleFactor = scaledHeight / height
						scaleFactors.append(scaleFactor)
						print("Scale factor for master '%s': %.1f" % (thisMaster.name, scaleFactor))

					# actually building letters:
					for glyphName in circledGlyphNames:
						if "black" in glyphName.lower():
							circleName = blackCircleName

						# check for suffixes:
						coreName = glyphName[:glyphName.find(".")]
						coreNames = [coreName]
						glyphNames = [glyphName]
						suffixDict = {}
						if suffixes:
							for suffix in suffixes:
								suffixedCoreName = coreName + suffix
								if "_" in coreName:
									particles = coreName.split("_")
									if suffixedCoreName not in coreNames:
										for particle in particles:
											if thisFont.glyphs[particle + suffix]:
												coreNames.append(suffixedCoreName)
												newGlyphName = glyphName + suffix
												glyphNames.append(newGlyphName)
												suffixDict[newGlyphName] = suffix
								else:
									if thisFont.glyphs[suffixedCoreName]:
										coreNames.append(suffixedCoreName)
										newGlyphName = glyphName + suffix
										glyphNames.append(newGlyphName)
										suffixDict[newGlyphName] = suffix

						for i, glyphName in enumerate(glyphNames):
							thisGlyph = thisFont.glyphs[glyphName]

							# generate it if it does not exist
							if not thisGlyph:
								thisGlyph = GSGlyph()
								thisGlyph.name = glyphName
								thisFont.glyphs.append(thisGlyph)
								thisGlyph.updateGlyphInfo()

							if glyphName in suffixDict:
								suffix = suffixDict[glyphName]
							else:
								suffix = None

							# thisGlyph.beginUndo()  # undo grouping causes crashes
							print("Building %s" % thisGlyph.name)
							buildCircledGlyph(thisGlyph, circleName, scaleFactors, minDistanceBetweenFigures, suffix)
							# thisGlyph.endUndo()  # undo grouping causes crashes

				except Exception as e:
					Glyphs.showMacroWindow()
					print("\n⚠️ Script Error:\n")
					import traceback
					print(traceback.format_exc())
					print()
					raise e
				finally:
					thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

				self.w.close()  # delete if you want window to stay open

			# Final report:
			Glyphs.showNotification(
				u"%s: Done" % (thisFont.familyName),
				u"Build Circled Glyphs is finished. Details in Macro Window",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Build Circled Glyphs Error: %s" % e)
			import traceback
			print(traceback.format_exc())


BuildCircledGlyphs()
