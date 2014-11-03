#MenuTitle: Insert Inflections
# -*- coding: utf-8 -*-
__doc__="""
Inserts Nodes on inflections on all paths in the selected glyphs.
"""

import GlyphsApp
Font = Glyphs.font
selectedLayers = Font.selectedLayers

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
	for ip in range( len( thisLayer.paths )):
		thisPath = thisLayer.paths[ip]
		numberOfNodes = len( thisPath.nodes )

		for i in range(numberOfNodes-1, -1, -1):
			node = thisPath.nodes[i]
			if node.type == 35: #CURVE
				nl = [ thisPath.nodes[ (x+numberOfNodes)%numberOfNodes ] for x in range( i-3, i+1 ) ]
				inflections = computeInflection( nl[0], nl[1], nl[2], nl[3] )
				if len(inflections) == 1:
					inflectionTime = inflections[0]
					thisPath.insertNodeWithPathTime_( i + inflectionTime )

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()


