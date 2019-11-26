#MenuTitle: Remove Nodes and Try to Keep Shape
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Delete the selected on-curve nodes, but try to keep the shape of the path. Hold down Shift for balanced handles.
"""

from Foundation import NSEvent

thisFont = Glyphs.font # frontmost font
thisLayer = thisFont.selectedLayers[0] # first of active layers of selected glyphs
thisGlyph = thisLayer.parent # current glyph
selection = thisLayer.selection # node selection in edit mode

# check if Shift is held down:
shiftKeyFlag = 131072
shiftKeyPressed = NSEvent.modifierFlags() & shiftKeyFlag == shiftKeyFlag

if selection:
	selectedNodes = [obj for obj in selection if type(obj)==GSNode and obj.type==GSCURVE]
	if selectedNodes:
		thisGlyph.beginUndo() # begin undo grouping
		thisLayer.selection = None
		for thisNode in selectedNodes:
			thisPath = thisNode.parent
			if not shiftKeyPressed:
				thisPath.removeNodeCheckKeepShape_( thisNode )
			else:
				thisPath.removeNodeCheckKeepShape_normalizeHandles_( thisNode, True )
		thisGlyph.endUndo()   # end undo grouping