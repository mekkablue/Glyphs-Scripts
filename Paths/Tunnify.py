#MenuTitle: Tunnify
# -*- coding: utf-8 -*-
__doc__="""
Averages out the handles of selected path segments.
"""

import GlyphsApp
Font = Glyphs.font
selectedLayer = Font.selectedLayers[0]
selectedGlyph = selectedLayer.parent
selection = selectedLayer.selection()

tunnifiedZeroLo = 0.43
tunnifiedZeroHi = 0.73

def intersect( x1, y1,  x2, y2,  x3, y3,  x4, y4 ):
	"""Calculates the intersection of line P1-P2 with P3-P4."""

	# Please help me: Can I do this simpler? It's been a while...
	slope12vertical = False
	slope34vertical = False
	
	try:
		slope12 = ( float(y2) - float(y1) ) / ( float(x2) - float(x1) )
	except: # division by zero
		slope12vertical = True

	try:
		slope34 = ( float(y4) - float(y3) ) / ( float(x4) - float(x3) )
	except: # division by zero
		slope34vertical = True
	
	if not slope12vertical and not slope34vertical:
		x = ( slope12 * x1 - y1 - slope34 * x3 + y3 ) / ( slope12 - slope34 )
		y = slope12 * ( x - x1 ) + y1
	elif slope12vertical:
		x = x1
		y = slope34 * ( x - x3 ) + y3
	elif slope34vertical:
		x = x3
		y = slope12 * ( x - x1 ) + y1
	
	return x, y
	
def pointdistance( x1, y1, x2, y2 ):
	"""Calculates the distance between P1 and P2."""
	dist = ( ( float(x2) - float(x1) ) ** 2 + ( float(y2) - float(y1) ) **2 ) ** 0.5
	return dist

def bezier( x1, y1,  x2,y2,  x3,y3,  x4,y4,  t ):
	x = x1*(1-t)**3 + x2*3*t*(1-t)**2 + x3*3*t**2*(1-t) + x4*t**3
	y = y1*(1-t)**3 + y2*3*t*(1-t)**2 + y3*3*t**2*(1-t) + y4*t**3
	return x, y

def xyAtPercentageBetweenTwoPoints( firstPoint, secondPoint, percentage ):
	"""
	Returns the x, y for the point at percentage
	(where 100 percent is represented as 1.0)
	between NSPoints firstPoint and secondPoint.
	"""
	x = firstPoint.x + percentage * ( secondPoint.x - firstPoint.x )
	y = firstPoint.y + percentage * ( secondPoint.y - firstPoint.y )
	return x, y

def handlePercentages( segment ):
	"""Calculates the handle distributions and intersection for segment P1, P2, P3, P4."""
	x1, y1 = segment[0]
	x2, y2 = segment[1]
	x3, y3 = segment[2]
	x4, y4 = segment[3]
	
	if [x1, y1] == [x2, y2]:
		# zero handle at beginning of segment
		xInt, yInt = x3, y3
		return tunnifiedZeroLo, tunnifiedZeroHi, xInt, yInt
	elif [x3, y3] == [x4, y4]:
		# zero handle at end of segment
		xInt, yInt = x2, y2
		return tunnifiedZeroHi, tunnifiedZeroLo, xInt, yInt
	else:
		# no zero handle, just bad distribution
		xInt, yInt = intersect( x1, y1,  x2, y2,  x3, y3,  x4, y4 )
		percentageP1P2 = pointdistance( x1, y1, x2, y2 ) / pointdistance( x1, y1, xInt, yInt )
		percentageP3P4 = pointdistance( x4, y4, x3, y3 ) / pointdistance( x4, y4, xInt, yInt )
		tunnifiedPercentage = ( percentageP1P2 + percentageP3P4 ) / 2
		return tunnifiedPercentage, tunnifiedPercentage, xInt, yInt

def tunnify( segment ):
	"""
	Calculates the average curvature for Bezier curve segment P1, P2, P3, P4,
	and returns new values for P2, P3.
	"""
	x1, y1 = segment[0]
	x4, y4 = segment[3]
	firstHandlePercentage, secondHandlePercentage, xInt, yInt = handlePercentages( segment )
	
	intersectionPoint = NSPoint( xInt, yInt )
	segmentStartPoint = NSPoint( x1, y1 )
	segmentFinalPoint = NSPoint( x4, y4 )
	
	firstHandleX,  firstHandleY  = xyAtPercentageBetweenTwoPoints( segmentStartPoint, intersectionPoint, firstHandlePercentage )
	secondHandleX, secondHandleY = xyAtPercentageBetweenTwoPoints( segmentFinalPoint, intersectionPoint, secondHandlePercentage )
	return firstHandleX, firstHandleY, secondHandleX, secondHandleY

selectedGlyph.beginUndo()

try:
	for thisPath in selectedLayer.paths:
		numOfNodes = len( thisPath.nodes )
		nodeIndexes = range( numOfNodes )
		
		for i in nodeIndexes:
			thisNode = thisPath.nodes[i]
			
			if thisNode in selection and thisNode.type == GSOFFCURVE:
				if thisPath.nodes[i-1].type == GSOFFCURVE:
					segmentNodeIndexes = [ i-2, i-1, i, i+1 ]
				else:
					segmentNodeIndexes = [ i-1, i, i+1, i+2 ]
				
				for x in range(len(segmentNodeIndexes)):
					segmentNodeIndexes[x] = segmentNodeIndexes[x] % numOfNodes
				
				thisSegment = [ [n.x, n.y] for n in [ thisPath.nodes[i] for i in segmentNodeIndexes ] ]
				x_handle1, y_handle1, x_handle2, y_handle2 = tunnify( thisSegment )
				thisPath.nodes[ segmentNodeIndexes[1] ].x = x_handle1
				thisPath.nodes[ segmentNodeIndexes[1] ].y = y_handle1
				thisPath.nodes[ segmentNodeIndexes[2] ].x = x_handle2
				thisPath.nodes[ segmentNodeIndexes[2] ].y = y_handle2
				
except Exception, e:
	print "Error:", e
	pass

selectedGlyph.endUndo()
