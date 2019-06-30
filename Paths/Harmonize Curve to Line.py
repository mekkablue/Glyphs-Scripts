#MenuTitle: Harmonize Curve to Line
# -*- coding: utf-8 -*-
__doc__="""
Maximizes opposing handles and reduces adjacent handles of line segments.
"""

def intersectionWithNSPoints( pointA, pointB, pointC, pointD ):
	"""
	Returns an NSPoint of the intersection AB with CD.
	Or False if there is no intersection
	"""
	try:
		x1, y1 = pointA.x, pointA.y
		x2, y2 = pointB.x, pointB.y
		x3, y3 = pointC.x, pointC.y
		x4, y4 = pointD.x, pointD.y
	
		try:
			slope12 = ( float(y2) - float(y1) ) / ( float(x2) - float(x1) )
		except:
			# division by zero if vertical
			slope12 = None
		
		try:
			slope34 = ( float(y4) - float(y3) ) / ( float(x4) - float(x3) )
		except:
			# division by zero if vertical
			slope34 = None
	
		if slope12 == slope34:
			# parallel, no intersection
			return None
		elif slope12 is None:
			# first line is vertical
			x = x1
			y = slope34 * ( x - x3 ) + y3
		elif slope34 is None:
			# second line is vertical
			x = x3
			y = slope12 * ( x - x1 ) + y1
		else:
			# both lines have an angle
			x = ( slope12 * x1 - y1 - slope34 * x3 + y3 ) / ( slope12 - slope34 )
			y = slope12 * ( x - x1 ) + y1
		
		intersectionPoint = NSPoint( x, y )
		if bothPointsAreOnSameSideOfOrigin( intersectionPoint, pointB, pointA ) and bothPointsAreOnSameSideOfOrigin( intersectionPoint, pointC, pointD ):
			if pointIsBetweenOtherPoints( intersectionPoint, pointB, pointA ) or pointIsBetweenOtherPoints( intersectionPoint, pointC, pointD ):
				return None
			return intersectionPoint
		else:
			return None
	
	except Exception as e:
		print str(e)
		import traceback
		print traceback.format_exc()
		return None

def pointDistance( P1, P2 ):
	"""Calculates the distance between P1 and P2."""
	x1, y1 = P1.x, P1.y
	x2, y2 = P2.x, P2.y
	dist = ( ( float(x2) - float(x1) ) ** 2 + ( float(y2) - float(y1) ) **2 ) ** 0.5
	return dist

def bezier( x1, y1,  x2,y2,  x3,y3,  x4,y4,  t ):
	x = x1*(1-t)**3 + x2*3*t*(1-t)**2 + x3*3*t**2*(1-t) + x4*t**3
	y = y1*(1-t)**3 + y2*3*t*(1-t)**2 + y3*3*t**2*(1-t) + y4*t**3
	return x, y

def bothPointsAreOnSameSideOfOrigin( pointA, pointB, pointOrigin ):
	returnValue = True
	xDiff = (pointA.x-pointOrigin.x) * (pointB.x-pointOrigin.x)
	yDiff = (pointA.y-pointOrigin.y) * (pointB.y-pointOrigin.y)
	if xDiff <= 0.0 and yDiff <= 0.0:
		returnValue = False
	return returnValue

def pointIsBetweenOtherPoints( thisPoint, otherPointA, otherPointB) :
	returnValue = False

	xDiffAB = otherPointB.x - otherPointA.x
	yDiffAB = otherPointB.y - otherPointA.y
	xDiffAP = thisPoint.x - otherPointA.x
	yDiffAP = thisPoint.y - otherPointA.y
	xDiffFactor = divideAndTolerateZero( xDiffAP, xDiffAB )
	yDiffFactor = divideAndTolerateZero( yDiffAP, yDiffAB )

	if xDiffFactor:
		if 0.0<=xDiffFactor<=1.0:
			returnValue = True

	if yDiffFactor:
		if 0.0<=xDiffFactor<=1.0:
			returnValue = True
	
	return returnValue

def divideAndTolerateZero( dividend, divisor ):
	if float(divisor) == 0.0:
		return None
	else:
		return dividend/divisor

def handleLength(a,b,intersection):
	return pointDistance(a,b)/pointDistance(a,intersection)
	
def moveHandle(a,b,intersection,bPercentage):
	x = a.x + (intersection.x-a.x) * bPercentage
	y = a.y + (intersection.y-a.y) * bPercentage
	return NSPoint(x,y)


Font = Glyphs.font

if len(Font.selectedLayers) > 1:
	selectionCounts = False
elif not Font.selectedLayers[0].selection:
	selectionCounts = False
else:
	selectionCounts = True
	
for selectedLayer in Font.selectedLayers:
	selectedGlyph = selectedLayer.parent
	selectedGlyph.beginUndo()
	
	# put original state in background:
	selectedLayer.contentToBackgroundCheckSelection_keepOldBackground_(False,False)
	
	for path in selectedLayer.paths:
		for n in path.nodes:
			processedHandles = []
			if (n.selected or not selectionCounts) and n.type == OFFCURVE:
				
				# determine the segment:
				if n.prevNode.type == OFFCURVE:
					a = n.prevNode.prevNode
					b = n.prevNode
					c = n
					d = n.nextNode
				else:
					a = n.prevNode
					b = n
					c = n.nextNode
					d = n.nextNode.nextNode
			
				if not a in processedHandles and not b in processedHandles:
					
					# intersection of the magic triangle:
					intersection = intersectionWithNSPoints( a.position, b.position, c.position, d.position )
					
					if intersection:
						# calculate percentages:
						bLength = handleLength(a,b,intersection)
						cLength = handleLength(d,c,intersection)
						shortLength = (abs(bLength) + abs(cLength) - 1.0) - (1.0-abs(bLength))*(1.0-abs(cLength))
						
						if d.nextNode.type == LINE and a.prevNode.type != LINE and d.connection == GSSMOOTH:
							# max handle:
							b.position = intersection
							# reduced handle:
							c.position = moveHandle(d,c,intersection,shortLength)
							
						elif a.prevNode.type == LINE and d.nextNode.type != LINE and a.connection == GSSMOOTH:
							# max handle:
							c.position = intersection
							# reduced handle:
							b.position = moveHandle(a,b,intersection,shortLength)
						
						# mark handles as processed:
						processedHandles.append(a)
						processedHandles.append(b)

	selectedGlyph.endUndo()
