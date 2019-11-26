#MenuTitle: New Tab with all Group Members
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Select two glyphs, e.g. ‘Ta’, run the script, it will give you a new tab with all combinations of the ‘T’ kerning group with the ‘a’ kerning group.
"""

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs
tabString = ""

if len(listOfSelectedLayers) > 1:
	firstGlyph = listOfSelectedLayers[0].parent
	firstGroup = firstGlyph.rightKerningGroup
	
	secondGlyph = listOfSelectedLayers[1].parent
	secondGroup = secondGlyph.leftKerningGroup
	
	firstGlyphNames = [g.name for g in thisFont.glyphs if g.rightKerningGroup == firstGroup]
	secondGlyphNames = [g.name for g in thisFont.glyphs if g.leftKerningGroup == secondGroup]
	
	for firstGlyphName in firstGlyphNames:
		for secondGlyphName in secondGlyphNames:
			thisPair = "/%s/%s/space" % ( firstGlyphName, secondGlyphName )
			tabString += thisPair
		tabString = tabString.strip() + "\n"
	
	tabString = tabString.strip()
	if tabString:
		# opens new Edit tab:
		from PyObjCTools.AppHelper import callAfter
		callAfter( Glyphs.currentDocument.windowController().addTabWithString_, tabString )
		