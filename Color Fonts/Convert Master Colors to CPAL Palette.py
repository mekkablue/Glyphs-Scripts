# MenuTitle: Convert Master Colors to CPAL Palette
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Will look for ‘Master Color’ parameters in the font masters and then create a ‘Color Palettes’ parameter in Font Info > Font with the same color. Will default to black (for missing Master Color parameters). Will add Dark Mode master colors as second palette.
"""

from AppKit import NSColor
from Foundation import NSHeight, NSMutableArray
from GlyphsApp import Glyphs


def colorForMaster(thisMaster, parameterName="Master Color"):
	color = thisMaster.customParameters[parameterName]
	if not color:
		color = NSColor.blackColor()
	color = color.colorUsingColorSpaceName_("NSCalibratedRGBColorSpace")
	print(f"\t{parameterName}: {color.redComponent():.3f}r {color.greenComponent():.3f}g {color.blueComponent():.3f}b {color.alphaComponent():.3f}a")
	return color


Glyphs.clearLog()  # clears log in Macro window
print("Status Report: Convert Master Colors to CPAL Palette")
if Glyphs.versionNumber < 4:
	try:
		splitview = Glyphs.delegate().macroPanelController().consoleSplitView()
		splitview.setPosition_ofDividerAtIndex_(NSHeight(splitview.frame()) * 0.2, 0)
	except Exception as e:
		print(f"\nFailed resetting the macro panel divider: {e}")
		import traceback
		print(traceback.format_exc())

thisFont = Glyphs.font  # frontmost font
thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	paletteColors = []
	paletteColorsDark = []
	for thisMaster in thisFont.masters:
		print(f"Analyzing master ‘{thisMaster.name}’...")
		paletteColors.append(colorForMaster(thisMaster))
		paletteColorsDark.append(colorForMaster(thisMaster, parameterName="Master Color Dark"))
	cpalPalettes = NSMutableArray.arrayWithObjects_(paletteColors, paletteColorsDark)
	if cpalPalettes:
		print("🌈 Adding Color Palettes parameter in Font Info > Font...")
		thisFont.customParameters["Color Palettes"] = cpalPalettes
		print("✅ Done.")
		# open Font Info:
		for doc in Glyphs.documents:
			if doc.font == thisFont:
				doc.windowController().showFontInfoWindowWithTabSelected_(0)
				break
	else:
		print("🚫 No palette added.")
		Glyphs.showMacroWindow()

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Convert Master Colors to CPAL Palette\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
