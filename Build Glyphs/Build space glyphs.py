#MenuTitle: Build space glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Creates mediumspace-math, emquad, emspace, enquad, enspace, figurespace, fourperemspace, hairspace, narrownbspace, punctuationspace, sixperemspace, nbspace, thinspace, threeperemspace, zerowidthspace.
"""

def tabfigure(font):
	fallbacks = ("zero.tf", "zero.tosf", "zero.tab", "zero.tnum")
	for referenceFigure in fallbacks:
		if font.glyphs[referenceFigure]:
			return referenceFigure
	return "zero"

def createSpaceGlyph( thisFont, glyphName, widthKey ):
	created = 0
	if thisFont.glyphs[glyphName]:
		print(u"👍🏻 %s: already exists in %s. Updating..." % (glyphName, thisFont.familyName))
		space = thisFont.glyphs[glyphName]
		if not space.export:
			space.export = True
			print(u"😬 %s was set to not export. Fixed. 🙌" % glyphName)
	else:
		print(u"✅ Creating %s" % glyphName)
		space = GSGlyph(glyphName)
		thisFont.glyphs.append(space)
		created = 1
	
	# space.beginUndo() # undo grouping causes crashes
	
	print(u"✅ setting width metrics key: %s" % widthKey)
	space.widthMetricsKey = widthKey
	space.rightMetricsKey = None
	space.leftMetricsKey = None
	for thisLayer in space.layers:
		# make sure it is empty:
		thisLayer.clear() 
		# clear all layer keys:
		thisLayer.widthMetricsKey = None
		thisLayer.rightMetricsKey = None
		thisLayer.leftMetricsKey = None
		# update metrics:
		thisLayer.updateMetrics()
		thisLayer.syncMetrics()
	
	if not space.unicode:
		newUnicode = Glyphs.glyphInfoForName(glyphName).unicode
		if not newUnicode:
			print(u"⛔️ Could not determine Unicode for %s. Please review.")
		else:
			print(u"✅ Setting Unicode value %s glyph %s" % (newUnicode, glyphName))
			space.unicode = newUnicode
	
	# space.endUndo() # undo grouping causes crashes
	return created
		

# frontmost font:
thisFont = Glyphs.font

# brings macro window to front and clears its log:
Glyphs.clearLog()

# start reporting
print("Building space glyphs for %s" % thisFont.familyName)
print(thisFont.filepath)
print()

# space dict:
spaces = {
	"mediumspace-math": "=%i" % (thisFont.upm*4/18), # "MMSP": four-eighteenths of an em
	"emquad": "=%i" % thisFont.upm, # same as emspace
	"emspace": "=%i" % thisFont.upm, # "mutton": nominally, a space equal to the type size in points, may scale by the condensation factor of a font
	"enquad": "=%i" % (thisFont.upm//2), # same as enspace
	"enspace": "=%i" % (thisFont.upm//2), # "nut": half an em
	"figurespace": "=%s" % tabfigure(thisFont), # space equal to tabular width of a font, this is equivalent to the digit width of fonts with fixed-width digits
	"threeperemspace": "=%s" % (thisFont.upm//3), # thick space
	"fourperemspace": "=%s" % (thisFont.upm//4), # mid space
	"sixperemspace": "=%s" % (thisFont.upm//6), # in computer typography sometimes equated to thin space
	"narrownbspace": "=space*0.2", # "NNBSP": a narrow form of a no-break space, typically the width of a thin space or a mid space
	"punctuationspace": "=period", # space equal to narrow punctuation of a font
	"nbspace": "=space", # commonly abbreviated as NBSP
	"thinspace": "=%i" % (thisFont.upm*0.125), # a fifth of an em (or sometimes a sixth), InD: an eighth
	"hairspace": "=%i" % (thisFont.upm*0.07), # thinner than a thin space; in traditional typography, the thinnest space available
	"zerowidthspace": "=0", # "ZWSP": this character is intended for invisible word separation and for line break control; it has no width, but its presence between two characters does not prevent increased letter spacing in justification
}

thisFont.disableUpdateInterface() # suppresses UI updates in Font View, speeds things up a little
try:
	# build spaces:
	createdSpaces = 0
	for thisSpace in spaces:
		widthKey = spaces[thisSpace]
		createdSpaces += createSpaceGlyph( thisFont, thisSpace, widthKey )
		print() 

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
 
reportMessage = "%i of %i space glyphs added" % (createdSpaces, len(spaces))
print("Done. %s."%reportMessage)
# Floating notification:
Glyphs.showNotification( 
	u"%s: space glyphs built" % (thisFont.familyName),
	u"%s, %i were already in the font. Detailed report in Macro Window." % (reportMessage, (len(spaces)-createdSpaces)),
	)

