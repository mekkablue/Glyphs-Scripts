#MenuTitle: Delete Nodes and Try to Keep Shape
# -*- coding: utf-8 -*-
__doc__="""
Delete the selected on-curve nodes, but try to keep the shape of the path.
"""

import GlyphsApp


thisFont = Glyphs.font # frontmost font
thisLayer = thisFont.selectedLayers[0] # first of active layers of selected glyphs
thisGlyph = thisLayer.parent # current glyph

# node selection in edit mode
try:
	selection = thisLayer.selection() # Glyphs 2.1 and earlier
except:
	selection = thisLayer.selection # Glyphs 2.2 and later


if selection:
	selectedNodes = [obj for obj in selection if type(obj)==GSNode and obj.type==35]
	if selectedNodes:
		thisGlyph.beginUndo() # begin undo grouping
		thisLayer.setSelection_( None )
		for thisNode in selectedNodes:
			try:
				thisPath = thisNode.parent()
			except Exception as e:
				thisPath = thisNode.parent
			thisPath.removeNodeCheckKeepShape_( thisNode )
		thisGlyph.endUndo()   # end undo grouping