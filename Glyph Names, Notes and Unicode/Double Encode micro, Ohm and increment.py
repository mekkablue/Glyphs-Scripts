# MenuTitle: Double Encode micro, Ohm, increment and florin
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Add Unicodes of mu, Omega and Delta to micro, Ohm and increment, as well as florin (but only if FHook is not present in the font). Hold down COMMAND + SHIFT to apply to ALL open fonts.
"""

from AppKit import NSEvent, NSEventModifierFlagShift, NSEventModifierFlagCommand
from GlyphsApp import Glyphs


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
	{
		"target": "florin",
		"greek": "Fhook",
	}
)

Glyphs.clearLog()  # clears log in Macro window

# CMD+SHIFT pressed?
keysPressed = NSEvent.modifierFlags()
shiftKeyPressed = keysPressed & NSEventModifierFlagShift == NSEventModifierFlagShift
commandKeyPressed = keysPressed & NSEventModifierFlagCommand == NSEventModifierFlagCommand
shouldApplyToAllFonts = shiftKeyPressed and commandKeyPressed

if shouldApplyToAllFonts:
	fonts = Glyphs.fonts
else:
	fonts = (Glyphs.font, )

for thisFont in fonts:
	print(f"DOUBLE ENCODE REPORT: {thisFont.filepath.lastPathComponent().stringByDeletingDotSuffix()}")
	thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
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
				print(f"  🔤 {targetGlyphName}: {', '.join(targetGlyph.unicodes)}")
			elif targetGlyphName == "florin":
				continue
			elif greekGlyph and not targetGlyph:
				greekGlyph.name = targetGlyphName
				greekGlyph.unicode = targetCode
				greekGlyph.unicodes = [targetCode, greekCode]
				print(f"  🔤 Renamed {greekName} → {targetGlyphName}: {', '.join(greekGlyph.unicodes)}")
			elif greekGlyph and targetGlyph:
				greekGlyph.export = False
				greekGlyph.name += ".disabled"
				targetGlyph.unicode = targetCode
				targetGlyph.unicodes = [targetCode, greekCode]
				print(f"  🔤 Disabled {greekName}, renamed to {greekGlyph.name}; {targetGlyphName}: {', '.join(targetGlyph.unicodes)}")
		thisFont.newTab("/" + "/".join([i["target"] for i in codeInfos]))
	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ Error in script: Double Encode micro, Ohm and increment\n")
		import traceback
		print(traceback.format_exc())
		print()
		raise e
	finally:
		thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
		print()
