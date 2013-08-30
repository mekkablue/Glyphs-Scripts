#MenuTitle: Keep First Master Hints Only
"""In selected glyphs, delete all hints in all layers except for the first master. Respects Bracket Layers."""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers
selectedGlyphs = [ l.parent for l in selectedLayers ]
firstMasterId = Font.masters[0].id

print "Only keeping first master hints:"

for thisGlyph in selectedGlyphs:
	print "Processing", thisGlyph.name
	layersToBeProcessed = [ l for l in thisGlyph.layers if l.associatedMasterId != firstMasterId ]
	thisGlyph.beginUndo()
	for thisLayer in layersToBeProcessed:
		thisLayer.hints = None
	thisGlyph.endUndo()
print "Done."