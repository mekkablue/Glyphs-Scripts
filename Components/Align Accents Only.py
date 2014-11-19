#MenuTitle: Align Accents Only
# -*- coding: utf-8 -*-
__doc__="""
Aligns accents without the need to use Automatic Alignment. Useful if you have an individually placed base glyph and want to update the accent positions.
"""

import GlyphsApp


thisFont = Glyphs.font # frontmost font
thisFontMasterID = thisFont.selectedFontMaster.id # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def subtract( firstPoint, secondPoint ):
	newX = firstPoint.x - secondPoint.x
	newY = firstPoint.y - secondPoint.y
	return NSPoint( newX, newY )

def add( firstPoint, secondPoint ):
	newX = firstPoint.x + secondPoint.x
	newY = firstPoint.y + secondPoint.y
	return NSPoint( newX, newY )

def updateLastPositions( positionDict, anchors ):
	anchorsWithoutUnderscore = [ a for a in anchors if not a.name.startswith("_") ]
	anchorsWithUnderscore = [ a for a in anchors if a.name.startswith("_") ]

	for thisAnchor in anchorsWithoutUnderscore:
		anchorShift = NSPoint(0,0)
		anchorName = thisAnchor.name
		anchorPosition = thisAnchor.position
		if anchorsWithUnderscore:
			correspondingAnchorsWithUnderscore = [ a for a in anchorsWithUnderscore if a.name.split("_")[1] == anchorName ]
			if correspondingAnchorsWithUnderscore:
				anchorShift = correspondingAnchorsWithUnderscore[0].position
		
		anchorOffset = subtract( anchorPosition, anchorShift )
		if anchorName in positionDict.keys():
			# anchor of an accent
			positionDict[anchorName] = add( positionDict[anchorName], anchorOffset )
		else:
			# base anchor:
			positionDict[anchorName] = anchorOffset

def componentPosition( componentAnchors, lastPositions ):
	componentAnchorsWithUnderscore = [ a for a in componentAnchors if a.name.startswith("_") ]
	if componentAnchorsWithUnderscore:
		for thisAnchor in componentAnchorsWithUnderscore:
			anchorName = thisAnchor.name
			baseAnchorName = anchorName[1:]
			if baseAnchorName in lastPositions.keys():
				anchorPosition = thisAnchor.position
				lastPosition = lastPositions[ baseAnchorName ]
				return subtract( lastPosition, anchorPosition )
				
	return None
	

def process( thisLayer ):
	thisMasterID = thisLayer.associatedMasterId
	
	# the base:
	baseComponent = thisLayer.components[0]
	baseComponentPosition = baseComponent.position
	baseComponentAnchors = [a.copy() for a in baseComponent.component.layers[thisMaster.id].anchors]
	for thisBaseAnchor in baseComponentAnchors:
		thisBaseAnchor.position = add( thisBaseAnchor.position, baseComponentPosition )
	
	# record anchor positions:
	lastPositions = {}
	updateLastPositions( lastPositions, [ a for a in baseComponentAnchors if not a.name.startswith("_") ] )

	# go through accents and reposition them:
	accentComponents = [c for c in thisLayer.components][1:]
	if accentComponents:
		for thisComponent in accentComponents:
			thisAccent = thisComponent.component.layers[ thisMasterID ]
			thisAccentAnchors = thisAccent.anchors
			newComponentPosition = componentPosition( thisAccentAnchors, lastPositions )
			
			if newComponentPosition:
				thisComponent.position = newComponentPosition
				updateLastPositions( lastPositions, thisAccentAnchors )
	
			

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
