#MenuTitle: New Tab with all Group Members
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Select two glyphs, e.g. ‘Ta’ (or place your cursor between them), run the script, it will give you a new tab with all combinations of the ‘T’ kerning group with the ‘a’ kerning group.
"""

thisFont = Glyphs.font # frontmost font
tab = thisFont.currentTab
tabString = ""
listOfSelectedLayers = thisFont.selectedLayers
firstGlyph, secondGlyph = None, None

if len(listOfSelectedLayers) == 2:
	firstGlyph = listOfSelectedLayers[0].parent
	secondGlyph = listOfSelectedLayers[1].parent
elif tab and tab.textRange == 0:
	cursorPosition = tab.layersCursor
	if cursorPosition > 0:
		firstGlyph = tab.layers[cursorPosition - 1].parent
		secondGlyph = tab.layers[cursorPosition].parent

if firstGlyph and secondGlyph:
	firstGroup = firstGlyph.rightKerningGroup
	secondGroup = secondGlyph.leftKerningGroup

	firstGlyphNames = [g.name for g in thisFont.glyphs if g.rightKerningGroup == firstGroup]
	secondGlyphNames = [g.name for g in thisFont.glyphs if g.leftKerningGroup == secondGroup]

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
