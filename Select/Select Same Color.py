#MenuTitle: Select Same Color
# -*- coding: utf-8 -*-
__doc__="""
Select glyphs with the same color as the currently selected one.
"""

import GlyphsApp

thisFont = Glyphs.font # frontmost font
selectedLayer = thisFont.selectedLayers[0]

def indexSetWithIndex( index ):
	indexSet = NSIndexSet.alloc().initWithIndex_( index )
	return indexSet

def hasColor( thisGlyph, colorIndex ):
	returnValue = False
	if thisGlyph.color == colorIndex:
		returnValue = True
	return returnValue

if selectedLayer:
	selectedColor = selectedLayer.parent.color
	thisDoc = Glyphs.currentDocument
	thisController = thisDoc.windowController().tabBarControl().viewControllers()[0].glyphsArrayController()
	displayedGlyphs = thisController.arrangedObjects()
	
	thisFont.disableUpdateInterface() # suppresses UI updates in Font View

	for i in range(len( displayedGlyphs )):
		thisGlyph = displayedGlyphs[i]
		if hasColor( thisGlyph, selectedColor ):
			thisController.addSelectionIndexes_( indexSetWithIndex(i) )

	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
