#MenuTitle: Make glyph names lowercase
"""Makes the names of selected glyphs lowercase, useful for smallcap glyphs."""

import GlyphsApp

Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

def process( thisGlyph ):
	oldName = thisGlyph.name
	newName = thisGlyph.name.lower()
	thisGlyph.name = newName
	print oldName, "-->", thisGlyph.name

Font.disableUpdateInterface() # this is a cse where the font.disableUpdateInterface makes sense

for thisGlyph in selectedGlyphs:
	process( thisGlyph )

Font.enableUpdateInterface()

