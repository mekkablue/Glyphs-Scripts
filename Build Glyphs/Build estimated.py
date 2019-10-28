#MenuTitle: Build estimated, bar, brokenbar
# -*- coding: utf-8 -*-
__doc__="""
Creates an estimated glyph and draws an estimated sign in it. Does the same for bar and brokenbar, for which it respects standard stems and italic angle. Does not overwrite existing glyphs.
"""

# TODO: emptyset, currency, lozenge, product, summation, radical

from Foundation import NSPoint
import math

thisFont = Glyphs.font # frontmost font

def italicize( coords, italicAngle=0.0, pivotalY=0.0 ):
	"""
	Returns the italicized position of an NSPoint 'thisPoint'
	for a given angle 'italicAngle' and the pivotal height 'pivotalY',
	around which the italic slanting is executed, usually half x-height.
	Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
	"""
	x = coords[0]
	y = coords[1]
	yOffset = y - pivotalY # calculate vertical offset
	italicAngle = math.radians( italicAngle ) # convert to radians
	tangens = math.tan( italicAngle ) # math.tan needs radians
	horizontalDeviance = tangens * yOffset # vertical distance from pivotal point
	x += horizontalDeviance # x of point that is yOffset from pivotal point
	return ( x, y )

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

def createGlyph(font, name, unicodeValue):
	if not font.glyphs[name]:
		newGlyph = GSGlyph()
		newGlyph.name = name
		newGlyph.unicode = unicodeValue
		font.glyphs.append(newGlyph)
		return newGlyph
	else:
		return None

def buildEstimated( thisFont ):
	glyphname = "estimated"
	estimatedGlyph = createGlyph(thisFont, glyphname, "212E")
	
	penpoints_estimated = (
		( (416.0,-5.0), ((557.0,-5.0), (635.0,33.0), (724.0,131.0)), (654.0,131.0), ((600.0,70.0), (511.0,22.0), (416.0,22.0)), ((274.0,22.0), (179.0,108.0), (179.0,143.0)), (179.0,311.0), ((179.0,328.0), (185.0,329.0), (194.0,329.0)), (792.0,329.0), ((782.0,557.0), (638.0,682.0), (416.0,682.0)), ((196.0,682.0), (40.0,544.0), (40.0,338.0)), ((40.0,129.0), (196.0,-5.0), (416.0,-5.0)) ),
		( (194.0,350.0), ((183.0,350.0), (179.0,353.0), (179.0,359.0)), (179.0,538.0), ((179.0,568.0), (280.0,658.0), (415.0,658.0)), ((522.0,658.0), (652.0,585.0), (652.0,531.0)), (652.0,366.0), ((652.0,354.0), (650.0,350.0), (636.0,350.0)), (194.0,350.0) )
	)
	
	if estimatedGlyph:
		# find zero:
		zeroGlyph = thisFont.glyphs["zero.lf"]
		if not zeroGlyph:
			zeroGlyph = thisFont.glyphs["zero.tf"]
			if not zeroGlyph:
				zeroGlyph = thisFont.glyphs["zero"]
		
		# draw in every layer:
		for thisLayer in estimatedGlyph.layers:
			for thisPath in penpoints_estimated:
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
						print "%s: Path drawing error. Could not process this segment:\n" % (glyphname, thisSegment)
				pen.closePath()
				pen.endPath()
		
			# scale estimated to match zero:
			if zeroGlyph:
				zeroBounds = zeroGlyph.layers[thisLayer.associatedMasterId].bounds
				zeroHeight = zeroBounds.size.height
				if zeroHeight: # zero could be empty
					zeroOvershoot = -zeroBounds.origin.y
					overshootDiff = zeroOvershoot - 5.0
					estimatedHeight = 687.0
					correctedEstimatedHeight = zeroHeight - 2 * overshootDiff
					if correctedEstimatedHeight != estimatedHeight:
						scaleFactor = correctedEstimatedHeight/estimatedHeight
						estimatedCorrection = transform(shiftY=5.0)
						estimatedCorrection.appendTransform_( transform(scale=scaleFactor) )
						estimatedCorrection.appendTransform_( transform(-5.0) )
						thisLayer.applyTransform( estimatedCorrection.transformStruct() )
		
			# tidy up paths and set width:
			thisLayer.cleanUpPaths()
			thisLayer.LSB = 40.0
			thisLayer.RSB = 40.0
			print "Created estimated in master '%s'" % thisLayer.associatedFontMaster().name
	else:
		print "\nEstimated Error"
		print "The glyph estimated already exists in this font. Rename or delete it and try again."
		Glyphs.showMacroWindow()

