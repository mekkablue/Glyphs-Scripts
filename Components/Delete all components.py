#MenuTitle: Delete components
"""Delete Components for selected glyphs."""

import GlyphsApp

Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
FontMaster = Doc.selectedFontMaster()
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def process( thisGlyph ):
	thisLayer = thisGlyph.layers[FontMaster.id]

	while len(thisLayer.components) > 0:
		del thisLayer.components[0]

for thisGlyph in selectedGlyphs:
	print "Processing", thisGlyph.name
	process( thisGlyph )
