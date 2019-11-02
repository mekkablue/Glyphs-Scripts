#MenuTitle: Create .ssXX glyph from current layer
# -*- coding: utf-8 -*-
__doc__="""
Takes the currently opened layers and creates new glyphs with the first available .ssXX ending. It marks the new glyph blue, and (in a multiple-master file) all other, unprocessed master layers orange.
"""

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
	sourceGlyph = sourceLayer.parent
	sourceGlyphName = sourceGlyph.name
	targetSuffix = findSuffix( sourceGlyphName )
	
	# append suffix, create glyph:
	targetGlyphName = sourceGlyphName + targetSuffix
	targetGlyph = GSGlyph( targetGlyphName )
	thisFont.glyphs.append( targetGlyph )
	targetGlyph.setColorIndex_(6)

	# copy original layer into respective master of new glyph:
	sourceMasterID = sourceLayer.associatedMasterId
	layerCopy = sourceLayer.copy()
	targetGlyph.layers[ sourceMasterID ] = layerCopy
	
	# copy other master layers into target layers:
	for thisMasterID in [m.id for m in thisFont.masters if m.id != sourceMasterID]:
		targetGlyph.layers[ thisMasterID ] = sourceGlyph.layers[ thisMasterID ].copy()
		targetGlyph.layers[ thisMasterID ].setColorIndex_(1)
	
	# add new glyph to tab:
	thisFont.currentText += "/%s" % targetGlyphName
	
	print "Created %s" % targetGlyphName

for thisLayer in selectedLayers:
	process( thisLayer )