def buildBars(thisFont):
	barGlyph = createGlyph(thisFont, "bar", "007C")
	brokenbarGlyph = createGlyph(thisFont, "brokenbar", "00A6")
	
	descender = round(thisFont.masters[0].descender * 1.2)
	ascender = round(thisFont.masters[0].ascender * 1.2)

	if barGlyph or brokenbarGlyph:
		for thisMaster in thisFont.masters:
			mID = thisMaster.id
			italicAngle = thisMaster.italicAngle
			pivot = thisMaster.xHeight * 0.5
			stemWidth = 50.0
			try:
				stemWidth = thisMaster.verticalStems[0] * 0.8
			except:
				Message("Bar Error", "No vertical stems set in Master '%s'. Will default to 50." % (thisMaster.name), OKButton="Continue")

			stemWidth -= stemWidth*math.cos(math.radians(italicAngle))-stemWidth
			sidebearing = max( (350-stemWidth)*0.5, 60.0 )
			gap = max( 250-stemWidth, 120.0 )
			
			bottomLeft = italicize( (sidebearing,descender), italicAngle=italicAngle, pivotalY=pivot )
			bottomRight = italicize( (sidebearing+stemWidth,descender), italicAngle=italicAngle, pivotalY=pivot )
			topRight = italicize( (sidebearing+stemWidth,ascender), italicAngle=italicAngle, pivotalY=pivot )
			topLeft = italicize( (sidebearing,ascender), italicAngle=italicAngle, pivotalY=pivot )

			if barGlyph:
				barLayer = barGlyph.layers[mID]
				pen = barLayer.getPen()
				pen.moveTo( bottomLeft )
				pen.lineTo( bottomRight )
				pen.lineTo( topRight )
				pen.lineTo( topLeft )
				pen.closePath()
				pen.endPath()
				barLayer.RSB = sidebearing
				print "Created bar in master '%s'" % thisMaster.name
			
			if brokenbarGlyph:
				gapBottomY = ((ascender+descender)-gap)*0.5
				gapTopY = ((ascender+descender)+gap)*0.5
				gapBottomRight = italicize( (sidebearing+stemWidth,gapBottomY), italicAngle=italicAngle, pivotalY=pivot )
				gapBottomLeft = italicize( (sidebearing,gapBottomY), italicAngle=italicAngle, pivotalY=pivot )
				gapTopRight = italicize( (sidebearing+stemWidth,gapTopY), italicAngle=italicAngle, pivotalY=pivot )
				gapTopLeft = italicize( (sidebearing,gapTopY), italicAngle=italicAngle, pivotalY=pivot )
				
				brokenbarLayer = brokenbarGlyph.layers[mID]
				pen = brokenbarLayer.getPen()
				pen.moveTo( bottomLeft )
				pen.lineTo( bottomRight )
				pen.lineTo( gapBottomRight )
				pen.lineTo( gapBottomLeft )
				pen.closePath()
				pen.endPath()
				
				brokenbarLayer = brokenbarGlyph.layers[mID]
				pen = brokenbarLayer.getPen()
				pen.moveTo( gapTopLeft )
				pen.lineTo( gapTopRight )
				pen.lineTo( topRight )
				pen.lineTo( topLeft )
				pen.closePath()
				pen.endPath()
				
				brokenbarLayer.RSB = sidebearing
				print "Created brokenbar in master '%s'" % thisMaster.name
	else:
		print "\nBar Error:"
		print "The glyphs bar and brokenbar already exist in this font. Rename or delete them and try again."
		Glyphs.showMacroWindow()

buildEstimated(thisFont)
buildBars(thisFont)