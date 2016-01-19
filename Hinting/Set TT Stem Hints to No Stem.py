#MenuTitle: Set TT Stem Hints to No Stem
# -*- coding: utf-8 -*-
__doc__="""
Sets all TT stem hints to ‘no stem’ in selected glyphs. In complex paths, it can improve rendering on Windows.
"""

import GlyphsApp

thisFont = Glyphs.font # frontmost font
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisLayer ):
	returnValue = False
	for thisHint in thisLayer.hints:
		if thisHint.type == TTSTEM:
			thisHint.setStem_(-1)
			returnValue = True
	return returnValue

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo() # begin undo grouping
	if process( thisLayer ):
		print "%s: OK." % thisGlyph.name
	else:
		print "%s: no TT stems found." % thisGlyph.name
	thisGlyph.endUndo() # end undo grouping
