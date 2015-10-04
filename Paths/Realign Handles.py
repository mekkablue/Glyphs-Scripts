#MenuTitle: Realign Handles in Current Glyph
# -*- coding: utf-8 -*-
__doc__="""
Realigns handles in current glyph. Glyph must be opened in Edit view.
"""

currentController = Glyphs.currentDocument.windowController().activeEditViewController()
zero = NSNumber.numberWithUnsignedInteger_(0)
Tool = GSToolSelect.alloc().init()
Tool.setEditViewController_(currentController)
moveForward = NSPoint( 1, 1 )
moveBackward = NSPoint( -1, -1 )

thisLayer = Glyphs.font.selectedLayers[0]
if thisLayer:
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			if thisNode.type == 65:
				thisLayer.setSelection_( NSMutableArray.arrayWithObject_(thisNode ) )
				Tool.moveSelectionWithPoint_withModifier_( moveForward, zero )
				Tool.moveSelectionWithPoint_withModifier_( moveBackward, zero )
else:
	print "Open a glyph in Edit view and run the script again."

# Tool.dealloc()
