#MenuTitle: Dekink
# -*- coding: utf-8 -*-
__doc__="""
Synchronize node distance proportions for angled smooth connections through all masters, thus avoiding interpolation kinks. Select one or more smoothly connected nodes and run the script.
"""

import GlyphsApp

Font = Glyphs.font
currentMaster = Font.selectedFontMaster
currentLayer = Font.selectedLayers[0]
currentGlyph = currentLayer.parent

def dekink( myMaster, myGlyph, pathindex, nodeindex, proportion ):
	try:
		myFont = myGlyph.parent
		for m in myFont.masters:
			if m != myMaster:
				p = myGlyph.layers[m.id].paths[pi]
				pathlength = len(p)
				n0 = p.nodes[(nodeindex-1) % pathlength]
				n1 = p.nodes[ nodeindex ]
				n2 = p.nodes[(nodeindex+1) % pathlength]
			
				n1.x = n0.x + proportion * (n2.x - n0.x)
				n1.y = n0.y + proportion * (n2.y - n0.y)
	
		return True
		
	except Exception, e:
		print e
		return False 

try:
	if currentGlyph.mastersCompatible():
		s = list( currentLayer.selection() )
		
		# find the indices for selected nodes:
		for n in [n for n in s if n.connection == GSSMOOTH]:
			for pi in range( len( currentLayer.paths )):
				pathlength = len( currentLayer.paths[pi].nodes )
				currentNodes = currentLayer.paths[pi].nodes
				for ni in range( pathlength ):
					if currentNodes[ni] == n:
						n0 = currentNodes[(ni-1) % pathlength]
						n1 = currentNodes[ ni ]
						n2 = currentNodes[(ni+1) % pathlength]
					
						longX  = n2.x - n0.x
						longY  = n2.y - n0.y
						shortX = n1.x - n0.x
						shortY = n1.y - n0.y

						if longY == 0.0 or longX == 0.0:
							print "Ignoring node at %i, %i because the segment is straight." % ( n1.x, n1.y )
						else:
							proportion = ( shortX / longX + shortY / longY ) / 2.0
						
							if not dekink( currentMaster, currentGlyph, pi, ni, proportion ):
								print "Error: dekinking failed."
	else:
		print "Error: masters not compatible."
	
except Exception, e:
	raise e
