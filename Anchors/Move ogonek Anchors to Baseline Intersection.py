#MenuTitle: Move ogonek anchors to baseline intersection
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Moves all ogonek and _ogonek anchors to the rightmost intersection of the outline with the baseline.
"""

import math
from Foundation import NSPoint, NSBundle

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

GLYPHSAPPVERSION = NSBundle.bundleForClass_(NSClassFromString("GSMenu")).infoDictionary().objectForKey_("CFBundleShortVersionString")
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

def intersectionOnBaseline( thisLayer ):
	"""Returns the NSPoint of the rightmost intersection with the baseline."""
	goodMeasure = 1

	originX = thisLayer.bounds.origin.x - goodMeasure
	originPoint = NSPoint( originX, 0.0 )
	targetX = originX + thisLayer.bounds.size.width + goodMeasure
	targetPoint = NSPoint( targetX, 0.0 )
	
	listOfIntersections = sliceIntersections( thisLayer, originPoint, targetPoint )
	
	print("intersectionOnBaseline:", listOfIntersections, originPoint, targetPoint)
	if listOfIntersections:
		rightmostIntersection = listOfIntersections[-2].pointValue()
		return rightmostIntersection
	else:
		return None
	

def process( thisLayer ):
	ogonekAnchor = thisLayer.anchors["ogonek"]
	if not ogonekAnchor:
		ogonekAnchor = thisLayer.anchors["_ogonek"]
	
	if ogonekAnchor:
		baselineOutlineIntersection = intersectionOnBaseline( thisLayer )
		if baselineOutlineIntersection:
			ogonekAnchor.position = baselineOutlineIntersection
			print("  Moved to %.1f, %.1f." % (ogonekAnchor.x, ogonekAnchor.y))
			
			# selects anchor on thisLayer:
			itemsToBeSelected = NSMutableArray.arrayWithObject_( ogonekAnchor )
			thisLayer.setSelection_( itemsToBeSelected )
		else:
			# put it on the baseline, at least:
			ogonekAnchor.y = 0
			print("  No outline intersection on baseline.")
	else:
		print("  No anchor ogonek or _ogonek found.")

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print("Processing", thisGlyph.name)
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
