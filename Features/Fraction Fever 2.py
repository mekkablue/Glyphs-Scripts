# MenuTitle: Fraction Fever 2
__doc__ = """
Insert Tal Leming’s Fraction Fever 2 code into the font.
"""

from mekkablue import createOTFeature
from GlyphsApp import Glyphs

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


# brings macro window to front and clears its log:
if not Font:
	print("Please open a font first.")
else:
	Glyphs.clearLog()
	print(createOTFeature(featureName="frac", featureCode=fractionFeverCode, targetFont=Font, codeSig="FRACTION-FEVER-2"))

	# Check which glyphs still need to be created:
	necessaryGlyphs = (
		"zero",
		"one",
		"two",
		"three",
		"four",
		"five",
		"six",
		"seven",
		"eight",
		"nine",
		"zero.numr",
		"one.numr",
		"two.numr",
		"three.numr",
		"four.numr",
		"five.numr",
		"six.numr",
		"seven.numr",
		"eight.numr",
		"nine.numr",
		"zero.dnom",
		"one.dnom",
		"two.dnom",
		"three.dnom",
		"four.dnom",
		"five.dnom",
		"six.dnom",
		"seven.dnom",
		"eight.dnom",
		"nine.dnom",
		"slash",
		"fraction",
		"space",
		"thinspace",
	)

	existingGlyphNames = [g.name for g in Font.glyphs]
	glyphsToBeCreated = [n for n in necessaryGlyphs if n not in existingGlyphNames]

	if len(glyphsToBeCreated) > 0:
		Glyphs.showMacroWindow()
		print("These glyphs still need to be created for the feature to work:")
		print(" ".join(glyphsToBeCreated))
