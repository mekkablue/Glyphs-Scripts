#MenuTitle: Compare Font Spacings
# -*- coding: utf-8 -*-
__doc__="""
Compare spacing of open fonts, output in the Macro Window.
"""

import GlyphsApp

abc = "abcdefghijklmnopqrstuvwxyz"
frequencies = { # Source: Wikipedia
	"a": 0.08167,
	"b": 0.01492,
	"c": 0.02782,
	"d": 0.04253,
	"e": 0.12702,
	"f": 0.02228,
	"g": 0.02015,
	"h": 0.06094,
	"i": 0.06966,
	"j": 0.00153,
	"k": 0.00772,
	"l": 0.04025,
	"m": 0.02406,
	"n": 0.06749,
	"o": 0.07507,
	"p": 0.01929,
	"q": 0.00095,
	"r": 0.05987,
	"s": 0.06327,
	"t": 0.09056,
	"u": 0.02758,
	"v": 0.00978,
	"w": 0.02361,
	"x": 0.00150,
	"y": 0.01974,
	"z": 0.00074
}

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

theFonts = Glyphs.fonts
for theFont in theFonts:
	print "FONT: %s\n%s\n" % (theFont.familyName, theFont.filepath)
	
	for thisMaster in theFont.masters:
		print "  Master: %s" % thisMaster.name
		
		lowercaseWidths = 0
		uppercaseWidths = 0
		weightedLowercaseWidths = 0
		weightedUppercaseWidths = 0
		
		for thisLetter in abc:
			lcWidth = theFont.glyphs[thisLetter].layers[thisMaster.id].width
			ucWidth = theFont.glyphs[thisLetter.upper()].layers[thisMaster.id].width
			factor = frequencies[thisLetter]
			
			lowercaseWidths += lcWidth
			uppercaseWidths += ucWidth
			weightedLowercaseWidths += lcWidth * factor
			weightedUppercaseWidths += ucWidth * factor
		
		print "    Lowercase: %.1f" % lowercaseWidths
		print "    Uppercase: %.1f" % uppercaseWidths
		print "    Weighted English Lowercase: %.1f" % (weightedLowercaseWidths * 26)
		print "    Weighted English Uppercase: %.1f" % (weightedUppercaseWidths * 26)
		print
