#MenuTitle: Delete All Vertical Hints in Font
# -*- coding: utf-8 -*-
__doc__="""
Removes all vertical hints in the font.
"""

import GlyphsApp


thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master



def process( thisLayer ):
	numberOfHints = len(thisLayer.hints)
	for i in range(numberOfHints)[::-1]:
		thisHint = thisLayer.hints[i]
		if not thisHint.horizontal:
			del thisLayer.hints[i]
			

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisGlyph in thisFont.glyphs:
	thisGlyph.beginUndo() # begin undo grouping
	for thisLayer in thisGlyph.layers:
		process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
