#MenuTitle: Enlarge Short Segments
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Doubles single-unit distances.
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			prevNode = thisNode.prevNode
			if prevNode.type != OFFCURVE and thisNode.type != OFFCURVE:
				xDistance = thisNode.x-prevNode.x
				yDistance = thisNode.y-prevNode.y
				if abs(xDistance) < 1.0 and abs(yDistance) < 1.0:
					thisNode.x = prevNode.x + xDistance * 2
					thisNode.y = prevNode.y + yDistance * 2

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print("Processing %s" % thisGlyph.name)
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
