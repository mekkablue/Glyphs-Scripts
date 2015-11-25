#MenuTitle: Create .ssXX glyph from current layer
# -*- coding: utf-8 -*-
__doc__="""
Takes the currently opened layers and creates new glyphs with a .ssXX ending. Checks if the name is free.
"""

import GlyphsApp

thisFont = Glyphs.font
allGlyphNames = [ x.name for x in thisFont.glyphs ]
selectedLayers = thisFont.selectedLayers

def findSuffix( glyphName ):
	nameIsFree = False
	ssNumber = 0
	
	while nameIsFree is False:
		ssNumber += 1
		targetSuffix = ".ss%.2d" % ssNumber
		targetGlyphName = glyphName + targetSuffix
		if allGlyphNames.count( targetGlyphName ) == 0:
			nameIsFree = True

	return targetSuffix
	
def process( sourceLayer ):
	# find suffix
	sourceGlyphName = sourceLayer.parent.name
	targetSuffix = findSuffix( sourceGlyphName )
	
	# append suffix, create glyph:
	targetGlyphName = sourceGlyphName + targetSuffix
	targetGlyph = GSGlyph( targetGlyphName )
	thisFont.glyphs.append( targetGlyph )

	# copy original layer into respective master of new glyph:
	masterID = sourceLayer.associatedMasterId
	layerCopy = sourceLayer.copy()
	targetGlyph.layers[ masterID ] = layerCopy
	print "Created %s" % targetGlyphName

for thisLayer in selectedLayers:
	process( thisLayer )

