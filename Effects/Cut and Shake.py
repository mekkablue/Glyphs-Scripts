#MenuTitle: Cut and Shake
# -*- coding: utf-8 -*-
"""Cuts selected glyphs into pieces and shakes them around a bit."""

numberOfCuts = 20
maxMove = 20.0
maxRotate = 8.0
goodMeasure = 5.0

import GlyphsApp
import random
import math
random.seed()

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers

def rotationTransform( angle=180.0, x_orig=0.0, y_orig=0.0 ):
	"""Returns a TransformStruct for rotating."""
	RotationTransform = NSAffineTransform.transform()
	RotationTransform.translateXBy_yBy_( x_orig, y_orig )
	RotationTransform.rotateByDegrees_( angle )
	RotationTransform.translateXBy_yBy_( -x_orig, -y_orig )
	return RotationTransform

def translateTransform( x_move=0.0, y_move=0.0 ):
	"""Returns a TransformStruct for translating."""
	TranslateTransform = NSAffineTransform.transform()
	TranslateTransform.translateXBy_yBy_( x_move, y_move )
	return TranslateTransform

def somewhereBetween( minimum, maximum ):
	precisionFactor = 100.0
	return random.randint( int( minimum * precisionFactor ), int( maximum * precisionFactor ) ) / precisionFactor

def rotate( x, y, angle=180.0, x_orig=0.0, y_orig=0.0):
	"""Rotates x/y around x_orig/y_orig by angle and returns result as [x,y]."""
	# TO DO: update this to use rotationTransform()
	
	new_angle = ( angle / 180.0 ) * math.pi
	new_x = ( x - x_orig ) * math.cos( new_angle ) - ( y - y_orig ) * math.sin( new_angle ) + x_orig
	new_y = ( x - x_orig ) * math.sin( new_angle ) + ( y - y_orig ) * math.cos( new_angle ) + y_orig
	
	return [ new_x, new_y ]

def rotatePath( thisPath, angle=180.0, x_orig=0.0, y_orig=0.0 ):
	"""Rotates a path around x_orig/y_orig by angle."""
	# TO DO: update this to use rotationTransform()
	
	for thisNode in thisPath.nodes:
		[ thisNode.x, thisNode.y ] = rotate( thisNode.x, thisNode.y, angle=(angle/1.0), x_orig=x_orig, y_orig=y_orig )

def translatePath( thisPath, translateByX=0.0, translateByY=0.0 ):
	"""Translates the path by translateByX/translateByY."""
	
	for thisNode in thisPath.nodes:
		thisNode.x += translateByX
		thisNode.y += translateByY

def randomCutLayer( thisLayer, numberOfCuts ):
	lowestY = thisLayer.bounds.origin.y - goodMeasure
	highestY = thisLayer.bounds.origin.y + thisLayer.bounds.size.height + goodMeasure
	leftmostX = thisLayer.bounds.origin.x - goodMeasure
	rightmostX = thisLayer.bounds.origin.x + thisLayer.bounds.size.width + goodMeasure
	
	for i in range( numberOfCuts ):
		# make either horizontal or vertical cut:
		if random.randint( 0, 1 ) == 0:
			pointL = NSPoint( leftmostX,  somewhereBetween( lowestY, highestY ) )
			pointR = NSPoint( rightmostX, somewhereBetween( lowestY, highestY ) )
			thisLayer.cutBetweenPoints( pointL, pointR )
		else:
			pointB = NSPoint( somewhereBetween( leftmostX, rightmostX ), lowestY  )
			pointT = NSPoint( somewhereBetween( leftmostX, rightmostX ), highestY )
			thisLayer.cutBetweenPoints( pointB, pointT )
	
	return True

def randomMovePaths( thisLayer, maximumMove ):
	for thisPath in thisLayer.paths:
		xMove = somewhereBetween( -maxMove/(2**0.5), maxMove/(2**0.5) )
		yMove = somewhereBetween( -maxMove/(2**0.5), maxMove/(2**0.5) )
		
		translatePath( thisPath, translateByX=xMove, translateByY=yMove )
		#thisPath.transform = translateTransform( x_move=xMove, y_move=yMove )

	return True

def randomRotatePaths( thisLayer, maximumRotate ):
	for thisPath in thisLayer.paths:
		centerX = thisPath.bounds.origin.x + thisPath.bounds.size.width / 2.0
		centerY = thisPath.bounds.origin.y + thisPath.bounds.size.height / 2.0
		pathRotate = somewhereBetween( -maxRotate, maxRotate )
		
		rotatePath( thisPath, angle=pathRotate, x_orig=centerX, y_orig=centerY )
		# thisPath.transform = rotationTransform( angle=pathRotate, x_orig=centerX, y_orig=centerY )
	
	return True

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	
	if randomCutLayer( thisLayer, numberOfCuts ):
		print "-- %i cuts, OK." % numberOfCuts
	if randomMovePaths( thisLayer, maxMove ):
		print "-- moved parts, max: %.1f, OK." % maxMove
	if randomRotatePaths( thisLayer, maxRotate ):
		print "-- rotated parts, max: %.1f degrees, OK." % maxRotate
		
	thisGlyph.endUndo()

Font.enableUpdateInterface()
