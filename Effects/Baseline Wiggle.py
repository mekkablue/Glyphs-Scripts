#MenuTitle: Baseline Wiggle
# -*- coding: utf-8 -*-
__doc__="""
Create pseudorandom GPOS baseline shift for all glyphs.
"""


import random
random.seed()

Font = Glyphs.font

wiggleMax  =  20
wiggleMin  = -20
linelength =  150
featurename = "titl"
classname = "wiggle"

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

featuretext = ""
for j in range( linelength, 0, -1 ):
	newline = "pos @wiggle' " + "@wiggle "*j + "<0 " + str( random.randint( wiggleMin, wiggleMax ) ) + " 0 0>;\n"
	featuretext = featuretext + newline

print create_otclass( classname=classname, classglyphs=sorted([ g.name for g in Font.glyphs if g.export == True ]) )
print create_otfeature( featurename=featurename, featurecode=featuretext, codesig="BASELINE-WIGGLE" )