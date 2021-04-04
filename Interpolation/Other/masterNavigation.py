# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from GlyphsApp import Glyphs, GSControlLayer

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

def showAllMastersOfGlyphs( glyphNames, openNewTab=True, avoidDuplicates=True ):
	if avoidDuplicates:
		glyphNamesSet = []
		[glyphNamesSet.append(g) for g in glyphNames if not g in glyphNamesSet]
		glyphNames = glyphNamesSet
	
	thisFont = Glyphs.font
	thisTab = thisFont.currentTab
	if openNewTab or not thisTab:
		thisTab = thisFont.newTab()
	thisTab.textRange = 0
	
	displayLayers = []
	for thisGlyphName in glyphNames:
		thisGlyph = thisFont.glyphs[thisGlyphName]
		if thisGlyph:
			displayLayers += [l for l in thisGlyph.layers if l.isMasterLayer or l.isSpecialLayer]
			displayLayers.append(GSControlLayer.newline())
	
	if len(displayLayers) > 1:
		displayLayers.pop(-1) # remove last newline
	
	thisTab.layers = displayLayers
	
	
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