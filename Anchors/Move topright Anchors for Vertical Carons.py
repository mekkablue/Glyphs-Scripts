#MenuTitle: Move vertical caron anchors to x-height intersection
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
On all layers of selected glyphs, moves all topright and _topright anchors to the rightmost intersection of the outline with the x-height. Verbose report in Macro Window.
"""

from Foundation import NSPoint
import math

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

def intersectionOnXHeight( thisLayer ):
	"""Returns the NSPoint of the rightmost intersection with the x-height."""
	goodMeasure = 0
	xHeight = thisLayer.master.xHeight
	if not xHeight:
		xHeight = 500 # fallback value
	
	originX = thisLayer.bounds.origin.x - goodMeasure
	originPoint = NSPoint( originX, xHeight )
	targetX = originX + thisLayer.bounds.size.width + goodMeasure
	targetPoint = NSPoint( targetX, xHeight )
	
	listOfIntersections = sliceIntersections( thisLayer, originPoint, targetPoint )
	
	# print("intersectionOnXHeight:", listOfIntersections, originPoint, targetPoint) # DEBUG
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
	
	xHeight = thisLayer.master.xHeight
	
	if toprightAnchor:
		xHeightOutlineIntersection = intersectionOnXHeight( thisLayer )
		if xHeightOutlineIntersection:
			if isAccent:
				xHeightOutlineIntersection.x = 0.0
			toprightAnchor.position = xHeightOutlineIntersection
			print("  ✅ %s: moved %s to %.1f, %.1f." % (thisLayer.name, toprightAnchor.name, toprightAnchor.x, toprightAnchor.y))
			
			# selects anchor on thisLayer:
			itemsToBeSelected = NSMutableArray.arrayWithObject_( toprightAnchor )
			thisLayer.setSelection_( itemsToBeSelected )
		else:
			# put it on the x-height, at least:
			toprightAnchor.y = 0
			print("  ⚠️ %s: moved %s to xHeight. No outline intersection on x-height." % (thisLayer.name, toprightAnchor.name))
	else:
		print("  ❓ %s: no anchor topright or _topright found." % thisLayer.name)

try:
	thisFont.disableUpdateInterface() # suppresses UI updates in Font View

	Glyphs.clearLog() # clears macro window log
	print("Move vertical caron anchors to x-height intersection:")

	for thisGlyph in [l.parent for l in selectedLayers]:
		print("\n🔠 Glyph: %s" % thisGlyph.name)
		# thisGlyph.beginUndo() # undo grouping causes crashes
		for thisLayer in thisGlyph.layers:
			if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
				process( thisLayer )
		# thisGlyph.endUndo() # undo grouping causes crashes

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
