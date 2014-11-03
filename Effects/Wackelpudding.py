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

def randomize( min, max ):
	range = max-min
	return random.random() * range + min

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
	myComponent.transform = compTransform.transformStruct()

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
	if i < 1:
		i = 1
	elif i > 20:
		i = 20
	return ".calt.ss%.2d" % ( i )

def make_ssXX( thisGlyph, number ):
	myListOfGlyphs = []

	for x in range(number):
		newName = thisGlyph.name + ssXXsuffix( x + 1 )
		myListOfGlyphs.append( glyphcopy( thisGlyph, newName ))

	return myListOfGlyphs

def wiggle( thisGlyph, maxangle, minangle ):
	print "__wiggle", thisGlyph
	rotateby = 0.0
	minangle = float( minangle )
	
	while abs(rotateby) < minangle:
		rotateby = randomize( -maxangle, maxangle )
		
	for thisLayer in thisGlyph.layers:
		x_orig = thisLayer.width / 2.0
		y_orig = thisLayer.bounds.size.height / 2.0
		Transform = rotationTransform( angle=(rotateby/1.0), x_orig=x_orig, y_orig=y_orig )
		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				thisNode.position = Transform.transformPoint_(thisNode.position)
		
		for thisComponent in thisLayer.components:
			transformComponent( thisComponent, Transform )

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

def updated_code( oldcode, beginsig, endsig, newcode ):
	"""Replaces text in oldcode with newcode, but only between beginsig and endsig."""
	begin_offset = oldcode.find( beginsig )
	end_offset   = oldcode.find( endsig ) + len( endsig )
	newcode = oldcode[:begin_offset] + beginsig + newcode + "\n" + endsig + oldcode[end_offset:]
	return newcode

def create_otfeature( featurename = "calt", 
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
			targetfeature.code = updated_code( targetfeature.code, beginSig, endSig, featurecode )
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

	return create_otfeature( featurename=featurename, featurecode=featuretext, codesig="WACKELPUDDING")

# Make ssXX copies of selected glyphs and rotate them randomly:
classlist = []
for thisGlyph in selectedGlyphs:
	if thisGlyph.export == True:
		glyphName = thisGlyph.name
		print "Processing %s" % ( glyphName )
		classlist.append( glyphName )
		glyphList = make_ssXX( thisGlyph, alphabets )
		for thisVeryGlyph in glyphList:
			wiggle( thisVeryGlyph, maxangle, minangle )

# Create OT classes:
print create_otclass( classname="default", classglyphs=classlist )
for x in range( alphabets ):
	print create_otclass( classname="@calt%i" % x, classglyphs=[s + ssXXsuffix( x+1 ) for s in classlist]  )

# Create OT feature:
print pseudoRandomize( alphabets=alphabets, linelength=linelength, featurename=featurename )
