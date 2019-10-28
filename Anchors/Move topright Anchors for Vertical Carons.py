#MenuTitle: Move vertical caron anchors to x-height intersection
# -*- coding: utf-8 -*-
__doc__="""
Moves all topright and _topright anchors to the rightmost intersection of the outline with the x-height.
"""

from Foundation import NSPoint
import math

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

GLYPHSAPPVERSION = NSBundle.bundleForClass_(GSMenu).infoDictionary().objectForKey_("CFBundleShortVersionString")
GLYPHS_IS_OLD = GLYPHSAPPVERSION.startswith("1.")
measurementTool = None
if GLYPHS_IS_OLD:
	measurementTool = NSClassFromString("GlyphsToolMeasurement").alloc().init()

def angle( firstPoint, secondPoint ):
	xDiff = firstPoint.x - secondPoint.x
	yDiff = firstPoint.y - secondPoint.y
	tangens = yDiff / xDiff
	angle = math.atan( tangens ) * 180.0 / math.pi
	return angle

def sliceIntersections( thisLayer, startPoint, endPoint ):
	if measurementTool:
		return measurementTool.calculateIntersectionsForLayer_startPoint_endPoint_( thisLayer, startPoint, endPoint )
	else:
		return thisLayer.calculateIntersectionsStartPoint_endPoint_( startPoint, endPoint )

def intersectionOnXHeight( thisLayer ):
	"""Returns the NSPoint of the rightmost intersection with the x-height."""
	goodMeasure = 1
	thisFont = thisLayer.parent.parent
	xHeight = thisFont.masters[thisLayer.associatedMasterId].xHeight
	
	originX = thisLayer.bounds.origin.x - goodMeasure
	originPoint = NSPoint( originX, xHeight )
	targetX = originX + thisLayer.bounds.size.width + goodMeasure
	targetPoint = NSPoint( targetX, xHeight )
	
	listOfIntersections = sliceIntersections( thisLayer, originPoint, targetPoint )
	
	print "intersectionOnXHeight:", listOfIntersections, originPoint, targetPoint
	if listOfIntersections:
		rightmostIntersection = listOfIntersections[-2].pointValue()
		return rightmostIntersection
	else:
		return None
	

def process( thisLayer ):
	toprightAnchor = thisLayer.anchors["topright"]
	isAccent = False
	if not toprightAnchor:
		toprightAnchor = thisLayer.anchors["_topright"]
		isAccent = True
	
	if toprightAnchor:
		xHeightOutlineIntersection = intersectionOnXHeight( thisLayer )
		if xHeightOutlineIntersection:
			if isAccent:
				xHeightOutlineIntersection.x = 0.0
			toprightAnchor.position = xHeightOutlineIntersection
			print "  Moved to %.1f, %.1f." % (toprightAnchor.x, toprightAnchor.y)
			
			# selects anchor on thisLayer:
			itemsToBeSelected = NSMutableArray.arrayWithObject_( toprightAnchor )
			thisLayer.setSelection_( itemsToBeSelected )
		else:
			# put it on the x-height, at least:
			toprightAnchor.y = 0
			print "  No outline intersection on x-height."
	else:
		print "  No anchor topright or _topright found."

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
