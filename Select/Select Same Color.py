#MenuTitle: Select Same Color
# -*- coding: utf-8 -*-
__doc__="""
In Font view, select glyphs with the same color(s) as the currently selected one(s).
"""

import GlyphsApp

def indexSetWithIndex( index ):
	indexSet = NSIndexSet.alloc().initWithIndex_( index )
	return indexSet

thisFont = Glyphs.font # frontmost font
fontView = thisDoc.windowController().tabBarControl().viewControllers()[0].glyphsArrayController()
displayedGlyphsInFontView = fontView.arrangedObjects() # all glyphs currently displayed
colorIndexes = []

if displayedGlyphsInFontView:
	displayedIndexRange = range(len(displayedGlyphsInFontView)) # indexes of glyphs in Font view
	for i in displayedIndexRange:
		if fontView.selectionIndexes().containsIndex_(i):
			thisGlyphColorIndex = displayedGlyphsInFontView[i].colorIndex()
			if not thisGlyphColorIndex in colorIndexes:
				colorIndexes.append( thisGlyphColorIndex )
	if colorIndexes:
		for i in displayedIndexRange:
			if displayedGlyphsInFontView[i].colorIndex() in colorIndexes:
				fontView.addSelectionIndexes_( indexSetWithIndex(i) )

