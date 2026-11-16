# MenuTitle: New Tab with Glyphs of Same Kerning Groups
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Opens a new tab containing all members of the left and right kerning groups of the current glyph.
"""

from GlyphsApp import Glyphs, Message

thisFont = Glyphs.font  # frontmost font
thisGlyph = thisFont.selectedLayers[0].parent if thisFont and thisFont.selectedLayers else None

if thisGlyph:
	leftGroup = thisGlyph.leftKerningGroup
	rightGroup = thisGlyph.rightKerningGroup

	leftGroupText = "left:\n"
	rightGroupText = "right:\n"

	for g in thisFont.glyphs:
		# glyphs without a group only stand for themselves:
		if (leftGroup and g.leftKerningGroup == leftGroup) or (not leftGroup and g.name == thisGlyph.name):
			leftGroupText += "/%s" % g.name
		if (rightGroup and g.rightKerningGroup == rightGroup) or (not rightGroup and g.name == thisGlyph.name):
			rightGroupText += "/%s" % g.name

	thisFont.newTab("%s %s\n\n%s %s" % (thisGlyph.name, leftGroupText, thisGlyph.name, rightGroupText))
else:
	Message(title="Script Error", message="No glyph currently selected.", OKButton=None)
