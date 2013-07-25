#MenuTitle: Tunnify
# -*- coding: utf-8 -*-
"""Averages out the handles of selected path segments."""

import GlyphsApp
Doc  = Glyphs.currentDocument
selectedLayer = Doc.selectedLayers()[0]
selectedGlyph = selectedLayer.parent
selection = selectedLayer.selection()

def intersect( x1, y1,  x2, y2,  x3, y3,  x4, y4 ):
	"""Calculates the intersection of line P1-P2 with P3-P4."""

	# Please help me: Can I do this simpler? It's been a while...
	slope12vertical = False
	slope34vertical = False
	
	try:
		slope12 = ( float(y2) - float(y1) ) / ( float(x2) - float(x1) )
	except:
		slope12vertical = True

	try:
		slope34 = ( float(y4) - float(y3) ) / ( float(x4) - float(x3) )
	except:
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

def tunnify( segment ):
	"""Calculates the average curvature for Bezier curve segment P1, P2, P3, P4 and returns new values for P2, P3"""
	[P1, P2, P3, P4] = segment
	[x1, y1] = P1
	[x2, y2] = P2
	[x3, y3] = P3
	[x4, y4] = P4
	
	
	
	# Fix Illustrator's zero-handles: 
	if [x1, y1] == [x2, y2]:
		x2, y2 = bezier( x1, y1,  x2, y2,  x3, y3,  x4, y4,  0.15)
		tunnifiedPercentage = 0.627
		xInt, yInt = intersect( x1, y1,  x2, y2,  x3, y3,  x4, y4 )
	elif [x3, y3] == [x4, y4]:
		x3, y3 = bezier( x1, y1,  x2, y2,  x3, y3,  x4, y4,  0.85)
		tunnifiedPercentage = 0.627
		xInt, yInt = intersect( x1, y1,  x2, y2,  x3, y3,  x4, y4 )
	else:
	# Calculate average percentage:
		xInt, yInt = intersect( x1, y1,  x2, y2,  x3, y3,  x4, y4 )
		percentageP1P2 = pointdistance( x1, y1, x2, y2 ) / pointdistance( x1, y1, xInt, yInt )
		percentageP3P4 = pointdistance( x4, y4, x3, y3 ) / pointdistance( x4, y4, xInt, yInt )
		tunnifiedPercentage = ( percentageP1P2 + percentageP3P4 ) / 2.0
	
	print tunnifiedPercentage * 100
	
	# Calculate new handle positions:
	x_handle1 = x1 + tunnifiedPercentage * ( xInt - x1 )
	y_handle1 = y1 + tunnifiedPercentage * ( yInt - y1 )
	x_handle2 = x4 + tunnifiedPercentage * ( xInt - x4 )
	y_handle2 = y4 + tunnifiedPercentage * ( yInt - y4 )
	
	return x_handle1, y_handle1, x_handle2, y_handle2
	
#selectedGlyph.undoManager().beginUndoGrouping()
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

#selectedGlyph.undoManager().beginUndoGrouping()
selectedGlyph.endUndo()
