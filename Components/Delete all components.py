#MenuTitle: Delete all components
"""Deletes all components in selected glyphs."""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	if len( thisLayer.components ) > 0:
		print "-- Deleted components: %s" % ", ".join( [c.componentName for c in thisLayer.components] )
		thisLayer.components = []

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()
