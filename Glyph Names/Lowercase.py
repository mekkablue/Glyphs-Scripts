#MenuTitle: Make glyph names lowercase
"""Makes the names of selected glyphs lowercase, useful for smallcap glyphs."""

import GlyphsApp

Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
FontMaster = Doc.selectedFontMaster()
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def process( thisGlyph ):
	oldName = thisGlyph.name
	newName = thisGlyph.name.lower()
	thisGlyph.name = newName
	print oldName, "-->", thisGlyph.name

Font.willChangeValueForKey_("glyphs")

for thisGlyph in selectedGlyphs:
	process( thisGlyph )

Font.didChangeValueForKey_("glyphs")

