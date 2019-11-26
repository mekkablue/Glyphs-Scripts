from __future__ import print_function
#MenuTitle: Build .notdef
# -*- coding: utf-8 -*-
__doc__="""
Creates a .notdef from your boldest available question mark.
"""

from GlyphsApp import GSOFFCURVE, GSCURVE, GSSMOOTH
from Foundation import NSPoint, NSRect, NSSize, NSAffineTransform, NSAffineTransformStruct

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def scaleLayerByFactor( thisLayer, scaleFactor ):
	"""
	Scales a layer by this factor.
	"""
	thisLayer.transform_checkForSelection_doComponents_(
		scaleMatrix(scaleFactor), False, True
	)

def scaleMatrix(scaleFactor):
	"""
	Returns a matrix for the scale factor,
	where 100% is represented as 1.0.
	"""
	scaleMatrix = ( scaleFactor, 0.0, 0.0, scaleFactor, 0.0, 0.0 )
	transformMatrix = transformFromMatrix( scaleMatrix )
	return transformMatrix

def transformFromMatrix( matrix ):
	"""
	Returns an NSAffineTransform based on the matrix supplied.
	Matrix needs to be a tuple of 6 floats.
	"""
	transformation = NSAffineTransform.transform()
	transformation.setTransformStruct_( matrix )
	return transformation

def circleInsideRect(rect):
	"""Returns a GSPath for a circle inscribed into the NSRect rect."""
	MAGICNUMBER = 4.0 * ( 2.0**0.5 - 1.0 ) / 3.0
	x = rect.origin.x
	y = rect.origin.y
	height = rect.size.height
	width = rect.size.width
	fullHeight = y+height
	fullWidth = x+width
	halfHeight = y + 0.5 * height
	halfWidth = x + 0.5 * width
	horHandle = width * 0.5 * MAGICNUMBER * 1.05
	verHandle = height * 0.5 * MAGICNUMBER * 1.05
	
	segments = (
		( NSPoint(x,halfHeight-verHandle), NSPoint(halfWidth-horHandle,y), NSPoint(halfWidth,y) ),
		( NSPoint(halfWidth+horHandle,y), NSPoint(fullWidth,halfHeight-verHandle), NSPoint(fullWidth,halfHeight) ),
		( NSPoint(fullWidth,halfHeight+verHandle), NSPoint(halfWidth+horHandle,fullHeight), NSPoint(halfWidth,fullHeight) ),
		( NSPoint(halfWidth-horHandle,fullHeight), NSPoint(x,halfHeight+verHandle), NSPoint(x,halfHeight) )
	)
	
	circlePath = GSPath()
	
	for thisSegment in segments:
		for i in range(3):
			nodeType = (GSOFFCURVE, GSOFFCURVE, GSCURVE)[i]
			nodePos = thisSegment[i]
			newNode = GSNode()
			newNode.position = nodePos
			newNode.type = nodeType
			newNode.connection = GSSMOOTH
			circlePath.nodes.append(newNode)

	print(circlePath)
	for n in circlePath.nodes:
		print("   ", n)
	circlePath.closed = True
	return circlePath

if not thisFont.glyphs[".notdef"]:
	if thisFont.glyphs["question"]:
		sourceMasterID = thisFont.masters[len(thisFont.masters)-1].id
		sourceLayer = thisFont.glyphs["question"].layers[sourceMasterID]
		if sourceLayer:
			# Build .notdef from question mark and circle:
			questionmarkLayer = sourceLayer.copyDecomposedLayer()
			scaleLayerByFactor( questionmarkLayer, 0.8 )
			qOrigin = questionmarkLayer.bounds.origin
			qWidth = questionmarkLayer.bounds.size.width
			qHeight = questionmarkLayer.bounds.size.height
			qCenter = NSPoint( qOrigin.x+0.5*qWidth, qOrigin.y+0.5*qHeight )
			side = max((qWidth,qHeight)) * 1.5
			circleRect = NSRect( 
				NSPoint(qCenter.x-0.5*side, qCenter.y-0.5*side),
				NSSize(side,side)
			)
			circle = circleInsideRect(circleRect)
			questionmarkLayer.paths.append(circle)
			questionmarkLayer.correctPathDirection()
			
			# Create glyph:
			notdefName = ".notdef"
			notdefGlyph = GSGlyph()
			notdefGlyph.name = notdefName
			thisFont.glyphs.append( notdefGlyph )
			if thisFont.glyphs[notdefName]:
				print("%s added successfully" % notdefName)
				print(thisFont.glyphs[notdefName])
				print(len(thisFont.glyphs[notdefName].layers))
			for masterID in [m.id for m in thisFont.masters]:
				notdefLayer = thisFont.glyphs[notdefName].layers[masterID]
				print(notdefLayer)
				for thisPath in questionmarkLayer.paths:
					print() 
					notdefLayer.paths.append( thisPath.copy() )
				notdefLayer.LSB = 30.0
				notdefLayer.RSB = 30.0
		else:
			Message("Notdef Error", "Could not determine source layer of glyph 'question'.", OKButton="Damn")
	else:
		Message("Notdef Error", "No question mark is available in your font. Cannot create .notdef.", OKButton="Shucks")
else:
	Message("Notdef Error", "There already is a .notdef in your font. Delete it and run the script again if you want to replace it.", OKButton="Too bad.")

