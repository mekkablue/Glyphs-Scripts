#MenuTitle: Delete Non-Color Layers in Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Deletes all sublayers in all glyphs that are not of type "Color X" (CPAL/COLR layers).
"""

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
thisFontMasterID = thisFontMaster.id
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisGlyph ):
	for i in range(len(thisGlyph.layers))[::-1]:
		currentLayer = thisGlyph.layers[i]
		if not currentLayer.layerId == thisFontMasterID: # not the master layer
			if not currentLayer.name.startswith("Color "):
				currentLayerID = currentLayer.layerId
				thisGlyph.removeLayerForKey_(currentLayerID)

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print("Processing", thisGlyph.name)
	thisGlyph.beginUndo() # begin undo grouping
	process( thisGlyph )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
