#MenuTitle: Delete Hints
"""Delete all hints in selected glyphs."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def process( thisGlyph ):
	for thisLayer in thisGlyph.layers:
		for x in reversed(range(len(thisLayer.hints))):
			del thisLayer.hints[x]
		
Font.disableUpdateInterface()

for thisGlyph in selectedGlyphs:
	print "Processing", thisGlyph.name
	process( thisGlyph )

Font.enableUpdateInterface()
