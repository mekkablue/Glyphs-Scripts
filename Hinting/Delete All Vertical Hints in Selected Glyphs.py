#MenuTitle: Delete All Vertical Hints in Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Removes all vertical hints in the selected layers.
"""




thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs



def process( thisLayer ):
	numberOfHints = len(thisLayer.hints)
	for i in range(numberOfHints)[::-1]:
		thisHint = thisLayer.hints[i]
		if not thisHint.horizontal:
			del thisLayer.hints[i]
			

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
