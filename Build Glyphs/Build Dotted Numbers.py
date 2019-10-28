#MenuTitle: Build dotted numbers
# -*- coding: utf-8 -*-
__doc__="""
Build dotted numbers from your default figures and the period.
"""

from Foundation import NSPoint
distanceBetweenComponents = 100.0

numberGlyphs = [
	"one_period",
	"two_period",
	"three_period",
	"four_period",
	"five_period",
	"six_period",
	"seven_period",
	"eight_period",
	"nine_period",
	"one_zero_period",
	"one_one_period",
	"one_two_period",
	"one_three_period",
	"one_four_period",
	"one_five_period",
	"one_six_period",
	"one_seven_period",
	"one_eight_period",
	"one_nine_period",
	"two_zero_period",
]

def unsuffixed(name):
	if "." in name:
		return name[:name.find(".")]
	else:
		return name

def measureLayerAtHeightLeftFromLeftOrRight( thisLayer, height, leftSide=True ):
	try:
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
	except:
		return None

def minDistanceBetweenTwoLayers( comp1, comp2, interval=5.0 ):
	topY = min( comp1.bounds.origin.y+comp1.bounds.size.height, comp2.bounds.origin.y+comp2.bounds.size.height )
	bottomY = max( comp1.bounds.origin.y, comp2.bounds.origin.y )
	distance = topY - bottomY
	minDist = None
	for i in range(int(distance/interval)):
		height = bottomY + i * interval
		left = measureLayerAtHeightLeftFromLeftOrRight( comp1, height, leftSide=False )
		right = measureLayerAtHeightLeftFromLeftOrRight( comp2, height, leftSide=True )
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
	minDist = minDistanceBetweenTwoLayers( original1, original2, interval=interval )
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


def process( thisGlyph ):
	parts = unsuffixed(thisGlyph.name).split("_")
	maxWidth = thisFont.upm
	thisGlyph.leftMetricsKey = None
	thisGlyph.rightMetricsKey = None
	print "-".join(parts)
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
		maxWidth = max(thisLayer.bounds.size.width*1.1, maxWidth)
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

thisFont = Glyphs.font # frontmost font
thisFont.disableUpdateInterface() # suppresses UI updates in Font View

maxWidth = 0.0
for name in numberGlyphs:
	thisGlyph = thisFont.glyphs[name]
	if not thisGlyph:
		thisGlyph = GSGlyph()
		thisGlyph.name = name
		thisFont.glyphs.append(thisGlyph)

	print "Processing %s" % thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	maxWidth = max( maxWidth, process( thisGlyph ) )
	print maxWidth
	thisGlyph.endUndo()   # end undo grouping

print maxWidth
scale = ( thisFont.upm / maxWidth ) * 0.95
yShift = transform( shiftY = thisFont.upm * 0.06 ).transformStruct()

for name in numberGlyphs:
	thisGlyph = thisFont.glyphs[name]
	#print "Post-processing %s" % thisGlyph.name
	postprocess( thisGlyph, scale, yShift )


thisFont.enableUpdateInterface() # re-enables UI updates in Font View
