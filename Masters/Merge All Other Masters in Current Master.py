#MenuTitle: Merge All Other Masters in Current Master
# -*- coding: utf-8 -*-
__doc__="""
For selected glyphs, merges all paths from other masters onto the current master layer.
"""

import GlyphsApp

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
otherMasterIDs = [m.id for m in thisFont.masters if m is not thisFontMaster]
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisGlyph ):
	currentLayer = thisGlyph.layers[thisFontMaster.id]
	print currentLayer
	for thisID in otherMasterIDs:
		sourceLayer = thisGlyph.layers[thisID]
		sourcePaths = sourceLayer.paths
		if sourcePaths:
			for sourcePath in sourcePaths:
				currentLayer.paths.append( sourcePath )

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisGlyph )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
