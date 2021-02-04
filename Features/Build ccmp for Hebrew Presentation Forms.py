#MenuTitle: Build ccmp for Hebrew Presentation Forms
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Builds the ccmp for precomposed uniFBxx glyphs, e.g. if you have pedagesh, you get 'sub pe dagesh by pedagesh' in your ccmp.
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

def create_otfeature( featureName = "calt", 
                      featureCode = "# empty feature code", 
                      targetFont  = thisFont,
                      codesig     = "DEFAULT-CODE-SIGNATURE" ):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	"""
	
	beginSig = "# BEGIN " + codesig + "\n"
	endSig   = "# END "   + codesig + "\n"
	
	targetFeature = None
	targetFeatures = [ f for f in targetFont.features if f.name==featureName and not f.automatic ]
	
	if targetFeatures:
		if len(targetFeatures)>1:
			targetFeaturesWithSig = [f for f in targetFeatures if beginSig in f.code]
			if targetFeaturesWithSig:
				targetFeature = targetFeaturesWithSig[0]
		else:
			targetFeature = targetFeatures[0]
		
		if beginSig in targetFeature.code:
			# replace old code with new code:
			targetFeature.code = updated_code( targetFeature.code, beginSig, endSig, featureCode )
		else:
			# append new code:
			targetFeature.code += "\n" + beginSig + featureCode + "\n" + endSig
			
		return "Updated existing OT feature '%s'" % featureName
	
	if not targetFeature:
		# create feature with new code:
		newFeature = GSFeature()
		newFeature.name = featureName
		newFeature.code = beginSig + featureCode + "\n" + endSig
		newFeature.automatic = False
		targetFont.features.append( newFeature )
		return "Created new OT feature '%s'" % featureName


lookup = ""

for thisGlyph in theseGlyphs:
	if thisGlyph.unicode and thisGlyph.unicode[:2]=="FB" and thisGlyph.script=="hebrew":
		glyphName = thisGlyph.name
		components = thisGlyph.glyphInfo.components
		if components:
			componentNames = [c.name for c in components]
			snippet = None
			if all( [thisFont.glyphs[n] for n in componentNames] ):
				snippet = " ".join(componentNames)
			elif len(thisGlyph.layers[0].components)>1:
				snippet = " ".join([c.componentName for c in thisGlyph.layers[0].components])
			if snippet:
				lookup += "\tsub %s by %s; # %s\n" % (snippet, glyphName, thisGlyph.unicode)
			else:
				lookup += "\t# could not create rule for %s" % glyphName

if lookup:
	lineCount = lookup.splitlines().__len__()
	lookup = "\nlookup %s {\n%s\n} %s;\n\nscript hebr;\nlookup %s;\n" % ( lookupTitle, lookup[:-1], lookupTitle, lookupTitle )
	reportMessage = create_otfeature( featureName="ccmp", featureCode=lookup, targetFont=thisFont, codesig=lookupTitle.upper() )
	Message(
		title="Created Hebrew ccmp Lookup",
		message="%s with %i Hebrew presentation form substitutions." % (reportMessage, lineCount), 
		OKButton="Cool"
		)
else:
	Message(
		title="Nothing added to ccmp",
		message="No Hebrew presentation forms found in font.", 
		OKButton="Too bad"
		)