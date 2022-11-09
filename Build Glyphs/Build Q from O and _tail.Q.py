#MenuTitle: Build Q from O and _tail.Q
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Run this script AFTER doing Component from Selection on the Q tail and naming it _tail.Q.
"""

from copy import copy as copy
thisFont = Glyphs.font # frontmost font
O = thisFont.glyphs["O"]
Q = thisFont.glyphs["Q"]
tailGlyph = thisFont.glyphs["_tail.Q"]
anchorName = "bottom"
newAnchorName = "_" + anchorName

if not O or not Q or not tailGlyph:
	Message(title="Missing glyphs", message="For this script, you need ‘O’, ‘Q’ and ‘_tail.Q’ in your font.", OKButton=None)
else:
	# del thisFont.glyphs["Q"]
	# thisFont.newGlyphWithName_("O+_tail.Q=Q")
	for thisLayer in tailGlyph.layers:
		thisMaster = thisLayer.associatedFontMaster()
		masterID = thisMaster.id

		# if necessary, add anchors to _tail.Q
		if not thisLayer.anchors[newAnchorName]:
			defaultPosition = O.layers[masterID].anchors[anchorName].position
			newAnchor = GSAnchor(newAnchorName, defaultPosition)
			thisLayer.anchors.append(newAnchor)

		# rebuild Q from O:
		targetLayer = Q.layers[masterID]
		targetLayer.clear()
		for componentName in (O.name, tailGlyph.name):
			newComponent = GSComponent(componentName)
			newComponent.automaticAlignment = True
			targetLayer.components.append(newComponent)

	# add special layers to _tail.Q:
	for layerIndex in range(len(Q.layers) - 1, -1, -1):
		thisLayer = Q.layers[layerIndex]
		if not thisLayer.isMasterLayer and thisLayer.isSpecialLayer:
			tailLayer = copy(thisLayer)

			# remove (O) components:
			for i in range(len(tailLayer.shapes) - 1, -1, -1):
				if type(tailLayer.shapes[i]) == GSComponent:
					del tailLayer.shapes[i]

			# add anchor:
			newAnchor = GSAnchor()
			newAnchor.name = newAnchorName
			newAnchor.position = O.layers[thisLayer.associatedMasterId].anchors[anchorName].position
			tailLayer.anchors.append(newAnchor)

			# add layer to _tail.Q:
			tailGlyph.layers.append(tailLayer)

			# remove layer from Q:
			del Q.layers[layerIndex]
