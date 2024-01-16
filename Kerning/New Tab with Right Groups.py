# MenuTitle: New Tab with Right Groups
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates a new tab with one glyph of each right group. Useful for checking the constency of right kerning groups.
"""
from PyObjCTools.AppHelper import callAfter
from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font
thisFontMaster = thisFont.selectedFontMaster  # active master
listOfSelectedLayers = thisFont.selectedLayers  # active layers of selected glyphs

groupDict = {}

for thisGlyph in thisFont.glyphs:
	glyphName = thisGlyph.name
	rGroup = thisGlyph.rightKerningGroup
	if rGroup in groupDict.keys():
		groupDict[rGroup].append(glyphName)
	else:
		groupDict[rGroup] = [glyphName]

tabString = ""

for thisRightGroup in groupDict.keys():
	tabString += "/%s/space\n" % "/".join(groupDict[thisRightGroup])

# opens new Edit tab:
callAfter(Glyphs.currentDocument.windowController().addTabWithString_, tabString)
