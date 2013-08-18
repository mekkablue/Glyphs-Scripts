#MenuTitle: Keep First Master Hints Only
"""In selected glyphs, delete all hints in all layers except for the first master. Respects Bracket Layers."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedLayers = Doc.selectedLayers()
selectedGlyphs = [ l.parent for l in selectedLayers ]
firstMasterName = Font.masters[0].name

print "Only keeping first master hints:"

def removeHints( thisLayer ):
	for x in reversed( range( len( thisLayer.hints ))):
		del thisLayer.hints[x]
		
Font.disableUpdateInterface()

for thisGlyph in selectedGlyphs:
	print "Processing", thisGlyph.name
	layersToBeProcessed = [ l for l in thisGlyph.layers if not l.name.startswith( firstMasterName ) ]

	for thisLayer in layersToBeProcessed:
		removeHints( thisLayer )

Font.enableUpdateInterface()

print "Done."