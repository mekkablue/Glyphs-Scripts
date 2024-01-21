# MenuTitle: Top Mark Mover
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Moves selected marks vertically, so their _top anchor is on the respective vertical metric.
"""

from Foundation import NSPoint
from GlyphsApp import Glyphs, GSUppercase, GSSmallcaps
from mekkablue.geometry import italicize


Glyphs.clearLog()  # clears log in Macro window
thisFont = Glyphs.font
thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	font = Glyphs.font
	selectedMarks = set([layer.parent for layer in font.selectedLayers if layer.parent.category == "Mark"])
	for glyph in selectedMarks:
		print(f"🔤 Processing {glyph.name}...")
		glyph.beginUndo()
		for layer in glyph.layers:
			top = layer.anchors["_top"]
			if not top:
				print(f"  🚫 No _top anchor found: {glyph.name}, layer ‘{layer.name}’")
				continue

			if glyph.case == GSUppercase:
				refHeight = layer.master.capHeight
			elif glyph.case == GSSmallcaps:
				refHeight = layer.master.xHeightForLayer_(layer)
			else:  # GSLowercase and other cases
				refHeight = layer.master.xHeight

			if refHeight != top.y:
				diffY = refHeight - top.y
				if diffY == 0:
					print(f"  ℹ️ _top anchor already OK ({top.y}y): {glyph.name}, {layer.name}")
					continue

				diff = italicize(NSPoint(0, diffY), italicAngle=layer.italicAngle)
				layer.applyTransform((1, 0, 0, 1, diff.x, diff.y))
				print(f"  ✅ Moved {diff.x}x {diff.y}y: {glyph.name}, {layer.name}")
		glyph.endUndo()
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Top Mark Mover\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
