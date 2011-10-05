#MenuTitle: Flashify Pixels
"""Adds bridges to diagonal pixel connections."""

import GlyphsApp

Font    = Glyphs.orderedDocuments()[0].font
Doc     = Glyphs.currentDocument
layers  = Doc.selectedLayers()
removeOverlapFilter = NSClassFromString("GlyphsFilterRemoveOverlap").alloc().init()

def karo( x, y ):
	koordinaten = [ [x-1,y], [x,y-1], [x+1,y], [x,y+1] ]

	karo = GSPath()
	for xy in koordinaten:
		newnode = GSNode()
		newnode.type = GSLINE
		newnode.setPosition_((xy[0], xy[1]))
		karo.addNode_( newnode )
	karo.setClosePath_( True )

	return karo

def process( thisglyph ):
	thisglyph.undoManager().disableUndoRegistration()

	FontMaster = Doc.selectedFontMaster()
	thislayer = thisglyph.layers[FontMaster.id]
	coordinatelist  = []
	for thispath in thislayer.paths:
		for thisnode in thispath.nodes:
			coordinatelist.append([ thisnode.x, thisnode.y ])

	mylength = len( coordinatelist )
	
	for cur1 in range( mylength ):
		for cur2 in range( cur1+1, mylength, 1 ):
			if coordinatelist[cur1] == coordinatelist[cur2]:
				[ my_x, my_y ] = coordinatelist[ cur1 ]
				mypath = karo( my_x, my_y )
				thislayer.addPath_( mypath )
				print thisglyph.name, ":", my_x, my_y

	thisglyph.undoManager().enableUndoRegistration()

print "Flashifying " + str( Font.familyName )

if Font.gridLength > 1:
	print "Set gridstep to 1."
	Font.gridLength = 1

Font.willChangeValueForKey_("glyphs")

for thisLayer in layers:
	removeOverlapFilter.runFilterWithLayer_error_( thisLayer, None )
	thisGlyph = thisLayer.parent
	process( thisGlyph )
	#removeOverlapFilter.runFilterWithLayer_error_(thisLayer, None)

Font.didChangeValueForKey_("glyphs")
