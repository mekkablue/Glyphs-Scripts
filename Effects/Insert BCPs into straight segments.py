#MenuTitle: Insert BCPs into straight segments Kopie
# -*- coding: utf-8 -*-
"""Inserts BCPs into straight segments of selected glyphs. The opposite of what the Tidy Up Paths command does. Useful if you want to bend the shape later."""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers
minimumLength = 20.0

def triplets( x1, y1, x2, y2 ):
	third1 = NSValue.valueWithPoint_(NSMakePoint( (x1 * 2 + x2 ) / 3,  ( y1 * 2 + y2 ) / 3))
	third2 = NSValue.valueWithPoint_(NSMakePoint( ( x1 + x2 * 2 ) / 3, ( y1 + y2 * 2 ) / 3))
	return (third1, third2)

def segmentLength( Node1, Node2 ):
	cath1 = Node2.x - Node1.x
	cath2 = Node2.y - Node1.y
	return ( cath1 ** 2 + cath2 ** 2 ) ** 0.5

def addBCPs( thisLayer ):
	virtualPaths = []
	
	for thisPath in thisLayer.paths:
		Segments = []
		for thisSegment in thisPath.segments:
			Point1 = thisSegment[0].pointValue()
			Point2 = thisSegment[1].pointValue()
			if len(thisSegment) == 2 and segmentLength( Point1, Point2 ) > minimumLength:
				newSegment = list(thisSegment)
				[ BCP1, BCP2 ] = triplets( Point1.x, Point1.y, Point2.x, Point2.y )
				newSegment.insert(1, BCP1)
				newSegment.insert(2, BCP2)
				Segments.append(newSegment)
			else:
				Segments.append(thisSegment)
			
		thisPath.segments = Segments
	
	
for thisLayer in selectedLayers:
	print "Processing", thisLayer.parent.name
	thisLayer.setDisableUpdates()
	thisLayer.parent.beginUndo()
	addBCPs( thisLayer )
	thisLayer.parent.endUndo()
	thisLayer.setEnableUpdates()
