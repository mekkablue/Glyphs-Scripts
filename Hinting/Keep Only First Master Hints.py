#MenuTitle: Keep First Master Hints Only
# -*- coding: utf-8 -*-
__doc__="""
In selected glyphs, delete all hints in all layers except for the first master. Respects Bracket Layers.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers
selectedGlyphs = [ l.parent for l in selectedLayers ]
firstMasterName = Font.masters[0].name

Glyphs.clearLog()
print "Only keeping first-master hints in:"

for thisGlyph in selectedGlyphs:
	print "- %s" % thisGlyph.name
	layersToBeProcessed = [ l for l in thisGlyph.layers if not l.name.startswith( firstMasterName ) ]
	for thisLayer in layersToBeProcessed:
		thisLayer.hints = None

print "Done."