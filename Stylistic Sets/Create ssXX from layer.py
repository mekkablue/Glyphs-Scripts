#MenuTitle: Create .ssXX glyph from current layer
"""
Takes the currently opened layers and creates new glyphs with a .ssXX ending.
Checks if the name is free.
"""

import GlyphsApp

Doc = Glyphs.currentDocument
Font = Glyphs.font
FirstMasterID = Font.masters[0].id
allGlyphNames = [ x.name for x in Font.glyphs ]
selectedLayers = Doc.selectedLayers()

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
	Font.glyphs.append( targetGlyph )

	# copy original layer into first master of new glyph:
	layerCopy = sourceLayer.copy()
	targetGlyph.layers[ FirstMasterID ] = layerCopy
	print "Created", targetGlyphName 
	

for thisLayer in selectedLayers:
	process( thisLayer )

