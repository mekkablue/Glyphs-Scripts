#MenuTitle: Remove Local Guides in Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Delete all local (blue) guides in selected glyphs.
"""

print("Deleting guides in:")

for thisLayer in Glyphs.font.selectedLayers:
	thisGlyph = thisLayer.parent
	# thisGlyph.beginUndo() # undo grouping causes crashes
	thisLayer.guideLines = None
	# thisGlyph.endUndo() # undo grouping causes crashes
	print("  %s" % thisGlyph.name)
