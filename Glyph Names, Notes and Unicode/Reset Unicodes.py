# MenuTitle: Reset Unicode Codepoints Based on GlyphData
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
For selected glyphs, it works like Glyph > Update Glyph Info, but will not change the name, rather reset the Unicode. Will process the built-in GlyphData and GlyphData-XXX.xml in ~/Library/Application Support/Glyphs 3/Info/.
"""

from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font
selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs

Glyphs.clearLog()  # clears log in Macro window
print("Reset Unicode Codepoints Based on GlyphData:")
print(f"Processing {len(selectedLayers)} selected glyphs in {thisFont.familyName}...")

thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		thisGlyph.beginUndo()  # begin undo grouping

		newCode = Glyphs.glyphInfoForName(thisGlyph.name).unicode
		if newCode:
			thisGlyph.unicode = Glyphs.glyphInfoForName(thisGlyph.name).unicode
			print(f"🔢 {thisGlyph.unicode} {thisGlyph.name}")
		else:
			print(f"❌ no Unicode codepoint available for {thisGlyph.name}")

		thisGlyph.endUndo()  # end undo grouping
	print("✅ Done.")
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Reset Unicode Codepoints Based on GlyphData\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
