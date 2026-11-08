# MenuTitle: Build Circled Glyphs
__doc__ = """
Builds circled numbers and letters (U+24B6...24EA and U+2460...2473) from _part.circle and the letters and figures.
"""

from Foundation import NSNumberFormatter, NSPoint
from AppKit import (
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityWindowSizeStayPut,
	NSRect,
	NSSize,
	NSWindowStyleMaskResizable,
)
import math
import objc
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


def combinedBounds(rects):
	# start from the first rect; hardcoded start values break for figures above 100 units or fonts wider than 1000 upm
	firstRect = rects[0]
	bottomLeft = NSPoint(firstRect.origin.x, firstRect.origin.y)
	topRight = NSPoint(firstRect.origin.x + firstRect.size.width, firstRect.origin.y + firstRect.size.height)
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


def buildCircledGlyph(thisGlyph, circleName, scaleFactors, figureDistance=90.0, suffix=None):
	isBlack = "black" in circleName.lower()

	thisFont = thisGlyph.font
	thisGlyph.widthMetricsKey = None
	thisGlyph.leftMetricsKey = "=40"
	thisGlyph.rightMetricsKey = "=|"

	for masterIndex, thisMaster in enumerate(thisFont.masters):
		figureHeight = None
		scaleFactor = scaleFactors[masterIndex]
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
		thisLayer.shapes.append(circleComponent)

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
				thisLayer.shapes.append(innerComponent)
				innerComponent.position = NSPoint(advance, 0.0)

				if j > 0:
					innerComponent.disableAlignment = True
					placeComponentsAtDistance(
						thisLayer,
						thisLayer.components[-2],
						thisLayer.components[-1],  # same as innerComponent
						distance=figureDistance
					)

				originalLayerWidth = thisFont.glyphs[compName].layers[thisMaster.id].width
				advance += originalLayerWidth

			collectedBounds = []
			for innerComponent in thisLayer.components[1:]:  # skip the circle
				collectedBounds.append(innerComponent.bounds)

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
			for innerComponent in thisLayer.components[1:]:  # skip the circle
				# optically shift so top anchor is in center:
				originalLayer = innerComponent.component.layers[thisMaster.id]
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
						opticalShift = transform(shiftX=opticalCorrection).transformStruct()
						innerComponent.applyTransform(opticalShift)

				innerComponent.applyTransform(shift)
				innerComponent.applyTransform(scaleToFit)
				innerComponent.applyTransform(backshift)

				# compensatory shift:
				if thisGlyph.name in ("two_zero.circled", "one_nine.circled", "one_zero.circled"):
					compensate = transform(shiftX=10.0).transformStruct()
					innerComponent.applyTransform(compensate)

				if innerComponent.component.glyphInfo.category == "Number":
					if figureHeight is None:
						figureHeight = innerComponent.position.y
					else:
						innerComponent.position = NSPoint(innerComponent.position.x, figureHeight)

				compensateStroke.append(innerComponent)

			# make slightly bolder:
			for componentToDecompose in reversed(compensateStroke):
				thisLayer.decomposeComponent_(componentToDecompose)

			offsetLayer(thisLayer, 4.0)
			if thisLayer.paths and isBlack:
				thisLayer.removeOverlap()
				for thisPath in thisLayer.paths:

					# set first node (make compatible again after remove overlap):
					lowestY = thisPath.bounds.origin.y
					lowestNodes = [n for n in thisPath.nodes if n.y <= lowestY]
					if len(lowestNodes) == 0:
						# floating-point mismatch after removeOverlap: fall back to all nodes
						lowestNode = sorted(thisPath.nodes, key=lambda node: (node.y, node.x))[0]
					elif len(lowestNodes) == 1:
						lowestNode = lowestNodes[0]
					else:
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

	if not isBlack and not thisFont.stems:
		Message(title="Error: no stems set", message="The script requires H and V stems set in Font Info > Masters.", OKButton=None)
		return False

	thisGlyph = thisFont.glyphs[glyphName]
	if not thisGlyph:
		thisGlyph = GSGlyph()
		thisGlyph.name = glyphName
		thisFont.glyphs.append(thisGlyph)
		thisGlyph.leftMetricsKey = "=40"
		thisGlyph.rightMetricsKey = "=|"
		print(f"Generated {glyphName}")

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
			thisLayer.shapes.append(innerCircle)

			# get stems
			hstems = []
			vstems = []

			masterStems = thisLayer.associatedFontMaster().stems
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
	return True


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
		"openInNewTab": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 290
		windowWidthResize = 100  # user can widen the window by this value
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Build Circled Glyphs",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Builds the following glyphs:", sizeStyle="small", selectable=True)
		self.w.descriptionText.setToolTip("Hint: if the letter or figure glyph contains #center anchors, the anchor position will be preferred for positioning the letter or figure inside the circle.")

		self.w.buildUC = vanilla.CheckBox("auto", "Uppercase circled letters", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.buildUC.setToolTip("ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂ︎ⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ")

		self.w.buildLC = vanilla.CheckBox("auto", "Lowercase circled letters", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.buildLC.setToolTip("ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ")

		self.w.buildCircledNumbers = vanilla.CheckBox("auto", "Circled numbers 0-20", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.buildCircledNumbers.setToolTip("🄋①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳")

		self.w.buildBlackUC = vanilla.CheckBox("auto", "Black uppercase circled letters", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.buildBlackUC.setToolTip("🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩")

		self.w.buildBlackLC = vanilla.CheckBox("auto", "Black lowercase circled letters ⚠️", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.buildBlackLC.setToolTip("These do not exist in Unicode. You will have to make them accessible through OpenType features.")

		self.w.buildBlackCircledNumbers = vanilla.CheckBox("auto", "Black circled numbers 0-20", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.buildBlackCircledNumbers.setToolTip("⓿❶❷❸❹❺❻❼❽❾❿⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴")

		tooltip = "The minimum distance between the figures of multi-figure numbers, in units."
		self.w.minDistanceBetweenFiguresText = vanilla.TextBox("auto", "Distance between figures:", sizeStyle="small", selectable=True)
		self.w.minDistanceBetweenFigures = SteppingEditText("auto", "90", formatter=integerFormatter(0), callback=self.SavePreferences, sizeStyle="small")
		self.w.minDistanceBetweenFiguresText.setToolTip(tooltip)
		self.w.minDistanceBetweenFigures.setToolTip(tooltip)

		self.w.suffixesCheckbox = vanilla.CheckBox("auto", "Include suffixes:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.suffixes = vanilla.EditText("auto", "ss02, ss06", callback=self.SavePreferences, sizeStyle="small")
		tooltip = "Will look if there is a base glyph with a dot suffix, and build the circled glyph with the same suffix. Separate multiple suffixes with a comma. E.g. you have an A and an A.ss06, then you get A.circled and A.circled.ss06, provided you enter ss06 here."
		self.w.suffixesCheckbox.setToolTip(tooltip)
		self.w.suffixes.setToolTip(tooltip)

		self.w.openInNewTab = vanilla.CheckBox("auto", "Open created glyphs in new tab", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.openInNewTab.setToolTip("After building, opens all created circled glyphs in a new Edit tab.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Build", callback=self.BuildCircledGlyphsMain)
		self.w.runButton.setToolTip("Builds the checked circled glyphs in the frontmost font.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[buildUC]-(>=inset)-|",
				"H:|-inset-[buildLC]-(>=inset)-|",
				"H:|-inset-[buildCircledNumbers]-(>=inset)-|",
				"H:|-inset-[buildBlackUC]-(>=inset)-|",
				"H:|-inset-[buildBlackLC]-(>=inset)-|",
				"H:|-inset-[buildBlackCircledNumbers]-(>=inset)-|",
				"H:|-inset-[minDistanceBetweenFiguresText]-gap-[minDistanceBetweenFigures(50)]-(>=inset)-|",
				"H:|-inset-[suffixesCheckbox]-gap-[suffixes(>=80)]-inset-|",
				"H:|-inset-[openInNewTab]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[buildUC]-checkRow-[buildLC]-checkRow-[buildCircledNumbers]-checkRow-[buildBlackUC]-checkRow-[buildBlackLC]-checkRow-[buildBlackCircledNumbers]-row-[minDistanceBetweenFigures]-row-[suffixes]-row-[openInNewTab]-inset-[runButton]-inset-|",
				{"view1": self.w.minDistanceBetweenFiguresText, "attribute1": "centerY", "view2": self.w.minDistanceBetweenFigures, "attribute2": "centerY"},
				{"view1": self.w.suffixesCheckbox, "attribute1": "centerY", "view2": self.w.suffixes, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# Resizable in width only. Vanilla's minSize/maxSize would count the title bar twice,
		# so set the limits on the NSWindow, in content sizes, with the height Auto Layout asks for:
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		contentHeight = nsWindow.contentView().fittingSize().height
		nsWindow.setContentMinSize_(NSSize(windowWidth, contentHeight))
		nsWindow.setContentMaxSize_(NSSize(windowWidth + windowWidthResize, contentHeight))

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

			thisFont = Glyphs.font  # frontmost font

			buildUC = self.pref("buildUC")
			buildLC = self.pref("buildLC")
			buildCircledNumbers = self.pref("buildCircledNumbers")
			buildBlackUC = self.pref("buildBlackUC")
			buildBlackLC = self.pref("buildBlackLC")
			buildBlackCircledNumbers = self.pref("buildBlackCircledNumbers")
			minDistanceBetweenFigures = self.prefInt("minDistanceBetweenFigures")
			shouldIncludeSuffixes = self.pref("suffixesCheckbox")
			suffixes = self.pref("suffixes")
			openInNewTab = self.prefBool("openInNewTab")
			if shouldIncludeSuffixes:
				suffixes = [("." + x.strip()).replace("..", ".") for x in suffixes.split(",") if x.strip()]
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
				return
			if not circledGlyphNames:
				Message(title="Nothing to Build", message="Please tick at least one kind of circled glyphs.", OKButton=None)
				return

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
				blackCircleName = "_part.blackCircle"
				if not thisFont.glyphs[circleName]:
					if not buildCirclePart(thisFont, circleName):
						return
				circleGlyph = thisFont.glyphs[circleName]

				if buildBlackUC or buildBlackLC or buildBlackCircledNumbers:
					if not thisFont.glyphs[blackCircleName]:
						buildCirclePart(thisFont, blackCircleName, isBlack=True)

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
				builtGlyphNames = []
				for glyphName in circledGlyphNames:
					glyphCircleName = blackCircleName if "black" in glyphName.lower() else circleName

					# check for suffixes:
					coreName = glyphName[:glyphName.find(".")]
					glyphNames = [glyphName]
					suffixDict = {}
					if suffixes:
						for suffix in suffixes:
							if "_" in coreName:
								# ligature-like name: one suffixed particle is enough
								hasSuffixedBase = any(thisFont.glyphs[particle + suffix] for particle in coreName.split("_"))
							else:
								hasSuffixedBase = bool(thisFont.glyphs[coreName + suffix])
							if hasSuffixedBase:
								newGlyphName = glyphName + suffix
								glyphNames.append(newGlyphName)
								suffixDict[newGlyphName] = suffix

					for glyphName in glyphNames:
						thisGlyph = thisFont.glyphs[glyphName]

						# generate it if it does not exist
						if not thisGlyph:
							thisGlyph = GSGlyph()
							thisGlyph.name = glyphName
							thisFont.glyphs.append(thisGlyph)
							thisGlyph.updateGlyphInfo()

						suffix = suffixDict.get(glyphName)

						# thisGlyph.beginUndo()  # undo grouping causes crashes
						print("Building %s" % thisGlyph.name)
						buildCircledGlyph(thisGlyph, glyphCircleName, scaleFactors, minDistanceBetweenFigures, suffix)
						builtGlyphNames.append(thisGlyph.name)
						# thisGlyph.endUndo()  # undo grouping causes crashes

			finally:  # errors are reported by the outer except
				thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

			if openInNewTab and builtGlyphNames:
				newTab = thisFont.newTab()
				newTab.text = "/" + "/".join(builtGlyphNames)

			self.w.close()  # delete if you want window to stay open

			# Final report:
			Glyphs.showNotification(
				f"{thisFont.familyName}: Done",
				"Build Circled Glyphs is finished. Details in Macro Window.",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Build Circled Glyphs Error: %s" % e)
			import traceback
			print(traceback.format_exc())


BuildCircledGlyphs()
