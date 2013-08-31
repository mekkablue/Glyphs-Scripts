#MenuTitle: Flashify Pixels
"""Adds small bridges to diagonal pixel connections (where two pixel corners touch). Otherwise your counters may be lost in the Flash text engine."""

import GlyphsApp

Font    = Glyphs.font
layers  = Font.selectedLayers

def karo( x, y ):
	koordinaten = [ [x-1,y], [x,y-1], [x+1,y], [x,y+1] ]
	
	karo = GSPath()
	for xy in koordinaten:
		newnode = GSNode()
		newnode.type = GSLINE
		newnode.position = (xy[0], xy[1])
		karo.nodes.append( newnode )
	karo.closed = True

	return karo

def process( thisLayer ):
	thisLayer.setDisableUpdates()
	thisLayer.parent.beginUndo()
	
	purePathsLayer = thisLayer.copyDecomposedLayer()
	purePathsLayer.removeOverlap()
	
	coordinatelist  = []
	for thisPath in purePathsLayer.paths:
		for thisNode in thisPath.nodes:
			coordinatelist.append([ thisNode.x, thisNode.y ])
	
	mylength = len( coordinatelist )
	
	for cur1 in range( mylength ):
		for cur2 in range( cur1+1, mylength, 1 ):
			if coordinatelist[cur1] == coordinatelist[cur2]:
				[ my_x, my_y ] = coordinatelist[ cur1 ]
				thisLayer.paths.append( karo( my_x, my_y ) )
				print thisLayer.parent.name, ":", my_x, my_y
	
	thisLayer.parent.endUndo()
	thisLayer.setEnableUpdates()

print "Flashifying " + str( Font.familyName )

oldGridstep = Font.gridLength
if oldGridstep > 1:
	Font.gridLength = 1

for thisLayer in layers:
	process( thisLayer )

Font.gridLength = oldGridstep