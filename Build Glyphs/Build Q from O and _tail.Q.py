#MenuTitle: Build Q from O and _tail.Q
# -*- coding: utf-8 -*-
__doc__="""
Run this script AFTER doing Component from Selection on the Q tail and naming it _tail.Q.
"""

thisFont = Glyphs.font # frontmost font
defaultGlyph = thisFont.glyphs["O"]
targetGlyph = thisFont.glyphs["Q"]
tailGlyph = thisFont.glyphs["_tail.Q"]
anchorName = "bottom"

for thisLayer in tailGlyph.layers:
	thisMaster = thisLayer.associatedFontMaster()
	masterID = thisMaster.id
	
	# if necessary, add anchors to _tail.Q
	newAnchorName = "_"+anchorName
	if not thisLayer.anchors[newAnchorName]:
		defaultPosition = defaultGlyph.layers[masterID].anchors[anchorName].position
		newAnchor = GSAnchor(newAnchorName,defaultPosition)
		thisLayer.anchors.append(newAnchor)
	
	# rebuild Q from O:
	targetLayer = targetGlyph.layers[masterID]
	targetLayer.clear()
	for componentName in (defaultGlyph.name,tailGlyph.name):
		newComponent = GSComponent(componentName)
		newComponent.automaticAlignment = True
		targetLayer.components.append(newComponent)
		
