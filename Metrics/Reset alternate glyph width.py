#MenuTitle: Reset alternate glyph widths
# -*- coding: utf-8 -*-
"""Sets the width of selected .ss01 (or any other extension) widths in the font to the width of their base glyphs. E.g. A.ss01 will have the same width as A."""

import GlyphsApp
Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedLayers = Font.selectedLayers

def resetWidth( thisLayer, thisName ):
	baseGlyphName = thisName[:thisName.find(".")]
	baseGlyph = Font.glyphs[ baseGlyphName ]
	baseLayer = baseGlyph.layers[ thisLayer.associatedMasterId ]
	baseWidth = baseLayer.width
	thisLayer.width = baseWidth
	return baseWidth

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyphName = thisGlyph.name
	if "." in thisGlyphName:
		thisGlyph.beginUndo()
		thisLayer.setDisableUpdates()
		print "Resetting width of %s to %.0f." % ( thisGlyphName, resetWidth( thisLayer, thisGlyphName ) )
		thisLayer.setEnableUpdates()
		thisGlyph.endUndo()

