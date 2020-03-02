#MenuTitle: Fill Up with Rectangles
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Inserts Rectangles in all empty, selected glyphs. Verbose report in Macro Window.
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
	thisGlyph = thisLayer.parent
	try:
		case = thisGlyph.case
		if case == GSLowercase:
			height = 500
		elif case == GSUppercase:
			height = 700
		else:
			height = 600
	except:
		subCategory = thisGlyph.subCategory
		if subCategory == "Lowercase":
			height = 500
		elif subCategory == "Uppercase":
			height = 700
		else:
			height = 600
			
	if layerIsEmpty:
		bottomLeft = ( 50.0, 0.0 )
		topRight = ( thisLayer.width - 50.0, height )
		layerRect = drawRect( bottomLeft, topRight )
		if layerRect:
			try:
				thisLayer.paths.append( layerRect )
			except:
				# Glyphs 3:
				thisLayer.shapes.append( layerRect )
			return "OK"
		else:
			return "error"
	else:
		return "not empty, skipped"

Glyphs.clearLog() # clears macro window log
print("‘Fill Up with Rectangles’ report for: %s\n" % Font.familyName)

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	print("Filling %s: %s." % ( thisGlyph.name, process( thisLayer ) ))
	thisGlyph.endUndo()

Font.enableUpdateInterface()

print("\nDone.")