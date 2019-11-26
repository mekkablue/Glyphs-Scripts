#MenuTitle: Build Parenthesized Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Creates parenthesized letters and numbers: one.paren, two.paren, three.paren, four.paren, five.paren, six.paren, seven.paren, eight.paren, nine.paren, one_zero.paren, one_one.paren, one_two.paren, one_three.paren, one_four.paren, one_five.paren, one_six.paren, one_seven.paren, one_eight.paren, one_nine.paren, two_zero.paren, a.paren, b.paren, c.paren, d.paren, e.paren, f.paren, g.paren, h.paren, i.paren, j.paren, k.paren, l.paren, m.paren, n.paren, o.paren, p.paren, q.paren, r.paren, s.paren, t.paren, u.paren, v.paren, w.paren, x.paren, y.paren, z.paren.
"""

import math
from Foundation import NSPoint

distanceBetweenComponents = 95.0
parenShiftForLetters = 40.0

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
parenGlyphs = [
	"one.paren", "two.paren", "three.paren", "four.paren", "five.paren", "six.paren", "seven.paren", "eight.paren", "nine.paren", 
	"one_zero.paren", "one_one.paren", "one_two.paren", "one_three.paren", "one_four.paren", "one_five.paren", "one_six.paren", "one_seven.paren", "one_eight.paren", "one_nine.paren", "two_zero.paren", 
	"a.paren", "b.paren", "c.paren", "d.paren", "e.paren", "f.paren", "g.paren", "h.paren", "i.paren", "j.paren", "k.paren", "l.paren", "m.paren", "n.paren", "o.paren", "p.paren", "q.paren", "r.paren", "s.paren", "t.paren", "u.paren", "v.paren", "w.paren", "x.paren", "y.paren", "z.paren" 
]

def measureLayerAtHeightFromLeftOrRight( thisLayer, height, leftSide=True ):
	thisLayer = thisLayer.copyDecomposedLayer()
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

def minDistanceBetweenTwoLayers( comp1, comp2, interval=5.0 ):
	topY = min( comp1.bounds.origin.y+comp1.bounds.size.height, comp2.bounds.origin.y+comp2.bounds.size.height )
	bottomY = max( comp1.bounds.origin.y, comp2.bounds.origin.y )
	distance = topY - bottomY
	minDist = None
	for i in range(int(distance/interval)):
		height = bottomY + i * interval
		left = measureLayerAtHeightFromLeftOrRight( comp1, height, leftSide=False )
		right = measureLayerAtHeightFromLeftOrRight( comp2, height, leftSide=True )
		try: # avoid gaps like in i or j
			total = left+right
			if minDist == None or minDist > total:
				minDist = total
		except:
			print("None!", minDist, height, comp1.parent.name, left, comp2.parent.name, right)
			pass
	return minDist

def placeComponentsAtDistance( thisLayer, comp1, comp2, interval=5.0, distance=10.0 ):
	thisMaster = thisLayer.associatedFontMaster()
	masterID = thisMaster.id
	original1 = comp1.component.layers[masterID]
	original2 = comp2.component.layers[masterID]
	minDist = minDistanceBetweenTwoLayers( original1, original2, interval=interval )
	if minDist != None:
		comp2shift = distance - minDist
		addedSBs = original1.RSB + original2.LSB
		comp2.x = comp1.x + original1.width - addedSBs + comp2shift

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

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

maxWidth = 0.0
for name in parenGlyphs:
	thisGlyph = thisFont.glyphs[name]
	if not thisGlyph:
		thisGlyph = GSGlyph()
		thisGlyph.name = name
		thisFont.glyphs.append(thisGlyph)

	print("Processing %s" % thisGlyph.name)
	thisGlyph.beginUndo() # begin undo grouping
	maxWidth = max( maxWidth, process( thisGlyph ) )
	print(maxWidth)
	thisGlyph.endUndo()   # end undo grouping

print(maxWidth)
scale = ( thisFont.upm / maxWidth ) * 0.95
yShift = transform( shiftY = thisFont.upm * 0.08 ).transformStruct()

for name in parenGlyphs:
	thisGlyph = thisFont.glyphs[name]
	#print "Post-processing %s" % thisGlyph.name
	postprocess( thisGlyph, scale, yShift )
	

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
