#MenuTitle: Remove Local Guides in Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

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
