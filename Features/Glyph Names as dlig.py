#MenuTitle: Glyph Names as Discretionary Ligatures
# -*- coding: utf-8 -*-
__doc__="""
Adds names of exporting glyphs without a Unicode value as ligatures into the dlig feature.
"""


thisFont = Glyphs.font # frontmost font

def updated_code( oldcode, beginsig, endsig, newcode ):
	"""Replaces text in oldcode with newcode, but only between beginsig and endsig."""
	begin_offset = oldcode.find( beginsig )
	end_offset   = oldcode.find( endsig ) + len( endsig )
	newcode = oldcode[:begin_offset] + beginsig + newcode + "\n" + endsig + oldcode[end_offset:]
	return newcode

def create_otfeature( featurename = "dlig", 
                      featurecode = "# empty feature code", 
                      targetfont  = thisFont,
                      codesig     = "GLYPHNAMES-AS-LIGATURES" ):
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

def glyphNamesForString( string ):
	"""
	Returns space-separated glyph names from a string, e.g.:
	a-b.c --> a hyphen b period c
	"""
	glyphNames = []
	for x in string:
		code = "%.4X" % ord(x)
		glyphNames.append( Glyphs.glyphInfoForUnicode(code).name )
	return " ".join(glyphNames)

def codelineForGlyphName( thisName ):
	if "." in thisName:
		dotPosition = thisName.find(".")
		firstPart = thisName[:dotPosition]
		restOfName = thisName[dotPosition:]
		thisInfo = Glyphs.glyphInfoForName(firstPart)
		if thisInfo and thisInfo.unicode:
			subCode = "%s %s" % ( firstPart, glyphNamesForString(restOfName))
		else:
			subCode = glyphNamesForString( thisName )
	else:
		subCode = glyphNamesForString( thisName )
		
	codeline = "sub %s by %s;\n" % ( subCode, thisName )
	return codeline

def sortLinesByNumberOfWords( paragraph ):
	linesOfParagraph = paragraph.splitlines()
	sortedLinesOfParagraph = sorted( linesOfParagraph, key = lambda line: -line.count(" ") )
	sortedParagraph = "\n".join( sortedLinesOfParagraph )
	return sortedParagraph

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print "Glyph Names in dlig:"
print "1. Finding all glyphs that:\n   - do export\n   - do not have a Unicode\n   - are not .notdef"
listOfAllAffectedGlyphNames = [g.name for g in thisFont.glyphs if g.unicode == None and g.export == True and g.name != ".notdef"]

print "2. Building ligature code for those glyphs."
featureCode = ""
for thisName in listOfAllAffectedGlyphNames:
	featureCode += codelineForGlyphName(thisName)

print "3. %s" % create_otfeature( featurecode = featureCode )
