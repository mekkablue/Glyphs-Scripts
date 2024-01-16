# MenuTitle: New Tab with Selected Glyph Combinations
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Opens a new tab with all possible combinations of currently selected glyphs.
"""

from GlyphsApp import Glyphs

Font = Glyphs.font
selectedLayers = Font.selectedLayers

namesOfSelectedGlyphs = ["/%s" % layer.parent.name for layer in selectedLayers if hasattr(layer.parent, 'name')]
editString = ""

for leftGlyphName in namesOfSelectedGlyphs:
	for rightGlyphName in namesOfSelectedGlyphs:
		newPair = leftGlyphName + rightGlyphName
		if newPair not in editString:
			editString += newPair
	editString += (leftGlyphName + "\n")

# in case last line fails, the text is in the macro window:
Glyphs.clearLog()  # clears macro window log
print(editString)

# opens new Edit tab:
Font.newTab(editString)
