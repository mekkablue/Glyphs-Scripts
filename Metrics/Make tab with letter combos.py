#MenuTitle: Make Tab with letter combos
# -*- coding: utf-8 -*-
"""Opens a new tab with all possible combinations of the selected glyphs."""

import GlyphsApp

Doc = Glyphs.currentDocument
Font = Glyphs.font
selectedLayers = Font.selectedLayers

namesOfSelectedGlyphs = ["/" + l.parent.name for l in selectedLayers]
editString = ""

for leftGlyphName in namesOfSelectedGlyphs:
	for rightGlyphName in namesOfSelectedGlyphs:
		editString += ( leftGlyphName + rightGlyphName + "/space" )

Doc.windowController().addTabWithString_( editString[:-1] )
