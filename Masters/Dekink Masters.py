#MenuTitle: Dekink
# -*- coding: utf-8 -*-
__doc__="""
Synchronize node distance proportions for angled smooth connections through all masters (and other compatible layers), thus avoiding interpolation kinks. Select one or more smoothly connected nodes and run the script.
"""

import GlyphsApp

Font = Glyphs.font
currentLayer = Font.selectedLayers[0]
currentGlyph = currentLayer.parent

def dekink( originLayer, compatibleLayerIDs, pathIndex, nodeIndex, proportion ):
	try:
		myGlyph = originLayer.parent
		for thisID in compatibleLayerIDs:
			thisLayer = myGlyph.layers[thisID]
			thisPath = thisLayer.paths[pathIndex]
			pathLength = len(thisPath)
			n0 = thisPath.nodes[ (nodeIndex-1) % pathLength ]
			n1 = thisPath.nodes[  nodeIndex ]
			n2 = thisPath.nodes[ (nodeIndex+1) % pathLength ]
			n1.x = n0.x + proportion * (n2.x - n0.x)
			n1.y = n0.y + proportion * (n2.y - n0.y)
		return True
	except Exception, e:
		print e
		import traceback
		print traceback.format_exc()
		return False

layerIDs = []
for subrunArray in currentGlyph.layerGroups_masters_error_( NSArray(Font.instances), Font.masters, None ):
	subrun = tuple(subrunArray)
	if currentLayer.layerId in subrun:
		for ID in subrun:
			if ID != currentLayer.layerId:
				layerIDs.append(ID)

if layerIDs:
	if currentGlyph.mastersCompatible:
		selection = currentLayer.selection
	
		s = list( selection )
		currentCompareString = currentLayer.compareString()
	
		# find the indices for selected nodes:
		for n in [n for n in s if n.connection == GSSMOOTH]:
			for pi in range( len( currentLayer.paths )):
				pathLength = len( currentLayer.paths[pi].nodes )
				currentNodes = currentLayer.paths[pi].nodes
				for ni in range( pathLength ):
					if currentNodes[ni] == n:
						n0 = currentNodes[(ni-1) % pathLength]
						n1 = currentNodes[ ni ]
						n2 = currentNodes[(ni+1) % pathLength]
				
						longX  = n2.x - n0.x
						longY  = n2.y - n0.y
						shortX = n1.x - n0.x
						shortY = n1.y - n0.y

						if longY == 0.0 or longX == 0.0:
							print "Ignoring node at %i, %i because the segment is straight." % ( n1.x, n1.y )
						else:
							proportion = ( shortX / longX + shortY / longY ) / 2.0
							if not dekink( currentLayer, layerIDs, pi, ni, proportion ):
								Message("Dekink Error", "Error: dekinking failed.", OKButton=None)
	else:
		Message("Dekink Error", "Could not find compatible masters.", OKButton=None)
else:
	Message("Dekink Error", "Could not find any other layers in this glyph for this interpolation.", OKButton=None)