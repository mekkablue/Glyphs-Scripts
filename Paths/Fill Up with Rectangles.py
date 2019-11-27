#MenuTitle: Fill Up with Rectangles
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Inserts Rectangles in all empty, selected glyphs.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def drawRect( myBottomLeft, myTopRight ):
	try:
		myRect = GSPath()
		myCoordinates = [
			[ myBottomLeft[0], myBottomLeft[1] ],
			[ myTopRight[0], myBottomLeft[1] ],
			[ myTopRight[0], myTopRight[1] ],
			[ myBottomLeft[0], myTopRight[1] ]
		]

		for thisPoint in myCoordinates:
			newNode = GSNode()
			newNode.type = GSLINE
			newNode.position = ( thisPoint[0], thisPoint[1] )
			myRect.nodes.append( newNode )

		myRect.closed = True
		return myRect

	except Exception as e:
		return False

def process( thisLayer ):
	layerIsEmpty = ( len(thisLayer.paths) == 0 and len(thisLayer.components) == 0 )
	if layerIsEmpty:
		bottomLeft = ( 50.0, 0.0 )
		topRight = ( thisLayer.width - 50.0, 600.0 )
		layerRect = drawRect( bottomLeft, topRight )
		if layerRect:
			thisLayer.paths.append( layerRect )
			return "OK"
		else:
			return "error"
	else:
		return "not empty, skipped"

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	print("Filling %s: %s." % ( thisGlyph.name, process( thisLayer ) ))
	thisGlyph.endUndo()

Font.enableUpdateInterface()
