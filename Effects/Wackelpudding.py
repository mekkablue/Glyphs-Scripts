#MenuTitle: Wackelpudding
# -*- coding: utf-8 -*-
__doc__="""
Create pseudorandom rotation feature for selected glyphs.
"""

maxangle = 20.0 # Maximum angle by which a glyph may rotate
minangle = 4.0
alphabets = 5 # Instances of rotated glyphs
linelength = 80 # length of the line the feature should be working on
featurename = "calt"

import GlyphsApp
import math, random
random.seed()

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

def rotationTransform( angle=180.0, xOrigin=0.0, yOrigin=0.0 ):
	"""Returns a TransformStruct for rotating."""
	RotationTransform = NSAffineTransform.transform()
	RotationTransform.translateXBy_yBy_( xOrigin, yOrigin )
	RotationTransform.rotateByDegrees_( angle )
	RotationTransform.translateXBy_yBy_( -xOrigin, -yOrigin )
	return RotationTransform

def clearLayer( thisLayer ):
	thisLayer.parent.beginUndo()
	for i in range( len( thisLayer.paths ))[::-1]:
		del thisLayer.paths[i]
	for i in range( len( thisLayer.components ))[::-1]:
		del thisLayer.components[i]
	thisLayer.parent.endUndo()

def glyphcopy( sourceGlyph, targetGlyphName ):
	targetGlyph = sourceGlyph.copy()
	targetGlyph.name = targetGlyphName
	Font.glyphs.append( targetGlyph )
	# targetGlyph = Font.glyphs[ targetGlyphName ]

	# Place Components:
	MasterIDs = [m.id for m in Font.masters]
	for thisMaster in MasterIDs:
		sourceLayer = sourceGlyph.layers[ thisMaster ]
		targetLayer = targetGlyph.layers[ thisMaster ]
		clearLayer( targetLayer )
		targetLayer.width = sourceLayer.width
		myComponent = GSComponent( sourceGlyph.name )
		myComponent.componentName = sourceGlyph.name
		targetLayer.components.append( myComponent )
		
	return targetGlyph

def ssXXsuffix( i ):
	"""Turns an integer into an ssXX ending between .ss01 and .ss20, e.g. 5 -> '.ss05'."""
	i = i%21  # max 20
	if not i: # if 0
		i = 1
	return ".calt.ss%.2d" % ( i )

def make_ssXX( thisGlyph, number ):
	myListOfGlyphs = []
	for x in range(number):
		newName = thisGlyph.name + ssXXsuffix( x + 1 )
		print "glyphcopy( thisGlyph, newName ): ", thisGlyph, newName
		copiedGlyph = glyphcopy( thisGlyph, newName )
		myListOfGlyphs.append( copiedGlyph )
	return myListOfGlyphs

def wiggle( thisGlyph, maxangle, minangle ):
	rotateBy = random.random() * (maxangle-minangle) + minangle
	positiveOrNegative = -1 + 2 * round(random.random()) # should be either -1 or 1
	rotateBy *= positiveOrNegative

	for thisLayer in thisGlyph.layers:
		# Disable aligment for components, so we can transform freely:
		for thisComponent in thisLayer.components:
			thisComponent.setDisableAlignment_( True )
		
		# Transform the whole layer:
		xOrigin = thisLayer.width * 0.5
		yOrigin = thisLayer.bounds.size.height * 0.5
		thisLayer.transform_checkForSelection_doComponents_( 
			rotationTransform( angle=rotateBy, xOrigin=xOrigin, yOrigin=yOrigin ), # rotate around origin
			False, # checkForSelection
			True   # doComponents
		)

def create_otclass( classname   = "@default",
                    classglyphs = [ x.parent.name for x in Font.selectedLayers ],
                    targetfont  = Font ):
	
	# strip '@' from beginning:
	classname = classname.lstrip("@")
	classcode = " ".join( classglyphs )
	otClass = targetfont.classes[classname]
	
	if otClass:
		otClass.code = classcode
		return "Updated existing OT class '%s'." % classname
	else:
		newClass = GSClass( classname, classcode )
		targetfont.classes.append( newClass )
		return "Created new OT class: '%s'" % classname

def updateCode( oldcode, beginsig, endsig, newcode ):
	"""Replaces text in oldcode with newcode, but only between beginsig and endsig."""
	begin_offset = oldcode.find( beginsig )
	end_offset   = oldcode.find( endsig ) + len( endsig )
	newcode = oldcode[:begin_offset] + beginsig + newcode + "\n" + endsig + oldcode[end_offset:]
	return newcode

def otFeatureCode( featurename = "calt",
                      featurecode = "# empty feature code",
                      targetfont  = Font,
                      codesig     = "DEFAULT-CODE-SIGNATURE" ):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	"""
	
	beginSig = "# BEGIN " + codesig + "\n"
	endSig   = "# END "   + codesig + "\n"
	
	if featurename in [ f.name for f in targetfont.features ]:
		# feature already exists:
		targetfeature = targetfont.features[ featurename ]
		
		if beginSig in targetfeature.code:
			# replace old code with new code:
			targetfeature.code = updateCode( targetfeature.code, beginSig, endSig, featurecode )
		else:
			# append new code:
			targetfeature.code += "\n" + beginSig + featurecode + "\n" + endSig
			
		return "Updated existing OT feature '%s'." % featurename
	else:
		# create feature with new code:
		newFeature = GSFeature( featurename, beginSig + featurecode + "\n" + endSig )
		targetfont.features.append( newFeature )
		return "Created new OT feature '%s'" % featurename

def pseudoRandomize( featurename="calt", defaultClassName="@default", pseudoClassName="@calt", alphabets=5, linelength=70 ):
	featuretext = ""
	listOfClasses = (range(alphabets)*((linelength//alphabets)+2))
	for i in range( (alphabets * ( linelength//alphabets ) + 1), 0, -1 ):
		newline = "sub @default' " + "@default "*i + "by @calt" + str( listOfClasses[i] ) + ";\n"
		featuretext = featuretext + newline

	return otFeatureCode( featurename=featurename, featurecode=featuretext, codesig="WACKELPUDDING")

# Make ssXX copies of selected glyphs and rotate them randomly:
classlist = []
for thisGlyph in selectedGlyphs:
	if thisGlyph.export == True:
		glyphName = thisGlyph.name
		print "Processing %s" % ( glyphName )
		classlist.append( glyphName )
		glyphList = make_ssXX( thisGlyph, alphabets )
		for thisVeryGlyph in glyphList:
			print "Wiggling", thisVeryGlyph.name
			wiggle( thisVeryGlyph, maxangle, minangle )

# Create OT classes:
print create_otclass( classname="default", classglyphs=classlist )
for x in range( alphabets ):
	print create_otclass( classname="@calt%i" % x, classglyphs=[s + ssXXsuffix( x+1 ) for s in classlist]  )

# Create OT feature:
print pseudoRandomize( alphabets=alphabets, linelength=linelength, featurename=featurename )
