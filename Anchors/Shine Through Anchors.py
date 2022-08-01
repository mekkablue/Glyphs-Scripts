#MenuTitle: Shine Through Anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
In all layers of selected glyphs, inserts (‘traversing’) anchors from components.
"""

def process( thisGlyph ):
	insertedAnchors = []
	layerCount = 0
	for thisLayer in thisGlyph.layers:
		if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
			layerCount += 1
			for thisAnchor in thisLayer.anchorsTraversingComponents():
				newAnchor = GSAnchor()
				newAnchor.name = thisAnchor.name
				newAnchor.position = thisAnchor.position
				thisLayer.anchors.append(newAnchor)
				insertedAnchors.append(newAnchor.name)
				
	insertedAnchors = sorted(list(set(insertedAnchors)))
	print("\t⚓️ Added %i anchors on %i layers: %s" % (
		len(insertedAnchors),
		layerCount,
		", ".join(insertedAnchors),
	))

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears log in Macro window

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		print("🔠 %s" % thisGlyph.name)
		thisGlyph.beginUndo() # begin undo grouping
		process( thisGlyph )
		thisGlyph.endUndo()   # end undo grouping
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Shine Through Anchors\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
