#MenuTitle: New Tab with Brace Layer Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Opens a new Edit tab with all glyphs which contain the Brace Layer trick.
"""



Font = Glyphs.font
editString = ""
for thisGlyph in Font.glyphs:
	allLayerNames = " ".join([ l.name for l in thisGlyph.layers if l.name ])
	if "{" in allLayerNames and "}" in allLayerNames:
		editString += ( "/" + thisGlyph.name )

# opens new Edit tab:
try:
	Font.newTab( editString )
except:
	# backwards compatibility
	from PyObjCTools.AppHelper import callAfter
	callAfter( Glyphs.currentDocument.windowController().addTabWithString_, editString )
