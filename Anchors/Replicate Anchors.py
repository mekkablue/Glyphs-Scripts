#MenuTitle: Replicate anchors in suffixed glyphs
# -*- coding: utf-8 -*-
"""Goes through your selected, dot-suffixed glyphs and copies the anchors and anchor positions of the base glyph into them. E.g. A.ss01 will have the same anchor positions as A."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = [ l for l in Font.selectedLayers if "." in l.parent.name ]

def process( thisLayer ):
	thisGlyphName = thisLayer.parent.name
	baseGlyphName = thisGlyphName[:thisGlyphName.find(".")]
	baseGlyph = Font.glyphs[ baseGlyphName ]
	baseLayer = baseGlyph.layers[ FontMaster.id ]
	
	print "%s <-- %s" % ( thisGlyphName, baseGlyphName )
	
	for baseAnchor in baseLayer.anchors:
		thisAnchorPosition = NSPoint()
		thisAnchorPosition.x = baseAnchor.x
		thisAnchorPosition.y = baseAnchor.y
		
		thisAnchorName = baseAnchor.name
		
		thisAnchor = GSAnchor( thisAnchorName, thisAnchorPosition )
		thisLayer.addAnchor_( thisAnchor )
		
		print "-- Added %s (%i, %i)" % ( thisAnchorName, thisAnchorPosition.x, thisAnchorPosition.y )
		

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

