#MenuTitle: Build positional calt feature
# -*- coding: utf-8 -*-
"""Create calt for positional forms with .isol, .init, .medi, .fina suffixes."""

import GlyphsApp
Font = Glyphs.font

positionalFeature = "calt"
anyLetterClassName = "AnyLetter"
extensionDef = "Def"
extensionSub = "Sub"
ignoreStatements = { 
	"isol": "ignore sub @isol%s' @%s, @%s @isol%s';" % ( extensionDef, anyLetterClassName, anyLetterClassName, extensionDef ), 
	"init": "ignore sub @%s @init%s';" % ( anyLetterClassName, extensionDef ), 
	"fina": "ignore sub @fina%s' @%s;" % ( extensionDef, anyLetterClassName ),
	"medi": "sub @%s @medi%s' @%s by @medi%s;" % ( anyLetterClassName, extensionDef, anyLetterClassName, extensionSub ) 
}
suffixes = [
	"isol",
	"init",
	"fina",
	"medi"
]

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
		return "Created new OT feature '%s'" % featurename

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

allLetters = [ g.name for g in Font.glyphs if g.category == "Letter" ]
create_otclass( classname=anyLetterClassName, classglyphs=allLetters, targetfont=Font )

positionalFeatureCode = "\n"

for thisSuffix in suffixes:
	dotSuffix = "." + thisSuffix
	dotSuffixLength = len( dotSuffix )
	theseSuffixedGlyphNames = [ g.name for g in Font.glyphs if g.name.endswith( dotSuffix ) and ( Font.glyphs[g.name[:-dotSuffixLength]] is not None ) ]
	theseUnsuffixedGlyphNames = [ n[:-dotSuffixLength] for n in theseSuffixedGlyphNames ]
	
	if len(theseSuffixedGlyphNames) > 0:
		create_otclass( classname=thisSuffix+extensionDef, classglyphs=theseUnsuffixedGlyphNames, targetfont=Font )
		create_otclass( classname=thisSuffix+extensionSub, classglyphs=theseSuffixedGlyphNames, targetfont=Font )

		thisIgnoreCode = ignoreStatements[ thisSuffix ]
		if thisIgnoreCode.startswith( "ignore" ):
			ignoreSubstitution = "sub @%s%s' by @%s%s;" % ( thisSuffix, extensionDef, thisSuffix, extensionSub )
		else:
			ignoreSubstitution = ""
	
		positionalFeatureCode += "lookup %sForms {\n" % thisSuffix.title()
		positionalFeatureCode += "\t" + thisIgnoreCode + "\n"
		positionalFeatureCode += "\t" + ignoreSubstitution + "\n"
		positionalFeatureCode += "} %sForms;\n\n" % thisSuffix.title()

create_otfeature( featurename=positionalFeature, featurecode=positionalFeatureCode, targetfont=Font, codesig="POSITIONAL ALTERNATES")

