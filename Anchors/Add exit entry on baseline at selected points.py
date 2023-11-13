#MenuTitle: Add #exit/#entry on baseline at selected points
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Use the outermost selected points, take their x coordinates, and add #exit and #entry anchors on the baseline with the same x coordinates.
"""

def process(thisLayer):
	isRTL = thisLayer.parent.direction == GSRTL
	def addAnchor(name, x):
		thisLayer.anchors.append(GSAnchor(name, (x, 0)))
	bounds =  thisLayer.bounds
	threshold = bounds.origin.x + bounds.size.width/2
	selectedNodes = []
	for item in thisLayer.selection:
		if type(item) == GSNode:
			selectedNodes.append(item)
	selectedNodes = sorted(selectedNodes, key=lambda node: node.x)
	if not selectedNodes:
		return
	if not isRTL:
		if selectedNodes[0].x < threshold:
			addAnchor("#entry", selectedNodes[0].x)
		if selectedNodes[-1].x > threshold:
			addAnchor("#exit", selectedNodes[0].x)
	else:
		if selectedNodes[0].x < threshold:
			addAnchor("#exit", selectedNodes[0].x)
		if selectedNodes[-1].x > threshold:
			addAnchor("#entry", selectedNodes[0].x)
	

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears log in Macro window

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		print(f"Processing {thisGlyph.name}")
		thisGlyph.beginUndo() # begin undo grouping
		for thatLayer in thisGlyph.layers:
			if thatLayer.isMasterLayer or thatLayer.isSpecialLayer:
				process(thatLayer)
		thisGlyph.endUndo()   # end undo grouping
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Add #exit/#entry on baseline at selected points\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
