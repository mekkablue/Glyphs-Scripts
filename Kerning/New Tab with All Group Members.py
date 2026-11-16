# MenuTitle: New Tab with All Group Members
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Select two glyphs, e.g. ‘Ta’ (or place your cursor between them), run the script, it will give you a new tab with all combinations of the ‘T’ kerning group with the ‘a’ kerning group.
"""

from GlyphsApp import Glyphs, Message

thisFont = Glyphs.font  # frontmost font
tab = thisFont.currentTab if thisFont else None
tabString = ""
listOfSelectedLayers = thisFont.selectedLayers if thisFont else []
firstGlyph, secondGlyph = None, None

if len(listOfSelectedLayers) == 2:
	firstGlyph = listOfSelectedLayers[0].parent
	secondGlyph = listOfSelectedLayers[1].parent
elif tab and tab.textRange == 0:
	cursorPosition = tab.layersCursor
	if 0 < cursorPosition < len(tab.layers):
		firstGlyph = tab.layers[cursorPosition - 1].parent
		secondGlyph = tab.layers[cursorPosition].parent

if firstGlyph and secondGlyph:
	firstGroup = firstGlyph.rightKerningGroup
	secondGroup = secondGlyph.leftKerningGroup

	# glyphs without a group only stand for themselves:
	if firstGroup:
		firstGlyphNames = [g.name for g in thisFont.glyphs if g.rightKerningGroup == firstGroup]
	else:
		firstGlyphNames = [firstGlyph.name]
	if secondGroup:
		secondGlyphNames = [g.name for g in thisFont.glyphs if g.leftKerningGroup == secondGroup]
	else:
		secondGlyphNames = [secondGlyph.name]

	for firstGlyphName in firstGlyphNames:
		for secondGlyphName in secondGlyphNames:
			thisPair = "/%s/%s/space" % (firstGlyphName, secondGlyphName)
			tabString += thisPair
		tabString = tabString.strip() + "\n"

	tabString = tabString.strip()
	if tabString:
		# opens new Edit tab:
		thisFont.newTab(tabString)
else:
	Message(
		title="Invalid Glyph Selection",
		message="This script needs exactly two glyphs selected, it will use the right kerning group of the left glyph, and vice versa. Select two glyphs and try again.",
		OKButton=None
	)
