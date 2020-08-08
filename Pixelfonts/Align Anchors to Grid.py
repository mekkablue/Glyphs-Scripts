#MenuTitle: Align Anchors to Grid
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Looks for anchors not on the grid and rounds their coordinate to the closest grid.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

pixelwidth = Font.gridLength

def process( thisLayer ):
	if len( thisLayer.anchors ) != 0:
		thisLayer.parent.beginUndo()
		
		anchorList = thisLayer.anchors
		
		for a in anchorList:
			xrest = a.x % pixelwidth
			yrest = a.y % pixelwidth
			
			if xrest or yrest:
				oldX = a.x
				oldY = a.y
				a.position = ( round( a.x/pixelwidth ) * pixelwidth, round( a.y/pixelwidth ) * pixelwidth )
				print("🔡 %s ⚓️ %s %i|%i --> %i|%i" % ( thisLayer.parent.name, a.name, int(oldX), int(oldY), int(a.x), int(a.y) ))
				
		thisLayer.parent.endUndo()

Font.disableUpdateInterface()
try:
	for thisLayer in selectedLayers:
		process( thisLayer )
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View

