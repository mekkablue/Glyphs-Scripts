#MenuTitle: Flashify Pixels
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds small bridges to diagonal pixel connections (where two pixel corners touch). Otherwise your counters may be lost in the Flash text engine (hence the name of the script).
"""

def karo( x, y ):
	koordinaten = ([x-1,y], [x,y-1], [x+1,y], [x,y+1])
	karo = GSPath()
	for xy in koordinaten:
		newnode = GSNode()
		newnode.type = GSLINE
		newnode.position = (xy[0], xy[1])
		karo.nodes.append( newnode )
	karo.closed = True
	return karo

def process( thisLayer ):
	# thisLayer.parent.beginUndo() # undo grouping causes crashes

	count = 0
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
				myKaro = karo( my_x, my_y )
				if Glyphs.versionNumber >= 3:
					# GLYPHS 3
					thisLayer.shapes.append( myKaro )
				else:
					# GLYPHS 2
					thisLayer.paths.append( myKaro )
				count += 1

	# thisLayer.parent.endUndo() # undo grouping causes crashes
	return count

Glyphs.clearLog()
thisFont = Glyphs.font
print("Flashifying %s...\n" % thisFont.familyName)

thisFont.disableUpdateInterface()
try:
	oldGridstep = thisFont.grid
	if oldGridstep > 1:
		thisFont.grid = 1
	layers = thisFont.selectedLayers
	totalCount = 0
	for thisLayer in layers:
		karoCount = process( thisLayer )
		totalCount += karoCount
		print("🔠 Added %i diamonds in %s" % (karoCount, thisLayer.parent.name))
	print("\nDone. Total diamond count: %i." % totalCount)
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
	
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View

# thisFont.grid = oldGridstep