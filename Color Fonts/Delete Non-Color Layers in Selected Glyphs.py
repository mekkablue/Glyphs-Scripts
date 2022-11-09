#MenuTitle: Delete Non-Color Layers in Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Deletes all sublayers in all glyphs that are not of type "Color X" (CPAL/COLR layers).
"""

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
thisFontMasterID = thisFontMaster.id
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process(thisGlyph):
	for i in range(len(thisGlyph.layers))[::-1]:
		currentLayer = thisGlyph.layers[i]
		if not currentLayer.layerId == thisFontMasterID: # not the master layer
			try:
				# GLYPHS 3
				isColorLayer = currentLayer.isColorPaletteLayer()
			except:
				# GLYPHS 2
				isColorLayer = currentLayer.name.startswith("Color ")
			if not isColorLayer:
				currentLayerID = currentLayer.layerId
				print("%s: removed non-Color layer ‘%s’" % (thisGlyph.name, currentLayer.name))
				try:
					# GLYPHS 3
					thisGlyph.removeLayerForId_(currentLayerID)
				except:
					# GLYPHS 2
					thisGlyph.removeLayerForKey_(currentLayerID)

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	Glyphs.clearLog()
	print("Removing non-Color layers in %i glyphs:" % len(listOfSelectedLayers))
	for thisLayer in listOfSelectedLayers:
		thisGlyph = thisLayer.parent
		print("\nProcessing", thisGlyph.name)
		# thisGlyph.beginUndo() # undo grouping causes crashes
		process(thisGlyph)
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
