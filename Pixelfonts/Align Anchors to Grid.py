#MenuTitle: Align Anchors to Grid
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Looks for anchors not on the grid and rounds their coordinate to the closest grid.
"""

def process( thisLayer ):
	count = 0
	if len( thisLayer.anchors ) != 0:
		thisLayer.parent.beginUndo()
		
		for a in thisLayer.anchors:
			xrest = a.x % pixelwidth
			yrest = a.y % pixelwidth
			if xrest or yrest:
				# round:
				oldX = a.x
				oldY = a.y
				a.x = round( a.x/pixelwidth ) * pixelwidth
				a.y = round( a.y/pixelwidth ) * pixelwidth
				
				# report:
				count+=1
				if count == 1:
					reportGlyphName = "%s" % thisLayer.parent.name
				elif count == 2:
					reportGlyphName = " "*len(reportGlyphName) # indent
				print("%s ⚓️ %s %i,%i → %i,%i" % (reportGlyphName , a.name, int(oldX), int(oldY), int(a.x), int(a.y) ))
				
		thisLayer.parent.endUndo()
	return count

thisFont.disableUpdateInterface()
try:
	thisFont = Glyphs.font
	selectedLayers = thisFont.selectedLayers
	pixelwidth = thisFont.gridLength
	
	# report:
	Glyphs.clearLog()
	print("Aligning anchors to grid in font: %s" % thisFont.familyName)
	print("Processing: %i glyph%s" % (len(selectedLayers), "" if len(selectedLayers)==1 else "s"))
	print("Grid: %i\n" % pixelwidth)
	
	# process and keep count:
	anchorCount = 0
	for thisLayer in selectedLayers:
		anchorCount += process( thisLayer )
	
	# report:
	print("\nMoved %i anchors. Done." % anchorCount)
	Glyphs.showNotification( 
		"Grid-aligned anchors in %s" % (thisFont.familyName),
		"Aligned %i anchors in %i selected glyphs. Details in Macro Window." % (anchorCount, len(selectedLayers)),
		)
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View

