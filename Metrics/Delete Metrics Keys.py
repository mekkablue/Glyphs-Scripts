#MenuTitle: Delete metrics keys
# -*- coding: utf-8 -*-
__doc__="""
Deletes left and right metrics keys in all layers of all selected glyphs.
"""

import GlyphsApp

Glyphs.clearLog() # clears macro window log
thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisGlyph ):
	thisGlyph.setLeftMetricsKey_(None)
	thisGlyph.setRightMetricsKey_(None)
	for thisLayer in thisGlyph.layers:
		thisLayer.setLeftMetricsKey_(None)
		thisLayer.setRightMetricsKey_(None)

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Deleted metrics keys: %s" % thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisGlyph )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
