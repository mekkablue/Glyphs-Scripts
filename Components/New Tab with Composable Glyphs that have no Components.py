#MenuTitle: New Tab with Composable Glyphs that have no Components
# -*- coding: utf-8 -*-
__doc__="""
Opens a new Edit tab containing all glyphs that consist of paths, but could be composed according to Glyph Data.
"""

Glyphs.clearLog() # clears log of Macro window
thisFont = Glyphs.font # frontmost font
affectedGlyphNames = []
for thisGlyph in thisFont.glyphs: # loop through all glyphs
	if not thisGlyph.layers[0].components:
		info = thisGlyph.glyphInfo
		if info and info.components:
			print "%s: %s" % (thisGlyph.name, ", ".join([c.name for c in info.components]))
			affectedGlyphNames.append(thisGlyph.name)
			

# open a new tab with the affected glyphs:
if affectedGlyphNames:
	tabString = "/" + "/".join(affectedGlyphNames)
	thisFont.newTab( tabString )

# otherwise send a message:
else:
	Message(
		title = "Nothing Found",
		message = "Could not find any composable glyphs that consist of paths.",
		OKButton = None
	)
	
