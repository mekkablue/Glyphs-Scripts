#MenuTitle: Build positional calt feature
# -*- coding: utf-8 -*-
__doc__="""
Create calt for positional forms with .isol, .init, .medi, .fina suffixes.
"""

import GlyphsApp
thisFont = Glyphs.font
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

def create_otfeature( featureName = "calt",
                      featureCode = "# empty feature code",
                      targetFont  = None,
                      codeSig     = "DEFAULT-CODE-SIGNATURE" ):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	"""
	
	if targetFont:
		beginSig = "# BEGIN " + codeSig + "\n"
		endSig   = "# END "   + codeSig + "\n"
	
		if featureName in [ f.name for f in targetFont.features ]:
			# feature already exists:
			targetFeature = targetFont.features[ featureName ]
		
			if beginSig in targetFeature.code:
				# replace old code with new code:
				targetFeature.code = updated_code( targetFeature.code, beginSig, endSig, featureCode )
			else:
				# append new code:
				targetFeature.code += "\n" + beginSig + featureCode + "\n" + endSig
			
			return "Updated existing OT feature '%s'." % featureName
		else:
			# create feature with new code:
			newFeature = GSFeature()
			newFeature.name = featureName
			newFeature.code = beginSig + featureCode + "\n" + endSig
			targetFont.features.append( newFeature )
			return "Created new OT feature '%s'" % featureName
	else:
		return "ERROR: Could not create OT feature %s. No font detected." % ( featureName )

def create_otclass( className       = "@default",
                    classGlyphNames = [],
                    targetFont      = None ):
	"""
	Creates an OpenType class in the font.
	Default: class @default with currently selected glyphs in the current font.
	Returns a status message in form of a string.
	"""
	
	if targetFont and classGlyphNames:
		# strip '@' from beginning:
		if className[0] == "@":
			className = className[1:]
	
		classCode = " ".join( classGlyphNames )
	
		if className in [ c.name for c in targetFont.classes ]:
			targetFont.classes[className].code = classCode
			return "Updated existing OT class '%s'." % ( className )
		else:
			newClass = GSClass()
			newClass.name = className
			newClass.code = classCode
			targetFont.classes.append( newClass )
			return "Created new OT class: '%s'" % ( className )
	else:
		return "ERROR: Could not create OT class %s. Missing either font or glyph names, or both." % ( className )

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print "Building positional calt feature:"

allLetterNames = [ g.name for g in thisFont.glyphs if g.category == "Letter" and g.export ]

print "\t%s" % create_otclass(
	className       = anyLetterClassName,
	classGlyphNames = allLetterNames,
	targetFont      = thisFont
)

positionalFeatureCode = "\n"

for thisSuffix in suffixes:
	dotSuffix = "." + thisSuffix
	dotSuffixLength = len( dotSuffix )
	theseSuffixedGlyphNames = [ 
		g.name for g in thisFont.glyphs 
		if dotSuffix in g.name # glyph has suffix
		and g.export # suffixed glyph exports
		and thisFont.glyphs[g.name.replace(dotSuffix,"")] is not None # unsuffixed counterpart exists
		and thisFont.glyphs[g.name.replace(dotSuffix,"")].export # unsuffixed glyph exports
	]
	theseSuffixedGlyphNames = list(set(theseSuffixedGlyphNames)) # make sure every glyph is unique
	theseUnsuffixedGlyphNames = [ n.replace(dotSuffix,"") for n in theseSuffixedGlyphNames ]
	
	print "\tFound %i glyphs with a %s suffix, and %i unsuffixed counterparts." % (
		len( theseSuffixedGlyphNames ),
		dotSuffix,
		len( theseUnsuffixedGlyphNames )
	)
	
	if len( theseSuffixedGlyphNames ) > 0:
		print "\t%s" % create_otclass(
			className       = thisSuffix + extensionDef,
			classGlyphNames = theseUnsuffixedGlyphNames,
			targetFont      = thisFont
		)
		print "\t%s" % create_otclass(
			className       = thisSuffix + extensionSub,
			classGlyphNames = theseSuffixedGlyphNames,
			targetFont      = thisFont
		)

		thisIgnoreCode = ignoreStatements[ thisSuffix ]
		
		if thisIgnoreCode.startswith( "ignore" ):
			ignoreSubstitution = "\tsub @%s%s' by @%s%s;\n" % (
				thisSuffix,
				extensionDef,
				thisSuffix,
				extensionSub
			)
		else:
			ignoreSubstitution = ""
	
		positionalFeatureCode += "lookup %sForms {\n" % ( thisSuffix.title() )
		positionalFeatureCode += "\t%s\n" % ( thisIgnoreCode )
		positionalFeatureCode += ignoreSubstitution
		positionalFeatureCode += "} %sForms;\n\n" % ( thisSuffix.title() )

print "\t%s" % create_otfeature(
	featureName = positionalFeature,
	featureCode = positionalFeatureCode,
	targetFont  = thisFont,
	codeSig     = "POSITIONAL ALTERNATES"
)
