#MenuTitle: New Edit tab with Bracket Layer glyphs
# -*- coding: utf-8 -*-
"""Opens a new Edit tab with all glyphs which contain the Bracket Layer trick."""

import GlyphsApp

Font = Glyphs.font
editString = ""
for thisGlyph in Font.glyphs:
	if "[" in "".join([ l.name for l in thisGlyph.layers ]):
		editString += ( "/" + thisGlyph.name )

Glyphs.currentDocument.windowController().addTabWithString_( editString )
