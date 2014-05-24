#MenuTitle: New Tab with Bracket Layer Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Opens a new Edit tab with all glyphs which contain the Bracket Layer trick.
"""

import GlyphsApp
from PyObjCTools.AppHelper import callAfter

Font = Glyphs.font
editString = ""
for thisGlyph in Font.glyphs:
	if "[" in "".join([ l.name for l in thisGlyph.layers ]):
		editString += ( "/" + thisGlyph.name )

callAfter( Glyphs.currentDocument.windowController().addTabWithString_, editString )
