#MenuTitle: New Edit tab with Bracket Layer glyphs
# -*- coding: utf-8 -*-
"""Opens a new Edit tab with all glyphs which contain the Bracket Layer trick."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font

editString = ""
print "Looking for bracket layers ..."

for thisGlyph in Font.glyphs:
	if "[" in "".join([ l.name for l in thisGlyph.layers ]):
		editString += ( "/" + thisGlyph.name )

Doc.windowController().performSelectorOnMainThread_withObject_waitUntilDone_("addTabWithString:", editString, True)


