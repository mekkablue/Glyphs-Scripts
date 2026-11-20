# MenuTitle: Set TT Stem Hints to No Stem
# -*- coding: utf-8 -*-
__doc__ = """
Sets all TT stem hints to ‘no stem’ in selected glyphs. In complex paths, it can improve rendering on Windows.
"""

from GlyphsApp import Glyphs, TTSTEM

thisFont = Glyphs.font  # frontmost font


def process(thisLayer):
	returnValue = False
	for thisHint in thisLayer.hints:
		if thisHint.type == TTSTEM:
			thisHint.setStem_(-1)
			returnValue = True
	return returnValue


if thisFont is None:
	print("⚠️ No font open.")
else:
	listOfSelectedLayers = thisFont.selectedLayers  # active layers of selected glyphs
	for thisLayer in listOfSelectedLayers:
		thisGlyph = thisLayer.parent
		# thisGlyph.beginUndo()  # undo grouping causes crashes
		if process(thisLayer):
			print("%s: OK." % thisGlyph.name)
		else:
			print("%s: no TT stems found." % thisGlyph.name)
		# thisGlyph.endUndo()  # undo grouping causes crashes
