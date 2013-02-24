#MenuTitle: Wackelpudding
"""Create pseudorandom rotation feature for selected glyphs."""

winkel = 20 # Maximum angle by which a glyph may rotate
alphabets = 5 # Instances of rotated glyphs
linelength = 80 # length of the line the feature should be working on

import GlyphsApp
import math
import random
random.seed()

Doc  = Glyphs.currentDocument
Font = Glyphs.font
FontMaster = Doc.selectedFontMaster()
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def randomize( min, max ):
	return random.randint( min, max )

def rotate( x, y, angle=180.0, x_orig=0.0, y_orig=0.0):
	"""Rotates x/y around x_orig/y_orig by angle and returns result as [x,y]."""
	
	new_angle = ( angle / 180.0 ) * math.pi
	new_x = ( x - x_orig ) * math.cos( new_angle ) - ( y - y_orig ) * math.sin( new_angle ) + x_orig
	new_y = ( x - x_orig ) * math.sin( new_angle ) + ( y - y_orig ) * math.cos( new_angle ) + y_orig
	
	return [ new_x, new_y ]

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
	return ".calt.ss" + ( "00"+str(i) )[-2:]

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
		thisLayer.decomposeComponents() # Sorry about this.
		x_orig = thisLayer.width / 2.0
		y_orig = thisLayer.bounds().size.height / 2.0

		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				[ thisNode.x, thisNode.y ] = rotate( thisNode.x, thisNode.y, angle=(rotateby/1.0), x_orig=x_orig, y_orig=y_orig )

def makeClass( listOfGlyphNames, className="@default" ):
	print "Creating OT class:", className
	myNewClass = GSClass()
	myNewClass.name = className
	myNewClass.code = " ".join( listOfGlyphNames )
	Font.classes.append( myNewClass )

def pseudoRandomize( myFeature="calt", defaultClassName="@default", pseudoClassName="@calt", alphabets=5, linelength=70):
	print "Creating OT feature:", myFeature
	myNewFeature = GSFeature()
	myNewFeature.name = myFeature

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
		
Font.enableUpdateInterface()

# Create OT classes:
makeClass( classlist )
for x in range( alphabets ):
	makeClass( [s + ssXXsuffix( x+1 ) for s in classlist], className = "@calt"+str( x ) )

# Create OT feature:
pseudoRandomize( alphabets=alphabets, linelength=linelength )
