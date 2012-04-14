#MenuTitle: Delete Hints
"""Delete all hints in selected glyphs."""

import GlyphsApp

Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
FontMaster = Doc.selectedFontMaster()
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def process( thisGlyph ):
	for thisLayer in thisGlyph.layers:
		for x in reversed(range(len(thisLayer.hints))):
			del thisLayer.hints[x]
		
Font.willChangeValueForKey_("glyphs")

for thisGlyph in selectedGlyphs:
	print "Processing", thisGlyph.name
	process( thisGlyph )

Font.didChangeValueForKey_("glyphs")

