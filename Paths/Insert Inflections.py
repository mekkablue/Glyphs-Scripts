#MenuTitle: Insert Inflections
# -*- coding: utf-8 -*-
"""Inserts Nodes on inflections on all paths in the selected glyphs."""

import GlyphsApp
Font = Glyphs.font
selectedLayers = Font.selectedLayers

def divideCurve(P0, P1, P2, P3, t):
	Q0x = P0.x + ( ( P1.x - P0.x) * t )
	Q0y = P0.y + ( ( P1.y - P0.y) * t )
	Q1x = P1.x + ( ( P2.x - P1.x) * t )
	Q1y = P1.y + ( ( P2.y - P1.y) * t )
	Q2x = P2.x + ( ( P3.x - P2.x) * t )
	Q2y = P2.y + ( ( P3.y - P2.y) * t )
	R0x = Q0x + ((Q1x-Q0x)*t)
	R0y = Q0y + ((Q1y-Q0y)*t)
	R1x = Q1x + ((Q2x-Q1x)*t)
	R1y = Q1y + ((Q2y-Q1y)*t)
	Sx = R0x + ((R1x-R0x)*t)
	Sy = R0y + ((R1y-R0y)*t)
	return (P0, NSMakePoint(Q0x, Q0y), NSMakePoint(R0x, R0y), NSMakePoint(Sx, Sy), NSMakePoint(R1x, R1y), NSMakePoint(Q2x, Q2y), P3)

def computeInflection( p1, p2, p3, p4 ):
	Result = []
	
	# aux variables involved in computing the numerator
	# in the formula (fraction) of a cubic Bezier curvature
	# (see http://www.caffeineowl.com/graphics/2d/vectorial/cubic-inflexion.html)
	ax = p2.x - p1.x
	ay = p2.y - p1.y
	bx = p3.x - p2.x - ax
	by = p3.y - p2.y - ay
	cx = p4.x - p3.x - ax - bx - bx
	cy = p4.y - p3.y - ay - by - by
	
	# coefficients of the polynomial in t that acts as the numerator
	# of the formula (fraction) of a cubic Bezier curvature.
	c0 = ( ax * by ) - ( ay * bx )
	c1 = ( ax * cy ) - ( ay * cx )
	c2 = ( bx * cy ) - ( by * cx )
	
	if abs(c2) > 0.00001: # quadratic equation
		discr = ( c1 ** 2 ) - ( 4 * c0 * c2)
		c2 *= 2
		
		if abs(discr) < 0.000001:
			root = -c1 / c2
			if (root > 0.001) and (root < 0.99):
				Result.append(root)
				
		elif discr > 0:
			discr = discr ** 0.5
			root = ( -c1 - discr ) / c2
			if (root > 0.001) and (root < 0.99):  #collect it only if between [0..1]
				Result.append(root)
			
			root = ( -c1 + discr ) / c2
			if (root > 0.001) and (root < 0.99): #collect it only if between [0..1]
				Result.append(root)
	elif c1 != 0.0: # linear equation c1*t+c0=0
		root = - c0 / c1
		if (root > 0.001) and (root < 0.99):
			Result.append(root)

	return Result


def process( thisLayer ):
	for ip in range(len(thisLayer.paths)):
		thisPath = thisLayer.paths[ip]
		newPathNodes = [ n for n in thisPath.nodes ]
		
		for i in range( len( thisPath.nodes ) - 3 )[::-1]:
			if thisPath.nodes[i].type != 65:
				nextTypes = [ thisPath.nodes[i+x].type for x in range(1,4) ]
				
				if nextTypes == [65, 65, 35]:# and thisPath.nodes[i].type != 65:
					nl = [ thisPath.nodes[x] for x in range(i,i+4) ]
					inflections = computeInflection( nl[0], nl[1], nl[2], nl[3] )
					
					if len(inflections) == 1:
						inflectionTime = inflections[0]
						listOfNewNodes = divideCurve( nl[0], nl[1], nl[2], nl[3], inflectionTime )[1:-1]
						listOfNewGSNodes = [ GSNode(n[0],n[1]) for n in zip( listOfNewNodes, [65,65,35,65,65] ) ]
						newPathNodes[i+1:i+3] = listOfNewGSNodes
						
		thisPath.setNodes_( newPathNodes )

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()	
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()


