#MenuTitle: Beowulferize
# -*- coding: utf-8 -*-
__doc__="""
Turns selected glyphs into a pseudorandom Beowulf-lookalike.
"""

# Please adjust to your own needs:

alphabets = 5    # how many variants of each glyph will be created
shatter = 12     # how far each single node may be moved each time
reiterations = 2 # how often a node may be moved
linelength = 70  # maximum number of letters in a line for which the feature works


import random
random.seed()

Font = Glyphs.font
selectedGlyphs = [ l.parent for l in Font.selectedLayers ]
listOfNames = [ thisGlyph.name for thisGlyph in selectedGlyphs ]
glyphsToProcess = []

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
		newFeature = GSFeature()
		newFeature.name = featurename
		newFeature.code = beginSig + featurecode + "\n" + endSig
		targetfont.features.append( newFeature )
		return "Created new OT feature '%s'." % featurename

def create_otclass( classname   = "@default",
                    classglyphs = [ x.parent.name for x in Font.selectedLayers ],
                    targetfont  = Font ):
	"""
	Creates an OpenType class in the font.
	Default: class @default with currently selected glyphs in the current font.
	Returns a status message in form of a string.
	"""
	
	# strip '@' from beginning:
	if classname[0] == "@":
		classname = classname[1:]
	
	classCode = " ".join( classglyphs )
	
	if classname in [ c.name for c in targetfont.classes ]:
		targetfont.classes[classname].code = classCode
		return "Updated existing OT class '%s'." % classname
	else:
		newClass = GSClass()
		newClass.name = classname
		newClass.code = classCode
		targetfont.classes.append( newClass )
		return "Created new OT class: '%s'." % classname

def randomize( min, max ):
	return random.randint( min, max )

def beowulferize( thisGlyph ):
	thisGlyph.beginUndo()
	for thisLayer in thisGlyph.layers:
		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				thisNode.x +=  randomize( -shatter, shatter )
				thisNode.y +=  randomize( -shatter, shatter )
				
			thisPath.checkConnections()

	thisGlyph.endUndo()



Glyphs.clearLog()
Glyphs.showMacroWindow()
print "Beowulferizing %s:" % str( Font.familyName )

Font.disableUpdateInterface()

# Create Glyph Variants:
print "Creating alternative glyphs for:",
for thisGlyph in selectedGlyphs:
	glyphsToProcess.append( thisGlyph )
	print thisGlyph.name,
	
	for thisRound in range( alphabets ):
		newName = thisGlyph.name+".calt"+str(thisRound)
		targetGlyph = thisGlyph.copy()
		targetGlyph.name = newName
		targetGlyph.unicode = None
		glyphsToProcess.append( targetGlyph )
		Font.glyphs.append( targetGlyph )

print "\nDeforming glyphs",
for thisGlyph in glyphsToProcess:
	print ".",
	for iteration in range( reiterations ):
		beowulferize( thisGlyph )

print

# Create Classes:
print create_otclass( classname="default", classglyphs=listOfNames, targetfont=Font )
for i in range( alphabets ):
	print create_otclass( classname="calt"+str(i), classglyphs=[ n+".calt"+str(i) for n in listOfNames ], targetfont=Font )

# Create OT Feature:
beowulfCode = ""
for i in range( ( alphabets * ( linelength//alphabets ) + 1 ), 0, -1 ):
	beowulfCode += "sub @default' " + "@default " * i + "by @calt" + str( ( range(alphabets) * ((linelength//alphabets)+2))[i] ) + ";\n"

print create_otfeature( featurename="calt", featurecode=beowulfCode, targetfont=Font, codesig="BEOWULFERIZER")

Font.enableUpdateInterface()
