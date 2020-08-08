#MenuTitle: Move ogonek anchors to baseline intersection
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
In selected glyphs, moves all ogonek and _ogonek anchors to the rightmost intersection of the outline with the baseline. Verbose report in 
"""

import math
from Foundation import NSPoint, NSBundle

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def angle( firstPoint, secondPoint ):
	xDiff = firstPoint.x - secondPoint.x
	yDiff = firstPoint.y - secondPoint.y
	tangens = yDiff / xDiff
	angle = math.atan( tangens ) * 180.0 / math.pi
	return angle

def sliceIntersections( thisLayer, startPoint, endPoint ):
	return thisLayer.calculateIntersectionsStartPoint_endPoint_( startPoint, endPoint )

def intersectionOnBaseline( thisLayer ):
	"""Returns the NSPoint of the rightmost intersection with the baseline."""
	goodMeasure = 1

	originX = thisLayer.bounds.origin.x - goodMeasure
	originPoint = NSPoint( originX, 0.0 )
	targetX = originX + thisLayer.bounds.size.width + goodMeasure
	targetPoint = NSPoint( targetX, 0.0 )
	
	intersections = sliceIntersections( thisLayer, originPoint, targetPoint )
	
	
	# print("intersectionOnBaseline:", intersections, originPoint, targetPoint)
	if len(intersections) > 2:
		rightmostIntersection = intersections[-2].pointValue()
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
			print("✅ Layer %s: ogonek anchor moved to %.1f, %.1f." % (thisLayer.name, ogonekAnchor.x, ogonekAnchor.y))
			
			# selects anchor on thisLayer:
			itemsToBeSelected = NSMutableArray.arrayWithObject_( ogonekAnchor )
			thisLayer.setSelection_( itemsToBeSelected )
		else:
			# put it on the baseline, at least:
			ogonekAnchor.y = 0
			print("⚠️ Layer %s: ogonek moved to baseline, but there is no outline intersection." % thisLayer.name )
	else:
		print("❓ Layer %s: No anchor ogonek or _ogonek found." % thisLayer.name )

try:
	thisFont.disableUpdateInterface() # suppresses UI updates in Font View

	Glyphs.clearLog() # clears macro window log
	print("Move ogonek anchors to baseline intersection:\n")

	for thisGlyph in [l.parent for l in selectedLayers]:
		print("Processing: %s" % thisGlyph.name)
		thisGlyph.beginUndo() # begin undo grouping
		for thisLayer in thisGlyph.layers:
			if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
				process( thisLayer )
		thisGlyph.endUndo()   # end undo grouping

	print("\nDone.")
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	print(e)
	print()
	import traceback
	print(traceback.format_exc())
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
