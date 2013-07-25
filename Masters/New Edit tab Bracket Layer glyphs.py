#MenuTitle: New Edit tab with Bracket Layer glyphs
# -*- coding: utf-8 -*-
"""Opens a new Edit tab with all glyphs which contain the Bracket Layer trick."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font

Font.disableUpdateInterface()

editString = ""
print "Looking for bracket layers ..."

for thisGlyph in Font.glyphs:
	if "[" in "".join([ l.name for l in thisGlyph.layers ]):
		editString += ( "/" + thisGlyph.name )

Doc.windowController().addTabWithString_( editString )

Font.enableUpdateInterface()
