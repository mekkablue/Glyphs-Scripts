#MenuTitle: Flashify Pixels
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds small bridges to diagonal pixel connections (where two pixel corners touch). Otherwise your counters may be lost in the Flash text engine (hence the name of the script).
"""

from Foundation import NSClassFromString

Font    = Glyphs.font
layers  = Font.selectedLayers
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
	thisLayer.parent.beginUndo()

	purePathsLayer = thisLayer.copyDecomposedLayer()
	removeOverlapFilter.runFilterWithLayer_error_( purePathsLayer, None )
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
				print("  %s: %i %i" % (thisLayer.parent.name, my_x, my_y))

	thisLayer.parent.endUndo()

print("Flashifying %s..." % Font.familyName)

oldGridstep = Font.gridLength
if oldGridstep > 1:
	Font.gridLength = 1

Font.disableUpdateInterface()
try:
	for thisLayer in layers:
		process( thisLayer )
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	Font.enableUpdateInterface() # re-enables UI updates in Font View

Font.gridLength = oldGridstep