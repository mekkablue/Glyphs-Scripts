#MenuTitle: Make glyph names lowercase
# -*- coding: utf-8 -*-
__doc__="""
Makes the names of selected glyphs lowercase, useful for smallcap glyphs.
"""

import GlyphsApp

Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

def process( thisGlyph ):
	oldName = thisGlyph.name
	newName = thisGlyph.name.lower()
	if oldName != newName:
		thisGlyph.name = newName
		print "%s --> %s" % (oldName, newName)
	else:
		print "%s: unchanged"

Font.disableUpdateInterface()

for thisGlyph in selectedGlyphs:
	process( thisGlyph )

Font.enableUpdateInterface()
