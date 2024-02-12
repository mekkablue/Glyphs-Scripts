# MenuTitle: Sync Components Across Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Takes the current layer’s components, and resets all other masters to the same component structure. Ignores paths and anchors. Hold down Option key to delete all paths and anchors.
"""
from AppKit import NSEvent, NSAlternateKeyMask
from GlyphsApp import Glyphs, GSComponent

Glyphs.clearLog()
thisFont = Glyphs.font  # frontmost font
listOfSelectedLayers = thisFont.selectedLayers  # active layers of selected glyphs
print(f"Sync Components Across Masters for {thisFont.familyName}:")

# combo key held down:
keysPressed = NSEvent.modifierFlags()
optionKeyPressed = keysPressed & NSAlternateKeyMask == NSAlternateKeyMask
if optionKeyPressed:
	print(f"Opt key detected: will reset layers, not just add components.")
print()


def process(thisLayer):
	thisGlyph = thisLayer.parent
	layerID = thisLayer.layerId

	# only act if components are present:
	if len(thisLayer.components)==0:
		print(f"  ⚠️ No components on layer {thisLayer.name}, skipping.")
		return
	
	compatibilityRun = None
	for layerGroup in thisGlyph.layerGroups():
		layerGroup = tuple(layerGroup)
		if layerID in layerGroup:
			compatibilityRun = layerGroup
			break
	
	if compatibilityRun is None:
		print(f"🆘 No interpolating layers found in glyph {thisGlyph.name}, skipping...")
		return
	
	for thatLayerID in compatibilityRun:
		thatLayer = thisGlyph.layerForId_(thatLayerID)
		
		if thatLayer is thisLayer:
			continue
			# source layer
		
		newComponents = []
		for thisComp in thisLayer.components:
			newComponents.append(thisComp.copy())

		if Glyphs.versionNumber >= 3:
			# GLYPHS 3
			if optionKeyPressed:
				# clear all:
				thatLayer.shapes = None
				thatLayer.anchors = None
			else:
				# clear components:
				for i in range(len(thatLayer.shapes) - 1, -1, -1):
					shape = thatLayer.shapes[i]
					if isinstance(shape, GSComponent):
						del thatLayer.shapes[i]
			# add components:
			thatLayer.shapes.extend(newComponents)

		else:
			# GLYPHS 2
			thatLayer.components = newComponents
			if optionKeyPressed:
				if thatLayer.anchors:
					thatLayer.anchors = None
					print("    Deleted anchors")
				if thatLayer.paths:
					thatLayer.paths = None
					print("    Deleted paths")

		print(f"  🆗 {thatLayer.name}")


thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	for thisLayer in listOfSelectedLayers:
		thisGlyph = thisLayer.parent
		print(f"🔠 Syncing components in {thisGlyph.name}...")
		thisGlyph.beginUndo()  # undo grouping
		process(thisLayer)
		thisGlyph.endUndo()  # undo grouping
	print("\n✅ Done.")
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
