#MenuTitle: Sync Components Across All Other Masters
# -*- coding: utf-8 -*-
__doc__="""
Takes the current layer’s components, and resets all other masters to the same component structure.
"""

import GlyphsApp

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisLayer ):
	thisGlyph = thisLayer.parent
	compSet = thisLayer.componentNames()
	for thatLayer in thisGlyph.layers:
		if thatLayer != thisLayer: # don't sync the layer with itself
			if thatLayer.layerId == thatLayer.associatedMasterId: # only sync master layers
				thatLayer.setComponentNames_( compSet )

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
