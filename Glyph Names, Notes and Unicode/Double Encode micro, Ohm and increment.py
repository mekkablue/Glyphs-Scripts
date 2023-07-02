#MenuTitle: Double Encode micro, Ohm and increment
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Add Unicodes of mu, Omega and Delta to micro, Ohm and increment.
"""

codeInfos = (
	{
		"target": "micro",
		"greek": "mu",
	},
	{
		"target": "Ohm",
		"greek": "Omega",
	},
	{
		"target": "increment",
		"greek": "Delta",
	},
)

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears log in Macro window

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for codeInfo in codeInfos:
		targetGlyphName = codeInfo["target"]
		targetGlyph = thisFont.glyphs[targetGlyphName]
		targetCode = Glyphs.glyphInfoForName(targetGlyphName).unicode
		
		greekName = codeInfo["greek"]
		greekGlyph = thisFont.glyphs[greekName]
		greekCode = Glyphs.glyphInfoForName(greekName).unicode

		if targetGlyph and not greekGlyph:
			targetGlyph.unicode = targetCode
			targetGlyph.unicodes = [targetCode, greekCode]
		elif greekGlyph and not targetGlyph:
			print(targetGlyphName)
			greekGlyph.name = targetGlyphName
			greekGlyph.unicode = targetCode
			greekGlyph.unicodes = [targetCode, greekCode]
		elif greekGlyph and targetGlyph:
			greekGlyph.export = False
			greekGlyph.name += ".disabled"
			targetGlyph.unicode = targetCode
			targetGlyph.unicodes = [targetCode, greekCode]
	thisFont.newTab("/"+"/".join([i["target"] for i in codeInfos]))
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Double Encode micro, Ohm and increment\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
