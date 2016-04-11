#MenuTitle: Propagate Corner Components to Other Masters
# -*- coding: utf-8 -*-
__doc__="""
Puts Corner Components from the current layer into other master layers, at the same point indexes. Useful if Corner components do not interpolate correctly.
"""

from GlyphsApp import CORNER

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def indexOfPath(l,p):
	for i in range(len(l.paths)):
		if p == l.paths[i]:
			return i
	return None

def indexOfNode(l,pi,n):
	for i in range(len(l.paths[pi].nodes)):
		if n == l.paths[pi].nodes[i]:
			return i
	return None
	
def deleteCornerComponentsOnLayer(l):
	cornerComponents = [h for h in l.hints if h.type == CORNER]
	if cornerComponents:
		for i in range(len(cornerComponents))[::-1]:
			h = cornerComponents[i]
			l.removeHint_(h)

def process( thisLayer ):
	thisGlyph = thisLayer.parent
	targetLayers = [l for l in thisGlyph.layers if l != thisLayer and l.associatedMasterId == l.layerId]
	for h in [h for h in thisLayer.hints if h.type == CORNER]:
		scale = h.scale()
		name = h.name()
		pathIndex = indexOfPath(thisLayer,h.originNode.parent())
		nodeIndex = indexOfNode(thisLayer,pathIndex,h.originNode)
		for targetLayer in targetLayers:
			deleteCornerComponentsOnLayer(targetLayer)
			newCorner = GSHint()
			newCorner.type = CORNER
			newCorner.setScale_(scale)
			newCorner.setName_(name)
			newCorner.originNode = targetLayer.paths[pathIndex].nodes[nodeIndex]
			targetLayer.addHint_(newCorner)
			

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
