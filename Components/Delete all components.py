#MenuTitle: Delete all components
"""Deletes all components in selected glyphs."""

import GlyphsApp

Doc  = Glyphs.currentDocument
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	while len(thisLayer.components) > 0:
		print "  Deleting component", thisLayer.components[0].componentName
		del thisLayer.components[0]

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()
