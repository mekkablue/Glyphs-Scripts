#MenuTitle: Realign BCPs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Realigns handles (BCPs) in current layers of selected glyphs. Useful for resetting out-of-sync handles, e.g., after a transform operation, after interpolation or after switching to a different grid. Hold down Option to process ALL layers of the glyph.
"""

from Foundation import NSPoint, NSEvent, NSNumber, NSMutableArray, NSClassFromString
optionKeyFlag = 524288
optionKeyPressed = NSEvent.modifierFlags() & optionKeyFlag == optionKeyFlag

thisFont = Glyphs.font
moveForward = NSPoint(1, 1)
moveBackward = NSPoint(-1, -1)
noModifier = NSNumber.numberWithUnsignedInteger_(0)
Tool = NSClassFromString("GlyphsPathPlugin").alloc().init()

def realignLayer(thisLayer):
	countOfHandlesOnLayer = 0
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			if thisNode.type == GSOFFCURVE:
				countOfHandlesOnLayer += 1
				selectedNode = NSMutableArray.arrayWithObject_(thisNode)
				thisLayer.setSelection_(selectedNode)
				Tool.moveSelectionLayer_shadowLayer_withPoint_withModifier_(thisLayer, thisLayer, moveForward, noModifier)
				Tool.moveSelectionLayer_shadowLayer_withPoint_withModifier_(thisLayer, thisLayer, moveBackward, noModifier)
	thisLayer.setSelection_(())
	return countOfHandlesOnLayer

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in thisFont.selectedLayers:
		thisGlyph = thisLayer.parent
		# thisGlyph.beginUndo() # undo grouping causes crashes
		if optionKeyPressed:
			handleCount = 0
			for everyLayer in thisGlyph.layers:
				handleCount += realignLayer(everyLayer)
		else:
			handleCount = realignLayer(thisLayer)
		# thisGlyph.endUndo() # undo grouping causes crashes
		print("Processed %i BCPs in %s%s" % (handleCount, "all layers of " if optionKeyPressed else "", thisGlyph.name))
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
