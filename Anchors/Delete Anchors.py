#MenuTitle: Delete All Anchors
# -*- coding: utf-8 -*-
__doc__="""
Deletes all anchors in active layers of selected glyphs.
"""

import GlyphsApp

thisFont = Glyphs.font
selectedLayers = thisFont.selectedLayers

print "Deleting anchors in:"

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "-- %s" % thisGlyph.name
	thisGlyph.beginUndo()
	thisLayer.setAnchors_( None )
	thisGlyph.endUndo()
