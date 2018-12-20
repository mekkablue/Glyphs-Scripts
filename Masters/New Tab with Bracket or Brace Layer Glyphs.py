#MenuTitle: New Tab with Bracket or Brace Layer Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Opens a new Edit tab with all glyphs which contain the Bracket or Brace Layer trick.
"""

import GlyphsApp
from PyObjCTools.AppHelper import callAfter

Font = Glyphs.font
editString = ""
for thisGlyph in Font.glyphs:
	# any(x is None for x in [thisGlyph.leftMetricsKey, thisGlyph.rightMetricsKey])
	stringOfLayerNames = "".join([ l.name for l in thisGlyph.layers if l.name != None])
	if any (x is True for x in ["[" in stringOfLayerNames, "]" in stringOfLayerNames, "{" in stringOfLayerNames, "}" in stringOfLayerNames] ):
		editString += ( "/" + thisGlyph.name )

callAfter( Glyphs.currentDocument.windowController().addTabWithString_, editString )
