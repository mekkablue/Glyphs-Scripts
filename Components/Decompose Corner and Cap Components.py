# MenuTitle: Decompose Corner and Cap Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Recreates the current paths without caps or components. Hold down SHIFT to decompose on all layers.
"""

from AppKit import NSEvent, NSShiftKeyMask
from GlyphsApp import Glyphs

keysPressed = NSEvent.modifierFlags()
shiftKeyPressed = keysPressed & NSShiftKeyMask == NSShiftKeyMask

thisFont = Glyphs.font  # frontmost font


def decomposeCornerAndCapComponentsOnLayer(thisLayer):
	thisLayer.decomposeSmartOutlines()
	thisLayer.cleanUpPaths()  # duplicate nodes at startpoint


def decomposeCornerAndCapComponentsOnAllLayersOfGlyph(thisGlyph):
	for thisLayer in thisGlyph.layers:
		if thisLayer.isSpecialLayer or thisLayer.isMasterLayer:
			decomposeCornerAndCapComponentsOnLayer(thisLayer)


thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		print("Processing", thisGlyph.name)
		# thisGlyph.beginUndo()  # undo grouping causes crashes
		if shiftKeyPressed:
			decomposeCornerAndCapComponentsOnAllLayersOfGlyph(thisGlyph)
		else:
			decomposeCornerAndCapComponentsOnLayer(thisLayer)
		# thisGlyph.endUndo()  # undo grouping causes crashes

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e

finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
