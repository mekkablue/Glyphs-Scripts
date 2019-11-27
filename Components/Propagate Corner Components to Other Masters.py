#MenuTitle: Propagate Corner Components to Other Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
Puts Corner Components from the current layer into other master layers, at the same point indexes. Useful if Corner components do not interpolate correctly.
"""

from GlyphsApp import CORNER
from AppKit import NSNotificationCenter

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

def pathStructure(thisLayer):
	layerString = ""
	for thisPath in thisLayer.paths:
		layerString += "_"
		for thisNode in thisPath.nodes:
			layerString += thisNode.type[0]
	return layerString

def process( thisLayer ):
	thisGlyph = thisLayer.parent
	targetLayers = [
		l for l in thisGlyph.layers 
			if l != thisLayer 
			and pathStructure(l) == pathStructure(thisLayer)
		]
	for targetLayer in targetLayers:
		deleteCornerComponentsOnLayer(targetLayer)
		for h in [h for h in thisLayer.hints if h.type == CORNER]:
			# query corner component attributes:
			pathIndex = indexOfPath(thisLayer, h.originNode.parent)
			nodeIndex = indexOfNode(thisLayer, pathIndex,h.originNode)
			
			# create eqivalent corner component in target layer:
			newCorner = h.copy()
			targetLayer.hints.append(newCorner)

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

if thisFont and listOfSelectedLayers:
	thisFont.disableUpdateInterface() # suppresses UI updates in Font View

	for thisLayer in listOfSelectedLayers:
		thisGlyph = thisLayer.parent
		print("Processing", thisGlyph.name)
		thisGlyph.beginUndo() # begin undo grouping
		process( thisLayer )
		thisGlyph.endUndo()   # end undo grouping

	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
	NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont)
