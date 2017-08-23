#MenuTitle: Build Kana Features
# -*- coding: utf-8 -*-
__doc__="""
Creates hkna, vkna and pkna OpenType features for Kana.
"""

thisFont = Glyphs.font # frontmost font
features = ("pkna","vkna")

def updatedCode( oldCode, beginSig, endSig, newCode ):
	"""Replaces text in oldCode with newCode, but only between beginSig and endSig."""
	beginOffset = oldCode.find( beginSig )
	endOffset   = oldCode.find( endSig ) + len( endSig )
	newCode = oldCode[:beginOffset] + beginSig + newCode + "\n" + endSig + oldCode[endOffset:]
	return newCode

def createOTFeature( featureName = "calt", 
                     featureCode = "# empty feature code", 
                     targetFont  = Glyphs.font,
                     codeSig     = "CUSTOM-CONTEXTUAL-ALTERNATES" ):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	featureName: name of the feature (str),
	featureCode: the AFDKO feature code (str),
	targetFont: the GSFont object receiving the feature,
	codeSig: the code signature (str) used as delimiters.
	"""
	
	beginSig = "# BEGIN " + codeSig + "\n"
	endSig   = "# END "   + codeSig + "\n"
	
	if featureName in [ f.name for f in targetFont.features ]:
		# feature already exists:
		targetFeature = targetFont.features[ featureName ]
		
		if beginSig in targetFeature.code:
			# replace old code with new code:
			targetFeature.code = updatedCode( targetFeature.code, beginSig, endSig, featureCode )
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


affectedGlyphNames = {}
for feature in features:
	affectedGlyphNames[feature] = []
	
for thisGlyph in thisFont.glyphs:
	for feature in features:
		if thisGlyph.name.endswith(".%s"%feature):
			affectedGlyphNames[feature].append( thisGlyph.name[:-5] ) 

for feature in affectedGlyphNames:
	code = ""
	for glyphName in affectedGlyphNames[feature]:
		code += "sub %s by %s.%s;\n" % (glyphName, glyphName, feature)
	if code:
		createOTFeature(featureName=feature,featureCode=code,targetFont=thisFont,codeSig="Automated %s code"%feature)
		

