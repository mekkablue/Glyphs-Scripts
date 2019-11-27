#MenuTitle: Build Circled Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Builds circled numbers and letters (U+24B6...24EA and U+2460...2473) from _part.circle and the letters and figures.
"""

from Foundation import NSPoint
import math

minDistanceBetweenFigures = 90.0

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
circledGlyphNames = ["one.circled", "two.circled", "three.circled", "four.circled", "five.circled", "six.circled", "seven.circled", "eight.circled", "nine.circled", "one_zero.circled", "one_one.circled", "one_two.circled", "one_three.circled", "one_four.circled", "one_five.circled", "one_six.circled", "one_seven.circled", "one_eight.circled", "one_nine.circled", "two_zero.circled", "A.circled", "B.circled", "C.circled", "D.circled", "E.circled", "F.circled", "G.circled", "H.circled", "I.circled", "J.circled", "K.circled", "L.circled", "M.circled", "N.circled", "O.circled", "P.circled", "Q.circled", "R.circled", "S.circled", "T.circled", "U.circled", "V.circled", "W.circled", "X.circled", "Y.circled", "Z.circled", "a.circled", "b.circled", "c.circled", "d.circled", "e.circled", "f.circled", "g.circled", "h.circled", "i.circled", "j.circled", "k.circled", "l.circled", "m.circled", "n.circled", "o.circled", "p.circled", "q.circled", "r.circled", "s.circled", "t.circled", "u.circled", "v.circled", "w.circled", "x.circled", "y.circled", "z.circled", "zero.circled"]



def offsetLayer( thisLayer, offset, makeStroke=False, position=0.5, autoStroke=False ):
	offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
	offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_error_shadow_(
		thisLayer,
		offset, offset, # horizontal and vertical offset
		makeStroke,     # if True, creates a stroke
		autoStroke,     # if True, distorts resulting shape to vertical metrics
		position,       # stroke distribution to the left and right, 0.5 = middle
		None, None )

def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct() # returns the 6-float tuple
	Apply the matrix tuple like this:
		Layer.applyTransform(tMatrix)
		Component.applyTransform(tMatrix)
		Path.applyTransform(tMatrix)
	Chain multiple NSAffineTransform objects t1, t2 like this:
		t1.appendTransform_(t2)
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX,shiftY)
	if skew:
		skewStruct = NSAffineTransformStruct()
		skewStruct.m11 = 1.0
		skewStruct.m22 = 1.0
		skewStruct.m21 = math.tan(math.radians(skew))
		skewTransform = NSAffineTransform.transform()
		skewTransform.setTransformStruct_(skewStruct)
		myTransform.appendTransform_(skewTransform)
	return myTransform

def centerOfRect(rect):
	"""
	Returns the center of NSRect rect as an NSPoint.
	"""
	x = rect.origin.x + rect.size.width * 0.5
	y = rect.origin.y + rect.size.height * 0.5
	return NSPoint(x,y)

def combinedBounds(rects):
	bottomLeft = NSPoint( 1000.0, 100.0 )
	topRight = NSPoint( 0.0, 0.0 )
	for thisRect in rects:
		bottomLeft.x = min( thisRect.origin.x, bottomLeft.x )
		bottomLeft.y = min( thisRect.origin.y, bottomLeft.y )
		topRight.x = max( topRight.x, thisRect.origin.x+thisRect.size.width )
		topRight.y = max( topRight.y, thisRect.origin.y+thisRect.size.height )
	combinedRect = NSRect()
	combinedRect.origin = bottomLeft
	combinedRect.size = NSSize( topRight.x-bottomLeft.x, topRight.y-bottomLeft.y )
	return combinedRect

def measureLayerAtHeightFromLeftOrRight( thisLayer, height, leftSide=True ):
	leftX = thisLayer.bounds.origin.x
	rightX = leftX + thisLayer.bounds.size.width
	y = height
	returnIndex = 1
	if not leftSide:
		returnIndex = -2
	measurement = thisLayer.intersectionsBetweenPoints( NSPoint(leftX,y), NSPoint(rightX,y) )[returnIndex].pointValue().x
	if leftSide:
		distance = measurement - leftX
	else:
		distance = rightX - measurement
	return distance

def minDistanceBetweenTwoLayers( comp1, comp2, interval=5.0 ):
	topY = min( comp1.bounds.origin.y+comp1.bounds.size.height, comp2.bounds.origin.y+comp2.bounds.size.height )
	bottomY = max( comp1.bounds.origin.y, comp2.bounds.origin.y )
	distance = topY - bottomY
	minDist = None
	for i in range(int(distance/interval)):
		height = bottomY + i * interval
		left = measureLayerAtHeightFromLeftOrRight( comp1, height, leftSide=False )
		right = measureLayerAtHeightFromLeftOrRight( comp2, height, leftSide=True )
		total = left+right
		if minDist == None or minDist > total:
			minDist = total
	return minDist

def placeComponentsAtDistance( thisLayer, comp1, comp2, interval=5.0, distance=10.0 ):
	thisMaster = thisLayer.associatedFontMaster()
	masterID = thisMaster.id
	original1 = comp1.component.layers[masterID]
	original2 = comp2.component.layers[masterID]
	minDist = minDistanceBetweenTwoLayers( original1, original2, interval=interval )
	comp2shift = distance - minDist
	addedSBs = original1.RSB + original2.LSB
	comp2.x = comp1.x + original1.width - addedSBs + comp2shift

def process( thisLayer, compName1, compName2, distance=10.0, interval=5.0 ):
	if compName1 and compName2:
		compCount = len(thisLayer.components)
		for compName in (compName1,compName2):
			newComp = GSComponent(compName)
			thisLayer.components.append(newComp)
			newComp.disableAlignment = True
		placeComponentsAtDistance( thisLayer, thisLayer.components[compCount], thisLayer.components[compCount+1] )
	else:
		return False


def buildCircledGlyph( thisGlyph, circleName, scaleFactors ):
	thisFont = thisGlyph.font()
	thisGlyph.setWidthMetricsKey_( "=%i" % thisFont.upm )
	circleGlyph = thisFont.glyphs[circleName]
	
	for i, thisMaster in enumerate(thisFont.masters):
		figureHeight = None
		scaleFactor = scaleFactors[i]
		thisLayer = thisGlyph.layers[thisMaster.id]
		circleLayer = circleGlyph.layers[thisMaster.id]
		circleScaleFactor = thisFont.upm * 0.9 / ( circleLayer.bounds.size.width )
		thisLayer.clear()
		thisLayer.syncMetrics()
		
		# add circle:
		assumedCenter = NSPoint( thisFont.upm*0.5, thisFont.upm*0.3 ) # hardcoded
		circleComponent = GSComponent(circleName)
		thisLayer.components.append(circleComponent)
		
		# scale circle:
		circleScale = transform( scale=circleScaleFactor ).transformStruct()
		circleComponent.applyTransform( circleScale )
		
		# move circle:
		circleBounds = thisLayer.components[0].bounds
		circleCenter = centerOfRect(circleBounds)
		xShift = assumedCenter.x - circleCenter.x
		yShift = assumedCenter.y - circleCenter.y
		circleShift = transform( shiftX=xShift, shiftY=yShift ).transformStruct()
		circleComponent.applyTransform(circleShift)
		
		# find components to add
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
				if thisFont.glyphs[lfName]:
					compName = lfName
				elif thisFont.glyphs[osfName]:
					compName = osfName
				
				innerComponent = GSComponent( compName )
				thisLayer.components.append( innerComponent )
				innerComponent.position = NSPoint( advance, 0.0 )
				
				if j > 0:
					innerComponent.disableAlignment = True
					placeComponentsAtDistance( 
						thisLayer,
						thisLayer.components[-2], 
						thisLayer.components[-1], # same as innerComponent
						distance = minDistanceBetweenFigures
					)
				
				originalLayerWidth = thisFont.glyphs[compName].layers[thisMaster.id].width
				advance += originalLayerWidth
			
			collectedBounds = [ c.bounds for c in thisLayer.components[1:] ]
			compCenter = centerOfRect( combinedBounds(collectedBounds) )
			circleCenter = centerOfRect( circleComponent.bounds )
		
			# scale and move it in place:
			shift = transform( shiftX=-compCenter.x, shiftY=-compCenter.y ).transformStruct()
			scaleToFit = transform( scale=scaleFactor*circleScaleFactor ).transformStruct()
			backshift = transform( shiftX=circleCenter.x, shiftY=circleCenter.y ).transformStruct()
			
			compensateStroke = []
			for innerComponent in thisLayer.components[1:]:
				
				# optically shift so top anchor is in center:
				originalLayer = topAnchor = innerComponent.component.layers[thisMaster.id]
				topAnchor = originalLayer.anchors["top"]
				if topAnchor:
					anchorCenter = topAnchor.x
					boundsCenter = centerOfRect(originalLayer.bounds).x
					opticalCorrection = boundsCenter-anchorCenter
					if opticalCorrection != 0.0:
						threshold = 35.0
						if abs(opticalCorrection) > threshold:
							posNeg = opticalCorrection/abs(opticalCorrection)
							rest = abs(opticalCorrection) - threshold
							opticalCorrection = posNeg * ( threshold + rest * 1/rest**0.3 )
							print("--", opticalCorrection)
						opticalShift = transform( shiftX = opticalCorrection ).transformStruct()
						innerComponent.applyTransform( opticalShift )
					
				
				innerComponent.applyTransform( shift )
				innerComponent.applyTransform( scaleToFit )
				innerComponent.applyTransform( backshift )
				
				# move components closer to center:
				#move = 15.0
				#hOffset = circleCenter.x - centerOfRect(innerComponent.bounds).x
				#if abs(hOffset) > move:
				#	hOffset = (hOffset/abs(hOffset))*move
				#if hOffset != 0.0:
				#	moveCloser = transform( shiftX=hOffset ).transformStruct()
				#	innerComponent.applyTransform( moveCloser )
				
				# compensatory shift:
				if thisGlyph.name in ("two_zero.circled", "one_nine.circled", "one_zero.circled"):
					compensate = transform( shiftX=10.0 ).transformStruct()
					innerComponent.applyTransform( compensate )
					
				
				
				if innerComponent.component.glyphInfo.category == "Number":
					if figureHeight == None:
						figureHeight = innerComponent.position.y
					else:
						innerComponent.position.y = figureHeight
						
				compensateStroke.append(innerComponent)
				
			# auffetten:
			isNumber = False
			for i in range(len(compensateStroke))[::-1]:
				componentToDecompose = compensateStroke[i]
				if componentToDecompose.component.category == "Number":
					isNumber = True
				thisLayer.decomposeComponent_(componentToDecompose)
				
			offsetLayer( thisLayer, 4.0 ) #4.0 if isNumber else 3.0 )
			thisLayer.anchors = None
			
			
			


def buildCirclePart( thisFont, glyphName ):
	partCircle = (
		(
			(353.0, 0.0),
			((152.0, 0.0),(0.0, 150.0),(0.0, 348.0)),
			((0.0, 549.0),(152.0, 700.0),(353.0, 700.0)),
			((556.0, 700.0),(708.0, 549.0),(708.0, 348.0)),
			((708.0, 149.0),(556.0, 0.0),(353.0, 0.0))
		),
	)
	
	thisGlyph = thisFont.glyphs[glyphName]
	if not thisGlyph:
		thisGlyph = GSGlyph()
		thisGlyph.name = glyphName
		thisFont.glyphs.append( thisGlyph )
		print("Generated %s" % glyphName)
	
	thisGlyph.export = False
	
	# find zero for reference:
	zeroGlyph = thisFont.glyphs["zero.lf"]
	if not zeroGlyph:
		zeroGlyph = thisFont.glyphs["zero.tf"]
		if not zeroGlyph:
			zeroGlyph = thisFont.glyphs["zero"]
	
	# draw in every layer:
	for thisLayer in thisGlyph.layers:
		# make sure it is empty:
		thisLayer.clear()
		
		# draw outer circle:
		for thisPath in partCircle:
			pen = thisLayer.getPen()
			pen.moveTo( thisPath[0] )
			for thisSegment in thisPath[1:]:
				if len(thisSegment) == 2: # lineto
					pen.lineTo( thisSegment )
				elif len(thisSegment) == 3: # curveto
					pen.curveTo(
						thisSegment[0],
						thisSegment[1],
						thisSegment[2]
					)
				else:
					print("%s: Path drawing error. Could not process this segment:\n" % (glyphName, thisSegment))
			pen.closePath()
			pen.endPath()
	
		# scale circle to match zero:
		if zeroGlyph:
			zeroBounds = zeroGlyph.layers[thisLayer.associatedMasterId].bounds
			zeroHeight = zeroBounds.size.height
			if zeroHeight: # zero could be empty
				zeroOvershoot = -zeroBounds.origin.y
				overshootDiff = zeroOvershoot - 5.0
				actualHeight = thisLayer.bounds.size.height
				correctedHeight = zeroHeight - 2 * overshootDiff
				if correctedHeight != actualHeight:
					scaleFactor = correctedHeight/actualHeight
					correction = transform(shiftY=5.0)
					correction.appendTransform_( transform(scale=scaleFactor) )
					correction.appendTransform_( transform(-5.0) )
					thisLayer.applyTransform( correction.transformStruct() )

		# inner circle, scaled down:
		currentHeight = thisLayer.bounds.size.height
		outerCircle = thisLayer.paths[0]
		innerCircle = outerCircle.copy()
		thisLayer.paths.append(innerCircle)
		
		# scale down inner circle:
		stemSize = 50.0
		hstems = thisLayer.associatedFontMaster().horizontalStems
		vstems = thisLayer.associatedFontMaster().verticalStems
		if hstems and vstems:
			stemSize = (hstems[0] + vstems[0]) * 0.25
		
		maximumStemSize = currentHeight * 0.28
		stemSize = min(maximumStemSize,stemSize)
		smallerBy = stemSize * 2 * 1.06
		newHeight = currentHeight - smallerBy
		scaleFactor = newHeight/currentHeight
		scale = transform(scale=scaleFactor).transformStruct()
		
		centerX = innerCircle.bounds.origin.x + innerCircle.bounds.size.width * 0.5
		centerY = innerCircle.bounds.origin.y + innerCircle.bounds.size.height * 0.5
		shift = transform(shiftX=-centerX, shiftY=-centerY).transformStruct()
		shiftBack = transform(shiftX=centerX, shiftY=centerY).transformStruct()
		
		innerCircle.applyTransform( shift )
		innerCircle.applyTransform( scale )
		innerCircle.applyTransform( shiftBack )

		# tidy up paths and set width:
		thisLayer.correctPathDirection()
		thisLayer.cleanUpPaths()
		thisLayer.LSB = 40.0
		thisLayer.RSB = 40.0
		
		# add anchor:
		centerX = thisLayer.bounds.origin.x + thisLayer.bounds.size.width * 0.5
		centerY = thisLayer.bounds.origin.y + thisLayer.bounds.size.height * 0.5
		centerAnchor = GSAnchor()
		centerAnchor.name = "#center"
		centerAnchor.position = NSPoint( centerX, centerY )
		thisLayer.anchors.append(centerAnchor)

def boxArea(thisLayer):
	return thisLayer.bounds.size.width * thisLayer.bounds.size.height

thisFont.disableUpdateInterface() # suppresses UI updates in Font View


# add circle if not present in font already:
circleName = "_part.circle"
if not thisFont.glyphs[circleName]:
	buildCirclePart( thisFont, circleName )
circleGlyph = thisFont.glyphs[circleName]

# determining scale of inscribed letters:
scaleFactors = []
for thisMaster in thisFont.masters:
	radius = circleGlyph.layers[thisMaster.id].paths[1].bounds.size.width * 0.5
	maxArea = 0.0
	biggestLayer = None
	for glyphName in circledGlyphNames:
		if "." in glyphName:
			glyphName = glyphName[:glyphName.find(".")]
		thisGlyph = thisFont.glyphs[glyphName]
		if thisGlyph:
			thisLayer = thisGlyph.layers[thisMaster.id]
			thisArea = boxArea(thisLayer)
			if thisArea > maxArea:
				maxArea = thisArea
				biggestLayer = thisLayer
	
	angleInRadians = math.atan2( biggestLayer.bounds.size.height, biggestLayer.bounds.size.width )
	scaledHeight = math.sin(angleInRadians) * radius * 2 * 0.9
	scaleFactor = scaledHeight / biggestLayer.bounds.size.height
	scaleFactors.append(scaleFactor)
	

for glyphName in circledGlyphNames:
	thisGlyph = thisFont.glyphs[glyphName]
	if not thisGlyph:
		thisGlyph = GSGlyph()
		thisGlyph.name = glyphName
		thisFont.glyphs.append(thisGlyph)

	thisGlyph.beginUndo() # begin undo grouping
	print("Building %s" % thisGlyph.name)
	buildCircledGlyph( thisGlyph, circleName, scaleFactors )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
