# MenuTitle: Set TT Stem Hints to Auto
# -*- coding: utf-8 -*-
__doc__ = """
Sets all TT stem hints to ‘Auto’ in selected glyphs.
"""

from Foundation import NSNotFound
from GlyphsApp import Glyphs, TTSTEM

thisFont = Glyphs.font  # frontmost font


def process(thisLayer):
	returnValue = False
	for thisHint in thisLayer.hints:
		if thisHint.type == TTSTEM:
			thisHint.setStem_(NSNotFound)
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
