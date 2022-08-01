#MenuTitle: Merge All Other Masters in Current Master
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
For selected glyphs, merges all paths from other masters onto the current master layer.
"""

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
otherMasterIDs = [m.id for m in thisFont.masters if m is not thisFontMaster]
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisGlyph ):
	currentLayer = thisGlyph.layers[thisFontMaster.id]
	print(currentLayer)
	try:
		# GLYPHS 3
		currentLayer.clear()
	except:
		# GLYPHS 2
		currentLayer.paths = None
		currentLayer.hints = None
		currentLayer.components = None
		
	for thisID in otherMasterIDs:
		sourceLayer = thisGlyph.layers[thisID]
		sourcePaths = sourceLayer.paths
		if sourcePaths:
			for sourcePath in sourcePaths:
				currentLayer.paths.append(sourcePath.copy())
		sourceHints = sourceLayer.hints
		if sourceHints:
			for sourceHint in sourceLayer.hints:
				if sourceHint.isCorner():
					currentLayer.hints.append(sourceHint.copy())
		sourceComponents = sourceLayer.components
		if sourceComponents:
			for sourceComponent in sourceLayer.components:
				currentLayer.components.append(sourceComponent.copy())

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in listOfSelectedLayers:
		thisGlyph = thisLayer.parent
		print("Processing", thisGlyph.name)
		# thisGlyph.beginUndo() # undo grouping causes crashes
		process( thisGlyph )
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
