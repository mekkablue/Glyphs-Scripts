#MenuTitle: Insert Brace Layers for Movement along Background Path
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Add a single path in the background and it will be used to create intermediate brace layers for OTVar animation.
"""

from Foundation import NSPoint, NSAffineTransform, NSAffineTransformStruct
import math

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs


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

def shiftedLayer( originalLayer, shiftTransform ):
	shiftedLayer = originalLayer.copy()
	shiftedLayer.applyTransform( shiftTransform )
	return shiftedLayer

def bezier( P1,  P2,  P3,  P4,  t ):
	"""
	Returns coordinates for t (=0.0...1.0) on curve segment.
	x1,y1 and x4,y4: coordinates of on-curve nodes
	x2,y2 and x3,y3: coordinates of BCPs
	"""
	
	x1, y1 = P1.x, P1.y
	x2, y2 = P2.x, P2.y
	x3, y3 = P3.x, P3.y
	x4, y4 = P4.x, P4.y
	x = x1*(1-t)**3 + x2*3*t*(1-t)**2 + x3*3*t**2*(1-t) + x4*t**3
	y = y1*(1-t)**3 + y2*3*t*(1-t)**2 + y3*3*t**2*(1-t) + y4*t**3

	return NSPoint(x, y)


def process( thisLayer, steps=5 ):
	thisGlyph = thisLayer.parent
	for i in range(len(thisGlyph.layers))[::-1]:
		thisLayer = thisGlyph.layers[i]
		if thisLayer.layerId != thisLayer.associatedMasterId:
			del thisGlyph.layers[i]
		
	
	shifts = []
	movePath = thisLayer.background.paths[0]
	originPoint = movePath.nodes[0]
	if movePath:
		for thisSegment in movePath.segments:
			print(thisSegment)
			# curve segments:
			if len(thisSegment) == 4:
				for i in range(steps):
					offsetPoint = bezier(
						thisSegment[0].pointValue(),
						thisSegment[1].pointValue(),
						thisSegment[2].pointValue(),
						thisSegment[3].pointValue(),
						i*1.0/steps
					)
					shiftTransform = transform(
						shiftX = offsetPoint.x-originPoint.x,
						shiftY = offsetPoint.y-originPoint.y
					).transformStruct()
					shifts.append( shiftTransform )
			# line segment:
			elif len(thisSegment) == 2:
				P1 = thisSegment[0].pointValue()
				P2 = thisSegment[1].pointValue()
				for i in range(steps):
					shiftTransform = transform(
						shiftX = (P1.x+i*(P2.x-P1.x)/steps)-originPoint.x,
						shiftY = (P1.y+i*(P2.y-P1.y)/steps)-originPoint.y
					).transformStruct()
					shifts.append( shiftTransform )
		
		# all segments are collected in 'shifts':
		print(shifts)
		firstMaster = thisLayer.parent.parent.masters[0]
		secondMaster = thisLayer.parent.parent.masters[1]
		firstMasterValue = firstMaster.weightValue
		secondMasterValue = secondMaster.weightValue
		frameCount = len(shifts)
		stepWidth = (secondMasterValue-firstMasterValue)/frameCount
		
		for i in range(len(shifts)):
			frameTransform = shifts[i]
			frameValue = firstMasterValue + i * stepWidth
			braceLayer = shiftedLayer( thisLayer, frameTransform )
			braceLayer.name = "{%i}" % frameValue
			thisLayer.parent.layers.append( braceLayer )
			

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print("Processing %s" % thisGlyph.name)
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
