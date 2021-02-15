#MenuTitle: Sync Components Across Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Takes the current layer’s components, and resets all other masters to the same component structure. Ignores paths and anchors. Hold down Option key to delete all paths and anchors.
"""
from AppKit import NSEvent, NSAlternateKeyMask

thisFont = Glyphs.font # frontmost font
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

# combo key held down:
keysPressed = NSEvent.modifierFlags()
optionKeyPressed = keysPressed & NSAlternateKeyMask == NSAlternateKeyMask

def process( thisLayer ):
	thisGlyph = thisLayer.parent
	# only act if components are present:
	if len(thisLayer.components):
		for thatLayer in thisGlyph.layers:
			if thatLayer is thisLayer:
				continue
			newComponents = []
			for thisComp in thisLayer.components:
				thatComp = thisComp.copy()
				newComponents.append(thatComp)
			
			if newComponents:
				if Glyphs.versionNumber >= 3:
					# GLYPHS 3
					if optionKeyPressed:
						#clear all:
						thatLayer.shapes = newComponents
						thatLayer.anchors = None
					else:
						# clear components:
						for i in range(len(thatLayer.shapes)-1,-1,-1):
							shape = thatLayer.shapes[i]
							if type(shape) == GSComponent or optionKeyPressed: # NEW: check for paths
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

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in listOfSelectedLayers:
		thisGlyph = thisLayer.parent
		print("Processing %s" % thisGlyph.name)
		thisGlyph.beginUndo() # begin undo grouping
		process( thisLayer )
		thisGlyph.endUndo()   # end undo grouping
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
