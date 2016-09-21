#MenuTitle: Make glyph names lowercase
# -*- coding: utf-8 -*-
__doc__="""
Makes the names of selected glyphs lowercase, useful for smallcap glyphs.
"""

Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

def lowercaseGlyphName( thisGlyph ):
	oldName = thisGlyph.name
	if "." in oldName:
		dotPosition = oldName.find(".")
		newName = oldName[:dotPosition].lower() + oldName[dotPosition:]
	else:
		newName = oldName.lower()
	if oldName != newName:
		thisGlyph.name = newName
		print "%s --> %s" % (oldName, newName)
	else:
		print "%s: unchanged"

Font.disableUpdateInterface()

for thisGlyph in selectedGlyphs:
	lowercaseGlyphName( thisGlyph )

Font.enableUpdateInterface()
