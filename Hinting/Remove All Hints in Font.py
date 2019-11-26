from __future__ import print_function
#MenuTitle: Remove All Hints in Font
# -*- coding: utf-8 -*-
__doc__="""
Deletes all hints throughout the whole font.
"""

from GlyphsApp import TOPGHOST, STEM, BOTTOMGHOST, TTANCHOR, TTSTEM, TTALIGN, TTINTERPOLATE, TTDIAGONAL

Font = Glyphs.font
totalDeletedHints = 0

print("Deleting all hints in %s ..." % Font.familyName)

def deleteHintsInLayer( thisLayer ):
	try:
		print(u"Processing %s, layer: %s" % (thisLayer.parent.name, thisLayer.name))
	except Exception as e:
		print(e)
	numOfHints = 0
	for hintIndex in range(len(thisLayer.hints))[::-1]:
		if thisLayer.hints[hintIndex].type in (TOPGHOST, STEM, BOTTOMGHOST, TTANCHOR, TTSTEM, TTALIGN, TTINTERPOLATE, TTDIAGONAL):
			del thisLayer.hints[hintIndex]
			numOfHints += 1
	return numOfHints

def process( thisGlyph ):
	deletedHintsCount = 0
	for thisLayer in thisGlyph.layers:
		deletedHintsCount += deleteHintsInLayer( thisLayer )
	return deletedHintsCount

Font.disableUpdateInterface()

for thisGlyph in Font.glyphs:
	totalDeletedHints += process( thisGlyph )

Font.enableUpdateInterface()

print("Done: removed %i hints." % totalDeletedHints)
