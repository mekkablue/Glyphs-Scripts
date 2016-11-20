#MenuTitle: New Tab with Glyphs of Same Kerning Groups
# -*- coding: utf-8 -*-
__doc__="""
Opens a new tab containing all members of the left and right kerning groups of the current glyph.
"""

import GlyphsApp

thisFont = Glyphs.font # frontmost font
thisGlyph = Font.selectedLayers[0].parent

if thisGlyph:
	leftGroup = thisGlyph.leftKerningGroup
	rightGroup = thisGlyph.rightKerningGroup

	leftGroupText = "left:\n"
	rightGroupText = "right:\n"

	for g in thisFont.glyphs:
		if g.leftKerningGroup == leftGroup:
			leftGroupText += "/%s" % g.name
		if g.rightKerningGroup == rightGroup:
			rightGroupText += "/%s" % g.name

	Font.newTab( "%s %s\n\n%s %s" % ( thisGlyph.name, leftGroupText, thisGlyph.name, rightGroupText ) )
else:
	Message("Script Error", "No glyph currently selected.", OKButton=None)