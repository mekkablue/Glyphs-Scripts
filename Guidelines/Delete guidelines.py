#MenuTitle: Delete Local Guidelines
# -*- coding: utf-8 -*-
__doc__="""
Delete all local guidelines in selected glyphs.
"""

import GlyphsApp

print "Deleting guidelines in:"

for thisLayer in Glyphs.font.selectedLayers:
	thisGlyph = thisLayer.parent
	# delete guidelines:
	thisGlyph.beginUndo()
	thisLayer.guideLines = []
	thisGlyph.endUndo()
	
	# report glyph name:
	print "  %s" % thisGlyph.name
