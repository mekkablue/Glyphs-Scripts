# MenuTitle: Remove Short Segments
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Deletes single-unit segments.
"""

from GlyphsApp import Glyphs, GSOFFCURVE

thisFont = Glyphs.font  # frontmost font
selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs


def process(thisLayer):
	for thisPath in thisLayer.paths:
		for i in range(len(thisPath.nodes))[::-1]:
			thisNode = thisPath.nodes[i]
			prevNode = thisNode.prevNode
			if prevNode.type != GSOFFCURVE and thisNode.type != GSOFFCURVE:
				xDistance = thisNode.x - prevNode.x
				yDistance = thisNode.y - prevNode.y
				if abs(xDistance) < 1.0 and abs(yDistance) < 1.0:
					thisPath.removeNodeCheckKeepShape_(thisNode)


thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		print("Processing %s" % thisGlyph.name)
		# thisGlyph.beginUndo()  # undo grouping causes crashes
		process(thisLayer)
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
