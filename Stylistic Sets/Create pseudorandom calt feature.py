#MenuTitle: Create pseudorandom calt feature from ssXX glyphs
# -*- coding: utf-8 -*-
__doc__="""
Create pseudorandom calt (contextual alternatives) feature based on number of existing ssXX glyphs in the font.
"""

linelength = 70
addDefault = True
featureName = "calt"
classNamePrefix = featureName

def ssXXsuffix(i):
	"""Turns an integer into an ssXX ending between .ss01 and .ss20, e.g. 5 -> '.ss05'."""
	returnString = ""
	if i > 0 and i <= 20:
		returnString = ".ss%02i" % i
	return returnString

def updated_code( oldcode, beginsig, endsig, newcode ):
	"""Replaces text in oldcode with newcode, but only between beginsig and endsig."""
	begin_offset = oldcode.find( beginsig )
	end_offset   = oldcode.find( endsig ) + len( endsig )
	newcode = oldcode[:begin_offset] + beginsig + newcode + "\n" + endsig + oldcode[end_offset:]
	return newcode

def create_otfeature( featurename = "calt", 
                      featurecode = "# empty feature code", 
                      targetFont  = Glyphs.font,
                      codesig     = "PSEUDORANDOM" ):
	"""
	Creates or updates an OpenType feature in the thisFont.
	Returns a status message in form of a string.
	"""
	
	beginSig = "# BEGIN " + codesig + "\n"
	endSig   = "# END "   + codesig + "\n"
	
	if featurename in [ f.name for f in targetFont.features ]:
		# feature already exists:
		targetfeature = targetFont.features[ featurename ]
		
		if beginSig in targetfeature.code:
			# replace old code with new code:
			targetfeature.code = updated_code( targetfeature.code, beginSig, endSig, featurecode )
		else:
			# append new code:
			targetfeature.code += "\n" + beginSig + featurecode + "\n" + endSig
			
		return "Updated existing OT feature '%s'." % featurename
	else:
		# create feature with new code:
		newFeature = GSFeature()
		newFeature.name = featurename
		newFeature.code = beginSig + featurecode + "\n" + endSig
		targetFont.features.append( newFeature )
		return "Created new OT feature '%s'" % featurename

def create_otclass( className   = "@default", 
                    classGlyphs = [ g.name for g in Glyphs.font.glyphs if "." not in g.name ], 
                    targetFont  = Glyphs.font ):
	"""
	Creates an OpenType class in the thisFont.
	Default: class @default with currently selected glyphs in the current thisFont.
	Returns a status message in form of a string.
	"""
	
	# strip '@' from beginning:
	if className[0] == "@":
		className = className[1:]
	
	classCode = " ".join( classGlyphs )
	
	if className in [ c.name for c in targetFont.classes ]:
		targetFont.classes[className].code = classCode
		return "Updated existing OT class '%s'." % className
	else:
		newClass = GSClass()
		newClass.name = className
		newClass.code = classCode
		targetFont.classes.append( newClass )
		return "Created new OT class: '%s'" % className

def highestStylisticSetInNameList( nameList ):
	ssXX_exists = True
	i = 1
	while ssXX_exists:
		ssXX = ssXXsuffix(i)
		ssXXglyphs = [ x for x in nameList if x.find( ssXX ) is not -1 ]
		if len(ssXXglyphs) == 0:
			i-=1
			ssXX_exists = False
		else:
			i+=1
	return i

thisFont = Glyphs.font
allGlyphs = [ x.name for x in list( thisFont.glyphs ) ]
highestSetNumber = highestStylisticSetInNameList( allGlyphs )
ssXX = ssXXsuffix( highestSetNumber )

if not ssXX:
	print "No ssXX glyphs in the thisFont. Aborting."
else:
	ssXXglyphs = [ x for x in allGlyphs if x.find( ssXX ) > -1 ]

	# Build and add OT classes:
	defaultGlyphs = [x[:-5] for x in ssXXglyphs]
	for XX in range(highestSetNumber+1):
		className = "%s%02i" % ( classNamePrefix, XX )
		classGlyphs = [ x + ssXXsuffix(XX) for x in defaultGlyphs ] + ["space"]
		print create_otclass( className = className, classGlyphs = classGlyphs, targetFont = thisFont )
	
	# Build OT feature:
	featureText = ""
	if addDefault:
		zeroOrOne = 0
	else:
		zeroOrOne = 1
	
	suffixNumberRange = range( zeroOrOne, highestSetNumber+1 ) * ( linelength // highestSetNumber+2 )
	
	for j in range( highestSetNumber * ( linelength // highestSetNumber+1 ), 0, -1 ):
		newLine = "sub @%s00' %s by @%s%02i;\n" % (
			classNamePrefix, "@%s00 "%classNamePrefix * j, 
			classNamePrefix, 
			suffixNumberRange[j] 
		) 
		featureText += newLine
	
	# Add OT feature:
	print create_otfeature( featurename = featureName, featurecode = featureText, targetFont = thisFont )
