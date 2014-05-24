#MenuTitle: Realign Handles in Current Glyph
# -*- coding: utf-8 -*-
__doc__="""
Realigns Handles in Current Glyph. Glyph must be opened in Edit View.
"""

def realignHandles():
	moveForward = NSPoint( 1, 1 )
	moveBackward = NSPoint( -1, -1 )
	currentController = Glyphs.currentDocument.windowController().activeEditViewController()

	Tool = GSToolSelect.alloc().init()
	Tool.setEditViewController_(currentController)
	Tool.moveSelectionWithPoint_withModifier_( moveForward, 0 )
	Tool.moveSelectionWithPoint_withModifier_( moveBackward, 0 )
	Tool.dealloc()

thisLayer = Glyphs.font.selectedLayers[0]

for thisPath in thisLayer.paths:
	for thisNode in thisPath.nodes:
		if thisNode.type != 65:
			thisLayer.setSelection_( NSMutableArray.arrayWithObject_(thisNode ) )
			realignHandles()
