#MenuTitle: Re-compose pixels
"""Looks for decomposed pixels and puts 'pixel' components back in their place."""

pixelGlyphName = "pixel"

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
FontMaster = Doc.selectedFontMaster()
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		originPoint = thisPath.bounds[0]
		newComponent = GSComponent( pixelGlyphName, originPoint )
		thisLayer.components.append( newComponent )
	
	countOfPaths = len( thisLayer.paths )
	for x in range( countOfPaths )[::-1]:
		del thisLayer.paths[x]

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.undoManager().beginUndoGrouping()
	process( thisLayer )
	thisGlyph.undoManager().endUndoGrouping()

Font.enableUpdateInterface()
