#MenuTitle: Realign Handles in Current Glyph
# -*- coding: utf-8 -*-
__doc__="""
Realigns handles in current glyph. Glyph must be opened in Edit view.
"""

moveForward = NSPoint( 1, 1 )
moveBackward = NSPoint( -1, -1 )
noModifier = NSNumber.numberWithUnsignedInteger_(0)
currentController = Glyphs.currentDocument.windowController().activeEditViewController()

Tool = GSToolSelect.alloc().init()
Tool.setEditViewController_(currentController)

thisLayer = Glyphs.font.selectedLayers[0]
# oldSelection = thisLayer.selection

if thisLayer:
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			if thisNode.type == GSOFFCURVE:
				selectedNode = NSMutableArray.arrayWithObject_(thisNode)
				thisLayer.setSelection_( selectedNode )
				Tool.moveSelectionWithPoint_withModifier_( moveForward,  noModifier )
				Tool.moveSelectionWithPoint_withModifier_( moveBackward, noModifier )
else:
	print "Open a glyph in Edit view and run the script again."

thisLayer.setSelection_( () )
# Tool.dealloc()
