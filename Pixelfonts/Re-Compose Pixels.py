#MenuTitle: Re-compose pixels
# -*- coding: utf-8 -*-
__doc__="""
Looks for decomposed pixels and puts 'pixel' components back in their place.
"""

pixelGlyphName = "pixel"

import GlyphsApp

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	for originPoint in set( [ (p.bounds.origin.x, p.bounds.origin.y) for p in thisLayer.paths ] ):
		x, y = originPoint[0], originPoint[1]
		newComponent = GSComponent( pixelGlyphName, NSPoint( x, y ) )
		thisLayer.components.append( newComponent )
		
	countOfPaths = len( thisLayer.paths )
	for x in range( countOfPaths )[::-1]:
		del thisLayer.paths[x]

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
