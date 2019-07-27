#MenuTitle: Replicate Anchors in Suffixed Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Goes through your selected, dot-suffixed glyphs and copies the anchors and anchor positions of the base glyph into them. E.g. A.ss01 will have the same anchor positions as A.
"""

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
		thisAnchor = baseAnchor.copy()
		thisLayer.anchors[ str(thisAnchor.name) ] = thisAnchor
		print "   Added %s (%i, %i)" % ( thisAnchor.name, thisAnchor.x, thisAnchor.y )

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

