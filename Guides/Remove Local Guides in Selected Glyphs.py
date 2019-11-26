from __future__ import print_function
#MenuTitle: Remove Local Guides in Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Delete all local (blue) guides in selected glyphs.
"""

print("Deleting guides in:")

for thisLayer in Glyphs.font.selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	thisLayer.guideLines = None
	thisGlyph.endUndo()
	print("  %s" % thisGlyph.name)
