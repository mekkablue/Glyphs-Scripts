#MenuTitle: Fraction Fever 2
# -*- coding: utf-8 -*-
__doc__="""
Insert Tal Leming’s Fraction Fever 2 code into the font.
"""

import GlyphsApp
Font = Glyphs.font

# Inject Fraction Fever 2 Code:

fractionFeverCode = """# Fraction Fever 2 by Tal Leming

@figDefault = [zero one two three four five six seven eight nine];
@figNumer = [zero.numr one.numr two.numr three.numr four.numr five.numr six.numr seven.numr eight.numr nine.numr];
@figDenom = [zero.dnom one.dnom two.dnom three.dnom four.dnom five.dnom six.dnom seven.dnom eight.dnom nine.dnom];

lookup FractionBar {
     ignore sub slash @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault slash';
     ignore sub slash' @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault slash;
     ignore sub slash @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault slash';
     ignore sub slash' @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault slash;
     ignore sub slash @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault slash';
     ignore sub slash' @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault slash;
     ignore sub slash @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault slash';
     ignore sub slash' @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault slash;
     ignore sub slash @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault slash';
     ignore sub slash' @figDefault @figDefault @figDefault @figDefault @figDefault @figDefault slash;
     ignore sub slash @figDefault @figDefault @figDefault @figDefault @figDefault slash';
     ignore sub slash' @figDefault @figDefault @figDefault @figDefault @figDefault slash;
     ignore sub slash @figDefault @figDefault @figDefault @figDefault slash';
     ignore sub slash' @figDefault @figDefault @figDefault @figDefault slash;
     ignore sub slash @figDefault @figDefault @figDefault slash';
     ignore sub slash' @figDefault @figDefault @figDefault slash;
     ignore sub slash @figDefault @figDefault slash';
     ignore sub slash' @figDefault @figDefault slash;
     ignore sub slash @figDefault slash';
     ignore sub slash' @figDefault slash;
     sub @figDefault slash' @figDefault by fraction;
} FractionBar;

lookup Numerator1 {
     sub @figDefault' fraction by @figNumer;
} Numerator1;

lookup Numerator2 {
     sub @figDefault' @figNumer fraction by @figNumer;
} Numerator2;

lookup Numerator3 {
     sub @figDefault' @figNumer @figNumer fraction by @figNumer;
} Numerator3;

lookup Numerator4 {
     sub @figDefault' @figNumer @figNumer @figNumer fraction by @figNumer;
} Numerator4;

lookup Numerator5 {
     sub @figDefault' @figNumer @figNumer @figNumer @figNumer fraction by @figNumer;
} Numerator5;

lookup Numerator6 {
     sub @figDefault' @figNumer @figNumer @figNumer @figNumer @figNumer fraction by @figNumer;
} Numerator6;

lookup Numerator7 {
     sub @figDefault' @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer fraction by @figNumer;
} Numerator7;

lookup Numerator8 {
     sub @figDefault' @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer fraction by @figNumer;
} Numerator8;

lookup Numerator9 {
     sub @figDefault' @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer fraction by @figNumer;
} Numerator9;

lookup Numerator10 {
     sub @figDefault' @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer fraction by @figNumer;
} Numerator10;

lookup Numerator11 {
     sub @figDefault' @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer fraction by @figNumer;
} Numerator11;

lookup Numerator12 {
     sub @figDefault' @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer @figNumer fraction by @figNumer;
} Numerator12;

lookup Denominator {
     sub [fraction @figDenom] @figDefault' by @figDenom;
} Denominator;

sub @figDefault space' @figNumer by thinspace;
"""

def updated_code( oldcode, beginsig, endsig, newcode ):
	"""Replaces text in oldcode with newcode, but only between beginsig and endsig."""
	begin_offset = oldcode.find( beginsig )
	end_offset   = oldcode.find( endsig ) + len( endsig )
	newcode = oldcode[:begin_offset] + beginsig + newcode + "\n" + endsig + oldcode[end_offset:]
	return newcode

def create_otfeature( featurename = "frac",
                      featurecode = "# empty feature code",
                      targetfont  = Glyphs.font,
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

# brings macro window to front and clears its log:
Glyphs.clearLog()
print create_otfeature( featurename = "frac", featurecode = fractionFeverCode, targetfont = Font, codesig = "FRACTION-FEVER-2" )

# Check which glyphs still need to be created:
necessaryGlyphs = (
	"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
	"zero.numr", "one.numr", "two.numr", "three.numr", "four.numr", "five.numr", "six.numr", "seven.numr", "eight.numr", "nine.numr",
	"zero.dnom", "one.dnom", "two.dnom", "three.dnom", "four.dnom", "five.dnom", "six.dnom", "seven.dnom", "eight.dnom", "nine.dnom",
	"slash", "fraction", "space", "thinspace",
)

existingGlyphNames = [ g.name for g in Font.glyphs ]
glyphsToBeCreated = [ n for n in necessaryGlyphs if n not in existingGlyphNames ]

if len( glyphsToBeCreated ) > 0:
	Glyphs.showMacroWindow()
	print "These glyphs still need to be created for the feature to work:"
	print " ".join( glyphsToBeCreated )
