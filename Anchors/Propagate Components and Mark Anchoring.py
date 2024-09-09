#MenuTitle: Propagate Components and Mark Anchoring
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Takes the current master’s component and mark anchoring setup and replicates it in all other (compatible) masters. Useful for complex Arabic ligature marks.
"""

def process(thisLayer):
	componentStructure = thisLayer.componentNames()
	glyph = thisLayer.parent
	for layer in glyph.layers:
		if layer is thisLayer:
			continue
		layer.setComponentNames_(componentStructure)
		if layer.compareString() != thisLayer.compareString():
			continue
		for i, accentComponent in enumerate(layer.components):
			if i < 1:
				continue
			accentComponent.setAnchor_(thisLayer.components[i].anchor)


thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears log in Macro window

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		print(f"Processing {thisGlyph.name}")
		thisGlyph.beginUndo() # begin undo grouping
		process(thisLayer)
		thisGlyph.endUndo()   # end undo grouping
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Propagate Components and Mark Anchoring\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
