#MenuTitle: Flashify Pixels
"""Adds bridges to diagonal pixel connections."""

import GlyphsApp

Font    = Glyphs.font
Doc     = Glyphs.currentDocument
layers  = Doc.selectedLayers()
removeOverlapFilter = NSClassFromString("GlyphsFilterRemoveOverlap").alloc().init()

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
	thisLayer.parent.undoManager().beginUndoGrouping()

	coordinatelist  = []
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			coordinatelist.append([ thisNode.x, thisNode.y ])

	mylength = len( coordinatelist )
	
	for cur1 in range( mylength ):
		for cur2 in range( cur1+1, mylength, 1 ):
			if coordinatelist[cur1] == coordinatelist[cur2]:
				[ my_x, my_y ] = coordinatelist[ cur1 ]
				myPath = karo( my_x, my_y )
				thisLayer.paths.append( myPath )
				print thisLayer.parent.name, ":", my_x, my_y

	thisLayer.parent.undoManager().endUndoGrouping()

print "Flashifying " + str( Font.familyName )

oldGridstep = Font.gridLength
if oldGridstep > 1:
	Font.gridLength = 1

Font.disableUpdateInterface()

for thisLayer in layers:
	removeOverlapFilter.runFilterWithLayer_error_( thisLayer, None )
	process( thisLayer )
	removeOverlapFilter.runFilterWithLayer_error_( thisLayer, None )

Font.enableUpdateInterface()

Font.gridLength = oldGridstep