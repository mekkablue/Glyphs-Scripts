#MenuTitle: Guideline through Selected Nodes
# -*- coding: utf-8 -*-
"""Creates a guideline through the currently selected two nodes."""

import GlyphsApp
import math

Font = Glyphs.font
thisLayer = Font.selectedLayers[0]
selection = thisLayer.selection()

if len( selection ) == 2:
	firstPoint = selection[0]
	secondPoint = selection[1]
	xDiff = firstPoint.x - secondPoint.x
	
	myGuideline = GSGuideLine()
	myGuideline.position = NSPoint( firstPoint.x, firstPoint.y )
	
	if xDiff != 0.0:
		tangens = (firstPoint.y - secondPoint.y) / xDiff
		myGuideline.angle = math.atan( tangens ) * 180.0 / math.pi
	else:
		myGuideline.angle = 90

	thisLayer.addGuideLine_( myGuideline )
	thisLayer.setSelection_(NSMutableArray.arrayWithObject_(myGuideline))
	


