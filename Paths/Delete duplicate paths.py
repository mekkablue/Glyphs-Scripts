#MenuTitle: Delete Duplicate Paths
# -*- coding: utf-8 -*-
__doc__="""
Finds and deletes duplicate paths in active layers of selected glyphs.
"""


thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisLayer ):
	indexesOfPathsToBeRemoved = []
	numberOfPaths = len(thisLayer.paths)
	numberOfDeletedPaths = 0
	
	for thisPathNumber in range( numberOfPaths ):
		if thisPathNumber < (numberOfPaths - 1):
			thisPath = thisLayer.paths[thisPathNumber]
			for thatPathNumber in range( thisPathNumber + 1, numberOfPaths ):
				thatPath = thisLayer.paths[thatPathNumber]
				if thisPath.pathDict() == thatPath.pathDict():
					indexesOfPathsToBeRemoved.append( thatPathNumber )
	
	if indexesOfPathsToBeRemoved:
		for thatIndex in reversed( sorted( indexesOfPathsToBeRemoved )):
			thisLayer.removePathAtIndex_( thatIndex )
			numberOfDeletedPaths += 1
	
	return numberOfDeletedPaths

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo() # begin undo grouping
	numberOfDeletions = process( thisLayer )
	if numberOfDeletions > 0:
		pathOrPaths = "path"
		if numberOfDeletions > 1:
			pathOrPaths += "s"
		print "Deleted %i duplicate %s in %s." % ( numberOfDeletions, pathOrPaths, thisGlyph.name)
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
