# MenuTitle: Randomly Distribute Shapes on Color Layers
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Take the shapes of the fallback master layer, and randomly copy them onto the available CPAL/COLR color layers. ⚠️ Will overwrite contents of existing color layers unless you hold down Cmd+Shift.
"""

import random
from AppKit import NSEvent
from copy import copy
from GlyphsApp import Glyphs, GSGlyph

random.seed()


def process(thisGlyph, shouldPreserveExistingShapes=False):
	for thisMaster in thisGlyph.parent.masters:
		mID = thisMaster.id
		masterLayer = thisGlyph.layers[mID]
		availableColorLayers = [layer for layer in thisGlyph.layers if layer.associatedMasterId == mID and layer.attributes and "colorPalette" in layer.attributes.keys()]
		if availableColorLayers:
			if not shouldPreserveExistingShapes:
				for colorLayer in availableColorLayers:
					colorLayer.clear()
			for thisShape in masterLayer.shapes:
				targetLayer = random.choice(availableColorLayers)
				targetLayer.shapes.append(copy(thisShape))


Glyphs.clearLog()  # clears log in Macro window
print("Randomly Distribute Shapes on Color Layers")

keysPressed = NSEvent.modifierFlags()
commandKey = 1048576
shiftKey = 131072
commandKeyPressed = keysPressed & commandKey == commandKey
shiftKeyPressed = keysPressed & shiftKey == shiftKey
shouldPreserveExistingShapes = commandKeyPressed and shiftKeyPressed

thisFont = Glyphs.font  # frontmost font
selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs
selectedGlyphs: list[GSGlyph] = []
if selectedLayers:
	selectedGlyphs = [layer.parent for layer in selectedLayers]
	print(f"{len(selectedGlyphs)} selected glyphs in font ‘{thisFont.familyName}’...")
else:
	selectedGlyphs = thisFont.glyphs
	print(f"No glyph selected, processing all {len(selectedGlyphs)} glyphs in font ‘{thisFont.familyName}’...")

thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	for thisGlyph in selectedGlyphs:
		print(f"Distributing shapes on {thisGlyph.name}")
		thisGlyph.beginUndo()  # begin undo grouping
		process(thisGlyph, shouldPreserveExistingShapes)
		thisGlyph.endUndo()  # end undo grouping
	print("✅ Done.")
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Randomly Distribute Shapes on Color Layers\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
