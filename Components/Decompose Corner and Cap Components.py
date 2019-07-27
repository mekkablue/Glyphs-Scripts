#MenuTitle: Decompose Corner and Cap Components
# -*- coding: utf-8 -*-
__doc__="""
Recreates the current paths without caps or components.
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
removeOverlapFilter = NSClassFromString("GlyphsFilterRemoveOverlap").alloc().init()
gridSize = float(thisFont.gridMain())/thisFont.gridSubDivision()

def removeCorners(thisLayer):
	numOfHints = len(thisLayer.hints)
	for i in range(numOfHints)[::-1]:
		if thisLayer.hints[i].type == 16: # corner
			thisLayer.removeObjectFromHintsAtIndex_(i)

def removeCaps(thisLayer):
	numOfHints = len(thisLayer.hints)
	for i in range(numOfHints)[::-1]:
		if thisLayer.hints[i].type == 17: # cap
			thisLayer.removeObjectFromHintsAtIndex_(i)
	
def process( thisLayer ):
	pen = GSBezStringPen.alloc().init()
	for thisPath in thisLayer.paths:
		thisPath.drawInPen_(pen)

	pathString = pen.charString()
	newPaths = removeOverlapFilter.pathsFromBez_gridSize_(pathString,gridSize)
	
	removeCaps(thisLayer)
	removeCorners(thisLayer)
	thisLayer.paths = newPaths
	

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
