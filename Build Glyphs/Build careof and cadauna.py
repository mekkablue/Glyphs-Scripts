#MenuTitle: Build cadauna and careof
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Builds cadauna and careof from your c, u and fraction glyphs.
"""

from Foundation import NSPoint, NSAffineTransform
import math

distanceBetweenComponents = 80

thisFont = Glyphs.font # frontmost font
newGlyphs = {
	"cadauna": ("c","u"),
	"careof": ("c","o")
}

		
def measureLayerAtHeightFromLeftOrRight( thisLayer, height, leftSide=True, transformStruct=None ):
	thisLayer = thisLayer.copyDecomposedLayer()
	if transformStruct != None:
		thisLayer.applyTransform(transformStruct)
	try:
		leftX = thisLayer.bounds.origin.x
		rightX = leftX + thisLayer.bounds.size.width
		y = height
		returnIndex = 1
		if not leftSide:
			returnIndex = -2
		measurements = thisLayer.intersectionsBetweenPoints( NSPoint(leftX,y), NSPoint(rightX,y) )
		if len(measurements) > 2:
			measurement = measurements[returnIndex].pointValue().x
			if leftSide:
				distance = measurement - leftX
			else:
				distance = rightX - measurement
			return distance
		else:
			return None
	except:
		return None

def minDistanceBetweenTwoLayers( comp1, comp2, interval=5.0, transformStruct1=None, transformStruct2=None ):
	if transformStruct1:
		comp1 = comp1.copyDecomposedLayer()
		comp1.applyTransform(transformStruct1)
	if transformStruct2:
		comp2 = comp2.copyDecomposedLayer()
		comp2.applyTransform(transformStruct2)
	topY = min( comp1.bounds.origin.y+comp1.bounds.size.height, comp2.bounds.origin.y+comp2.bounds.size.height )
	bottomY = max( comp1.bounds.origin.y, comp2.bounds.origin.y )
	distance = topY - bottomY
	minDist = None
	for i in range(int(distance/interval)):
		height = bottomY + i * interval
		left = measureLayerAtHeightFromLeftOrRight( comp1, height, leftSide=False, transformStruct=None )
		right = measureLayerAtHeightFromLeftOrRight( comp2, height, leftSide=True, transformStruct=None )
		try: # avoid gaps like in i or j
			total = left+right
			if minDist == None or minDist > total:
				minDist = total
		except:
			pass
	return minDist

def placeComponentsAtDistance( thisLayer, comp1, comp2, interval=5.0, distance=10.0 ):
	thisMaster = thisLayer.associatedFontMaster()
	masterID = thisMaster.id
	original1 = comp1.component.layers[masterID]
	original2 = comp2.component.layers[masterID]
	minDist = minDistanceBetweenTwoLayers( original1, original2, interval=interval, transformStruct1=comp1.transformStruct(), transformStruct2=comp2.transformStruct() )
	if minDist != None:
		comp2shift = distance - minDist
		addedSBs = original1.RSB + original2.LSB
		comp2.x = comp1.bounds.origin.x + comp1.bounds.size.width + comp2shift - (comp2.bounds.origin.x-comp2.x)
		#comp1.x + original1.width - addedSBs + comp2shift

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

def unsuffixed(name):
	if "." in name:
		return name[:name.find(".")]
	else:
		return name

def getGlyphWithName(glyphName, thisFont):
	thisGlyph = thisFont.glyphs[glyphName]
	if thisGlyph:
		return thisGlyph
	else:
		newGlyph = GSGlyph(glyphName)
		thisFont.glyphs.append(newGlyph)
		newGlyph.updateGlyphInfo()
		return newGlyph

def getZeroGlyph(thisFont):
	# find zero:
	zeroGlyph = thisFont.glyphs["zero.dnom"]
	if not zeroGlyph:
		zeroGlyph = thisFont.glyphs["zero.subs"]
	return zeroGlyph

def process( thisGlyph ):
	parts = ["parenleft"] + unsuffixed(thisGlyph.name).split("_") + ["parenright"]
	maxWidth = thisFont.upm
	thisGlyph.leftMetricsKey = None
	thisGlyph.rightMetricsKey = None
	print("-".join(parts))
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
			try:
				thisLayer.shapes.append(comp)
			except:
				thisLayer.components.append(comp)
			if i>0:
				placeComponentsAtDistance( 
					thisLayer,
					thisLayer.components[i-1],
					comp,
					distance=distanceBetweenComponents )
			
		#thisLayer.decomposeComponents()
		maxWidth = max(thisLayer.bounds.size.width*0.97, maxWidth)
	return maxWidth
		
def postprocess( thisGlyph, scale, shiftUp ):
	for thisLayer in thisGlyph.layers:
		#thisLayer.decomposeComponents()
		#for thisComp in thisLayer.components:
		#	thisComp.makeDisableAlignment()
		scaleDown = transform(scale=scale).transformStruct()
		thisLayer.applyTransform( scaleDown )
		thisLayer.applyTransform( shiftUp )
		lsb = (thisFont.upm - thisLayer.bounds.size.width) // 2.0
		thisLayer.LSB = lsb
		thisLayer.width = thisFont.upm
		
		if thisLayer.components[1].component.category == "Letter":
			thisLayer.components[0].x -= parenShiftForLetters
			thisLayer.components[2].x += parenShiftForLetters

try:
	thisFont.disableUpdateInterface() # suppresses UI updates in Font View

	for newGlyph in newGlyphs:
		thisGlyph = getGlyphWithName(newGlyph,thisFont)
		for thisLayer in thisGlyph.layers:
			thisLayer.clear()
		firstComp = newGlyphs[newGlyph][0]
		lastComp = newGlyphs[newGlyph][1]
		for i,compName in enumerate( (firstComp,"fraction",lastComp) ):
			for thisMaster in thisFont.masters:
				thisLayer = thisGlyph.layers[thisMaster.id]
				newComponent = GSComponent(compName)
				try:
					thisLayer.shapes.append( newComponent )
				except:
					thisLayer.components.append( newComponent )
				newComponent.disableAlignment = True
			
				if i in (0,2):
					zero = getZeroGlyph(thisFont).layers[thisMaster.id]
					scale = zero.bounds.size.height / newComponent.bounds.size.height
					zoomTransform = transform(scale=scale).transformStruct()
					newComponent.applyTransform(zoomTransform)
				if i == 0:
					zero = thisFont.glyphs["zero.numr"].layers[thisMaster.id]
					zeroTop = zero.bounds.origin.y + zero.bounds.size.height
					compTop = newComponent.bounds.origin.y + newComponent.bounds.size.height
					shiftUp = transform( shiftY=(zeroTop-compTop) ).transformStruct()
					newComponent.applyTransform(shiftUp)
				if i > 0:
					try:
						previousComponent = thisLayer.shapes[i-1]
					except:
						previousComponent = thisLayer.components[i-1]
					placeComponentsAtDistance( 
						thisLayer,
						previousComponent,
						newComponent,
						interval=3.0,
						distance=distanceBetweenComponents 
						)
				
				if i == 2:
					try:
						thisLayer.LSB = thisLayer.shapes[0].component.layers[thisMaster.id].LSB
						thisLayer.RSB = thisLayer.shapes[2].component.layers[thisMaster.id].RSB
					except:
						thisLayer.LSB = thisLayer.components[0].component.layers[thisMaster.id].LSB
						thisLayer.RSB = thisLayer.components[2].component.layers[thisMaster.id].RSB
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	print(e)
	print()
	import traceback
	print(traceback.format_exc())
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
