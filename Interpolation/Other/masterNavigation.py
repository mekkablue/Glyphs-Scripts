# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from GlyphsApp import Glyphs

def showAllMastersOfGlyphInCurrentTab( thisGlyphName ):
	thisFont = Glyphs.font
	thisGlyph = thisFont.glyphs[thisGlyphName]
	if thisGlyph:
		thisTab = thisFont.currentTab
		if not thisTab:
			thisTab = thisFont.newTab()
		
		thisTab.layers = [l for l in thisGlyph.layers if l.isMasterLayer or l.isSpecialLayer]
		# thisTab.textCursor = 0
		thisTab.textRange = 0
	
def glyphNameForIndexOffset( indexOffset ):
	thisFont = Glyphs.font # frontmost font
	currentLayer = thisFont.selectedLayers[0]
	currentGlyph = currentLayer.parent
	glyphIndex = currentGlyph.glyphId()

	# open a new tab with the current glyph if opened from Font tab:
	if thisFont.currentTab:
		glyphIndex += indexOffset
	
	thisGlyph = thisFont.glyphs[ glyphIndex % len(thisFont.glyphs) ]
	if thisGlyph:
		return thisGlyph.name
	else:
		return None