#MenuTitle: All Anchors in All Layers
# -*- coding: utf-8 -*-
__doc__="""
Makes sure all nodes are replicated in all layers in the same relative positions.
"""

import GlyphsApp


thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def allAnchorsOfThisGlyph( thisGlyph ):
	anchorDict = {}
	for thisLayer in thisGlyph.layers:
		thisWidth = thisLayer.width
		for thisAnchor in [a for a in thisLayer.anchors]:
			thisAnchorInfo = ( thisAnchor.x / thisWidth, thisAnchor.y )
			if not thisAnchor.name in anchorDict.keys():
				anchorDict[thisAnchor.name] = [ thisAnchorInfo ]
			else:
				anchorDict[thisAnchor.name].append( thisAnchorInfo )
	return anchorDict

def averagePosition( listOfPositions, thisWidth ):
	numOfValues = len( listOfPositions )
	averageX = sum( p[0] for p in listOfPositions ) / numOfValues
	averageY = sum( p[1] for p in listOfPositions ) / numOfValues
	return NSPoint( averageX * thisWidth, averageY )

def process( thisGlyph ):
	reportString = ""
	allAnchorDict = allAnchorsOfThisGlyph( thisGlyph )

	if allAnchorDict: # skip glyphs without anchors (like space)
		allAnchorNames = allAnchorDict.keys()

		for thisLayer in thisGlyph.layers:
			layerAnchorNames = [a.name for a in thisLayer.anchors]
		
			if len(layerAnchorNames) < len(allAnchorNames):
				anchorsAdded = []
				anchorNamesToBeAdded = [n for n in allAnchorNames if not n in layerAnchorNames]
				thisWidth = thisLayer.width
			
				for newAnchorName in anchorNamesToBeAdded:
					newAnchorPosition = averagePosition( allAnchorDict[newAnchorName], thisWidth )
					newAnchor = GSAnchor()
					newAnchor.name = newAnchorName
					newAnchor.position = newAnchorPosition
					thisLayer.addAnchor_( newAnchor )
					anchorsAdded.append( newAnchorName )
				
				reportString += "  %s: %s\n" % ( thisLayer.name, ", ".join(anchorsAdded) )
		
	return reportString
			

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	print process( thisGlyph )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
