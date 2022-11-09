#MenuTitle: Build APL Greek
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Create APL Greek glyphs.
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
aplGlyphNames = ("APLiota", "APLrho", "APLomega", "APLalpha")
Glyphs.clearLog()

for glyphName in aplGlyphNames:
	original = glyphName.replace("APL", "")
	if thisFont.glyphs[original]:
		thisGlyph = Font.glyphs[glyphName]
		if not thisGlyph:
			thisGlyph = GSGlyph()
			thisGlyph.name = glyphName
			thisFont.glyphs.append(thisGlyph)

		for thisLayer in thisGlyph.layers:
			thisLayer.clear()
			comp = GSComponent(original)
			thisLayer.components.append(comp)
			comp.automaticAlignment = True
	else:
		print("%s: not found in font." % original)
		Glyphs.showMacroWindow()
