#MenuTitle: Delete All Anchors
# -*- coding: utf-8 -*-
__doc__="""
Deletes all anchors in active layers of selected glyphs.
"""

import GlyphsApp

Font = Glyphs.font

print "Deleting anchors in:"

for thisLayer in Font.selectedLayers:
	print "-- %s" % thisLayer.parent.name
	thisLayer.setAnchors_( None )
