#MenuTitle: Report Area in Square Units
# -*- coding: utf-8 -*-
__doc__="""
Calculates the area of each selected glyph, and outputs it in square units. Increase precision by changing the value for PRECISION in line 9 (script will slow down).
"""

import GlyphsApp

PRECISION = 2 # higher numbers = more precision, but slower

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

GLYPHSAPPVERSION = NSBundle.bundleForClass_(GSMenu).infoDictionary().objectForKey_("CFBundleShortVersionString")
if GLYPHSAPPVERSION.startswith("1."):
	measurementTool = NSClassFromString("GlyphsToolMeasurement").alloc().init()
else:
	measurementTool = NSClassFromString("GSGuideLine")
	
def sliceIntersections( thisLayer, startPoint, endPoint ):
	if GLYPHSAPPVERSION.startswith("2."):
		return thisLayer.calculateIntersectionsStartPoint_endPoint_( startPoint, endPoint )	
	else:
		return measurementTool.calculateIntersectionsForLayer_startPoint_endPoint_( thisLayer, startPoint, endPoint )	

def sizeOfSlice( thisLayer, y ):
	theseBounds = thisLayer.bounds
	startPointX = theseBounds.origin.x - 10
	endPointX = startPointX + theseBounds.size.width + 20
	startPoint = NSPoint( startPointX, y )
	endPoint   = NSPoint( endPointX, y )
	listOfIntersections = sliceIntersections( thisLayer, startPoint, endPoint )
	totalLength = 0.0
	if listOfIntersections and len(listOfIntersections) >= 4:
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

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

# calculates areas for selected glyphs:
for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Area of %s:" % (thisGlyph.name),
	process( thisLayer )
