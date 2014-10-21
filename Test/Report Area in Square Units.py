#MenuTitle: Report Area in Square Units
# -*- coding: utf-8 -*-
__doc__="""
Calculates the area of each selected glyph, and outputs it in square units. Increase precision by changing the value for PRECISION in line 9 (script will slow down).
"""

import GlyphsApp

PRECISION = 2

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs
measurementTool = NSClassFromString("GlyphsToolMeasurement").alloc().init()

def sizeOfSlice( thisLayer, y ):
	theseBounds = thisLayer.bounds
	startPointX = theseBounds.origin.x - 10
	endPointX = startPointX + theseBounds.size.width + 20
	startPoint = NSPoint( startPointX, y )
	endPoint   = NSPoint( endPointX, y )
	listOfIntersections = measurementTool.calculateIntersectionsForLayer_startPoint_endPoint_( thisLayer, startPoint, endPoint )
	totalLength = 0.0
	if len(listOfIntersections) >= 4:
		listOfIntersections.pop(0)
		listOfIntersections.pop(-1)
		for thisPairIndex in range(len(listOfIntersections)/2):
			firstNode = listOfIntersections[ thisPairIndex*2 ].pointValue()
			secondNode = listOfIntersections[ thisPairIndex*2+1 ].pointValue()
			totalLength += abs( secondNode.x - firstNode.x )
	return totalLength

def areaForLayer( thisLayer, precision = 2 ):
	cleanLayer = thisLayer.copyDecomposedLayer()
	cleanLayer.removeOverlap()
	cleanLayer.addExtremePointsForce_(True)
	cleanBounds = cleanLayer.bounds
	lowerY = int( cleanBounds.origin.y )
	upperY = lowerY + int( cleanBounds.size.height + 2 )
	area = 0.0
	for thisY in range(lowerY,upperY):
		for thisRound in range(precision):
			measurementHeight = float(thisY) + ( float(thisRound) / float(precision) )
			area += sizeOfSlice( cleanLayer, measurementHeight )
	return area / precision

def process( thisLayer ):
	area = areaForLayer( thisLayer, PRECISION )
	print "%.1f square units" % ( area )

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Area of %s:" % (thisGlyph.name),
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
