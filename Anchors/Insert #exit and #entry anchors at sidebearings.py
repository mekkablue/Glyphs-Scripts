#MenuTitle: Insert #exit and #entry anchors at sidebearings
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Inserts #entry at LSB and #exit at RSB (LTR) or the other way around (RTL) in all masters and special layers of the selected glyphs. Will not overwrite existing anchors unless you hold down OPT+SHIFT.
"""

from AppKit import NSEvent, NSPoint

def process(thisLayer, overwrite):
	anchorInfos = {
		"#exit": thisLayer.width if thisLayer.parent.direction != GSRTL else 0.0,
		"#entry": 0.0 if thisLayer.parent.direction != GSRTL else thisLayer.width,
		}
	for anchorName in anchorInfos.keys():
		if not thisLayer.anchors[anchorName] or overwrite:
			x = anchorInfos[anchorName]
			newAnchor = GSAnchor()
			newAnchor.name = anchorName
			newAnchor.position = NSPoint(x, 0.0)
			thisLayer.anchors.append(newAnchor)

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears log in Macro window

keysPressed = NSEvent.modifierFlags()
optionKey = 524288
shiftKey = 131072
optionKeyPressed = keysPressed & optionKey == optionKey
shiftKeyPressed = keysPressed & shiftKey == shiftKey
forceReset = optionKeyPressed and shiftKeyPressed

try:
	for selectedLayer in selectedLayers:
		thisGlyph = selectedLayer.parent
		print("Processing %s" % thisGlyph.name)
		for thisLayer in thisGlyph.layers:
			process(thisLayer, forceReset)
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Insert #exit and #entry anchors at sidebearings\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
