#MenuTitle: Wackelpudding
"""Create pseudorandom rotation feature for selected glyphs."""

winkel = 20 # Maximum angle by which a glyph may rotate
alphabets = 5 # Instances of rotated glyphs
linelength = 80 # length of the line the feature should be working on

import GlyphsApp
import math, random

random.seed()

Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

def randomize( min, max ):
	return random.randint( min, max )

def rotate( x, y, angle=180.0, x_orig=0.0, y_orig=0.0):
	"""Rotates x/y around x_orig/y_orig by angle and returns result as [x,y]."""
	# TO DO: update this to use rotationTransform()
	
	new_angle = ( angle / 180.0 ) * math.pi
	new_x = ( x - x_orig ) * math.cos( new_angle ) - ( y - y_orig ) * math.sin( new_angle ) + x_orig
	new_y = ( x - x_orig ) * math.sin( new_angle ) + ( y - y_orig ) * math.cos( new_angle ) + y_orig
	
	return [ new_x, new_y ]

def rotationTransform( angle=180.0, x_orig=0.0, y_orig=0.0 ):
	"""Returns a TransformStruct for rotating."""
	RotationTransform = NSAffineTransform.transform()
	RotationTransform.translateXBy_yBy_( x_orig, y_orig )
	RotationTransform.rotateByDegrees_( angle )
	RotationTransform.translateXBy_yBy_( -x_orig, -y_orig )
	
	return RotationTransform

def transformComponent( myComponent, myTransform ):
	compTransform = NSAffineTransform.transform()
	compTransform.setTransformStruct_( myComponent.transform )
	compTransform.appendTransform_( myTransform )
	t = compTransform.transformStruct()
	tNew = ( t.m11, t.m12, t.m21, t.m22, t.tX, t.tY )
	myComponent.transform = tNew

	return myComponent

def glyphcopy( sourceGlyph, targetGlyphName ):
	targetGlyph = sourceGlyph.copy()
	targetGlyph.name = targetGlyphName
	Font.glyphs.append( targetGlyph )
	return targetGlyph

def ssXXsuffix( i ):
	"""Turns an integer into an ssXX ending between .ss01 and .ss20, e.g. 5 -> '.ss05'."""
	if i < 1:
		i = 1
	elif i > 20:
		i = 20
	return ".calt.ss%.2d" % i

def make_ssXX( thisGlyph, number ):
	myListOfGlyphs = []

	for x in range(number):
		newName = thisGlyph.name + ssXXsuffix( x + 1 )
		myListOfGlyphs.append( glyphcopy( thisGlyph, newName ))

	return myListOfGlyphs

def wiggle( thisGlyph, maxangle ):
	rotateby = 0
	while rotateby == 0:
		rotateby = randomize( -maxangle, maxangle )
		
	for thisLayer in thisGlyph.layers:
		x_orig = thisLayer.width / 2.0
		y_orig = thisLayer.bounds.size.height / 2.0
		
		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				[ thisNode.x, thisNode.y ] = rotate( thisNode.x, thisNode.y, angle=(rotateby/1.0), x_orig=x_orig, y_orig=y_orig )
		
		for thisComponent in thisLayer.components:
			thisComponent = transformComponent( thisComponent, rotationTransform( angle=(rotateby/1.0), x_orig=x_orig, y_orig=y_orig ) )

def makeClass( listOfGlyphNames, className="@default" ):
	print "Creating OT class:", className
	myNewClass = GSClass(className, " ".join( listOfGlyphNames ))
	Font.classes.append( myNewClass )

def pseudoRandomize( myFeature="calt", defaultClassName="@default", pseudoClassName="@calt", alphabets=5, linelength=70):
	print "Creating OT feature:", myFeature
	myNewFeature = GSFeature(myFeature)
	
	featuretext = ""
	listOfClasses = (range(alphabets)*((linelength//alphabets)+2))
	for i in range( (alphabets * ( linelength//alphabets ) + 1), 0, -1 ):
		newline = "  sub @default' " + "@default "*i + "by @calt" + str( listOfClasses[i] ) + ";\n"
		featuretext = featuretext + newline

	myNewFeature.code = featuretext
	Font.features.append(myNewFeature)

# Make ssXX copies of selected glyphs and rotate them randomly:

Font.disableUpdateInterface()

classlist = []

for thisGlyph in selectedGlyphs:
	glyphName = thisGlyph.name
	print "Processing", glyphName
	classlist.append( glyphName )
	glyphList = make_ssXX( thisGlyph, alphabets )
	for thisVeryGlyph in glyphList:
		wiggle( thisVeryGlyph, winkel )
		

# Create OT classes:
makeClass( classlist )
for x in range( alphabets ):
	makeClass( [s + ssXXsuffix( x+1 ) for s in classlist], className = "@calt%d" % x )

# Create OT feature:
pseudoRandomize( alphabets=alphabets, linelength=linelength )

Font.enableUpdateInterface()