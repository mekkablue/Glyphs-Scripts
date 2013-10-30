#MenuTitle: Delete all components
"""Deletes all components in selected glyphs."""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	while len(thisLayer.components) > 0:
		print "-- Deleting component %s" % thisLayer.components[0].componentName
		del thisLayer.components[0]

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
