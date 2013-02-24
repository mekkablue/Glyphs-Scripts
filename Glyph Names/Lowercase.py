#MenuTitle: Make glyph names lowercase
"""Makes the names of selected glyphs lowercase, useful for smallcap glyphs."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def process( thisGlyph ):
	oldName = thisGlyph.name
	newName = thisGlyph.name.lower()
	thisGlyph.name = newName
	print oldName, "-->", thisGlyph.name

Font.disableUpdateInterface()

for thisGlyph in selectedGlyphs:
	process( thisGlyph )

Font.enableUpdateInterface()

