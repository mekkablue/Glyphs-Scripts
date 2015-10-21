#MenuTitle: Delete All Components
# -*- coding: utf-8 -*-
__doc__="""
Deletes all components in selected glyphs.
"""

import GlyphsApp

thisFont = Glyphs.font
selectedLayers = thisFont.selectedLayers

def process( thisLayer ):
	if len( thisLayer.components ) > 0:
		listOfComponentNames = ", ".join( [c.componentName for c in thisLayer.components] )
		print "-- Deleted components: %s" % listOfComponentNames
		thisLayer.components = []

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()
