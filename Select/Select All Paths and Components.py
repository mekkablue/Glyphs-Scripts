#MenuTitle: Select All Paths and Components
# -*- coding: utf-8 -*-
__doc__="""
Select all paths and components in the current glyph, and deselect all anchors.
"""



thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs
thisDoc = Glyphs.currentDocument # the frontmost document

def process( thisLayer ):
	thisLayer.clearSelection()
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			thisLayer.addSelection_(thisNode)
	for thisComponent in thisLayer.components:
		thisLayer.addSelection_(thisComponent)

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Selecting paths and components in: %s." % thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
