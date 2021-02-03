#MenuTitle: Build ccmp for Hebrew Presentation Forms
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Builds the ccmp for precomposed uniFBxx glyphs, e.g. if you padagesh, you get 'sub pa dagesh by padagesh' in your ccmp.
"""

lookupTitle = "hebrewPresentationForms"
thisFont = Glyphs.font
theseGlyphs = thisFont.glyphs
firstMasterID = thisFont.masters[0].id

def updated_code( oldcode, beginsig, endsig, newcode ):
	"""Replaces text in oldcode with newcode, but only between beginsig and endsig."""
	begin_offset = oldcode.find( beginsig )
	end_offset   = oldcode.find( endsig ) + len( endsig )
	newcode = oldcode[:begin_offset] + beginsig + newcode + "\n" + endsig + oldcode[end_offset:]
	return newcode

def create_otfeature( featurename = "calt", 
                      featurecode = "# empty feature code", 
                      targetfont  = thisFont,
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


lookup = ""

for thisGlyph in theseGlyphs:
	if thisGlyph.unicode and thisGlyph.unicode[:2] == "FB" and "-hb" in thisGlyph.name:
		glyphName = thisGlyph.name
		comps = thisGlyph.layers[firstMasterID].components
		componentNames = " ".join([c.component.name for c in comps])
		lookup += "\tsub %s by %s;\n" % (componentNames, glyphName)

if lookup:
	lineCount = lookup.splitlines().__len__()
	lookup = "\nlookup %s {\n%s\n} %s;\n\nscript hebr;\nlookup %s;\n" % ( lookupTitle, lookup[:-1], lookupTitle, lookupTitle )
	create_otfeature( featurename="ccmp", featurecode=lookup, targetfont=thisFont, codesig=lookupTitle.upper() )
	Message(
		title="Created Hebrew ccmp Lookup",
		message="Created ccmp OpenType feature with %i Hebrew presentation form substitutions." % lineCount, 
		OKButton="Cool"
		)
else:
	Message(
		title="Nothing added to ccmp",
		message="No Hebrew presentation forms found in font.", 
		OKButton="Too bad"
		)