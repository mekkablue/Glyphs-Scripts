#MenuTitle: Glyph Jelly
"""Create pseudorandom rotation feature for selected glyphs."""

# Change these values manually if you don't have Vanilla installed:

maxAngle = 10   # Maximum angle by which a glyph may rotate
alphabets = 5   # Number of instances of rotated glyphs
linelength = 80 # Length of the line the feature should be working on

import GlyphsApp
import math
import random
random.seed()

def zufall( min, max ):
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
		rotateby = zufall( -maxangle, maxangle )
		
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

def pseudorandomize( myFeature="calt", defaultClassName="@default", pseudoClassName="@calt", alphabets=5, linelength=70):
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

def main( winkel = 10, alphabets = 5, linelength = 80 ):
	Font = Glyphs.orderedDocuments()[0].font
	Doc  = Glyphs.currentDocument
	FontMaster = Doc.selectedFontMaster()
	selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

	# Make ssXX copies of selected glyphs and rotate them randomly:
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
		makeClass( [s + ssXXsuffix( x+1 ) for s in classlist], className = "@calt"+str( x ) )

	# Create OT feature:
	pseudorandomize( alphabets=alphabets, linelength=linelength )

class WackelDialog(object):

	def __init__(self):
		self.w = Window( (440, 150), title="Glyph Jelly", minSize=(440,150), maxSize=(800,150) )

		self.w.Alphabets_Text = TextBox( (20, 20, 80, 22), "Alphabets")
		self.w.Alphabets_Edit = EditText( (110, 17, 40, 22), callback=self.myCallback, text="5", continuous=False )

		self.w.Linelength_Text = TextBox( (160, 20, 80, 22), "Line length")
		self.w.Linelength_Edit = EditText( (240, 17, 40, 22), callback=self.myCallback, text="70", continuous=False )

		self.w.Winkel_Text   = TextBox( (20, 50, 80, 22), "Max angle")
		self.w.Winkel_Slider = Slider( (110, 50, -20, 23), callback=self.myCallback, stopOnTickMarks=True, tickMarkCount=50, value=12, minValue=1, maxValue=50, continuous=False )

		self.w.button_do     = Button((-150, -40, -20, 20), "Wiggle Glyphs", callback=self.okCallback)
		self.w.button_cancel = Button((-240, -40, -160, 20), "Cancel", callback=self.cancelCallback)

		self.w.open()

	def okCallback(self, sender):
		alphabets   = int( self.w.Alphabets_Edit.get()  )
		linelength  = int( self.w.Linelength_Edit.get() )
		maxAngle    = int( self.w.Winkel_Slider.get()   )
		print "OK:", maxAngle, alphabets, linelength
		main( maxAngle, alphabets, linelength )
		self.w.close()

	def cancelCallback(self, sender):
		alphabets   = int( self.w.Alphabets_Edit.get()  )
		linelength  = int( self.w.Linelength_Edit.get() )
		maxAngle    = int( self.w.Winkel_Slider.get()   )
		print "Cancelled:", maxAngle, alphabets, linelength
		self.w.close()

	def myCallback(self, sender):
		pass


try:
	from vanilla import *
	WackelDialog()
	
except Exception, e:
	import sys
	pythonversion = sys.version[:3]
	print "You should install Typesupply's Vanilla for Python", pythonversion
	main( maxAngle, alphabets, linelength )
