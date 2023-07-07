#MenuTitle: Propagate Corner Components to Other Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Puts Corner Components from the current layer into other master layers, at the same point indexes. Useful if Corner components do not interpolate correctly.
"""

from GlyphsApp import CORNER, SEGMENT, CAP
# from AppKit import NSNotificationCenter
SUPPORTEDTYPES = (CORNER, SEGMENT, CAP)

def indexOfPath(l, p):
	for i in range(len(l.paths)):
		if p == l.paths[i]:
			return i
	return None

def indexOfNode(l, pi, n):
	for i in range(len(l.paths[pi].nodes)):
		if n == l.paths[pi].nodes[i]:
			return i
	return None

def deleteCornerComponentsOnLayer(l):
	cornerComponents = [h for h in l.hints if h.type in SUPPORTEDTYPES]
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

def process(thisLayer):
	thisGlyph = thisLayer.parent
	targetLayers = [l for l in thisGlyph.layers if l != thisLayer and pathStructure(l) == pathStructure(thisLayer)]
	for targetLayer in targetLayers:
		deleteCornerComponentsOnLayer(targetLayer)
		for h in [h for h in thisLayer.hints if h.type in SUPPORTEDTYPES]:
			# query corner component attributes:
			pathIndex = indexOfPath(thisLayer, h.originNode.parent)
			nodeIndex = indexOfNode(thisLayer, pathIndex, h.originNode)

			# create eqivalent corner component in target layer:
			newCorner = h.copy()
			targetLayer.hints.append(newCorner)
	

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

if thisFont and selectedLayers:
	thisFont.disableUpdateInterface() # suppresses UI updates in Font View
	try:
		for thisLayer in selectedLayers:
			thisGlyph = thisLayer.parent
			print("Processing", thisGlyph.name)
			# thisGlyph.beginUndo() # undo grouping causes crashes
			process(thisLayer)
			# thisGlyph.endUndo() # undo grouping causes crashes

	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ Script Error:\n")
		import traceback
		print(traceback.format_exc())
		print()
		raise e

	finally:
		thisFont.enableUpdateInterface() # re-enables UI updates in Font View
		if Glyphs.versionNumber < 3 and thisFont.currentTab:
			thisFont.currentTab.redraw()
			# NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont.currentTab)
