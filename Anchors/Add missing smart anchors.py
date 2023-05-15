#MenuTitle: Add missing smart anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds all anchors for properties of selected smart glyphs on all their layers. Skips Width and Height anchors.
"""

from AppKit import NSPoint

def process( glyph ):
	countOfAnchors = 0
	countOfLayers = 0
	axisNames = [a.name for a in glyph.smartComponentAxes if not a.name in ("Width", "Height")]
	for thisLayer in glyph.layers:
		if thisLayer.isSpecialLayer:
			countOfLayers += 1
			for i, axisName in enumerate(axisNames):
				if not thisLayer.anchors[axisName]:
					smartAnchor = GSAnchor(axisName, NSPoint(0, -i*50))
					thisLayer.anchors.append(smartAnchor)
					countOfAnchors += 1
	print(f"  - added {countOfAnchors} anchors on {countOfLayers} smart layers.")

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears log in Macro window
print(f"Adding missing smart anchors in {len(selectedLayers)} glyphs:\n")

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		if not thisGlyph.isSmartGlyph():
			print(f"⏭️ Skipping {thisGlyph.name} (not a smart glyph).")
		else:
			print(f"⚙️ Processing {thisGlyph.name}:")
			thisGlyph.beginUndo() # begin undo grouping
			process( thisGlyph )
			thisGlyph.endUndo()   # end undo grouping
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Add missing smart anchors\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
