# MenuTitle: Reset Alternate Glyph Widths
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Sets the width of selected .ss01 (or any other extension) widths in the font to the width of their base glyphs. E.g. A.ss01 will have the same width as A.
"""

from GlyphsApp import Glyphs, Message

Font = Glyphs.font


def resetWidth(thisLayer, thisName):
	if thisLayer is None:
		print("> couldn't get layer of <%s> " % thisName)
		return
	baseGlyphName = thisName[:thisName.find(".")]
	baseGlyph = Font.glyphs[baseGlyphName]
	if baseGlyph is None:
		print("> couldn't find a base glyph for <%s> " % thisName)
		return
	baseLayer = baseGlyph.layers[FontMaster.id]
	baseWidth = baseLayer.width
	thisLayer.width = baseWidth
	return baseWidth


if Font:
	selectedLayers = Font.selectedLayers
	FontMaster = Font.selectedFontMaster
	Font.disableUpdateInterface()
	try:
		for thisLayer in selectedLayers:
			thisGlyph = thisLayer.parent
			thisGlyphName = thisGlyph.name
			if "." in thisGlyphName:
				thisLayer.parent.beginUndo()  # undo grouping causes crashes
				try:
					print("Resetting width of %s to %.0f." % (thisGlyphName, resetWidth(thisLayer, thisGlyphName)))
				except:
					print("> ERROR, couldn't reset <%s>" % (thisGlyphName))
				thisLayer.parent.endUndo()  # undo grouping causes crashes

	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ Script Error:\n")
		import traceback
		print(traceback.format_exc())
		print()
		raise e

	finally:
		Font.enableUpdateInterface()  # re-enables UI updates in Font View
else:
	Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
