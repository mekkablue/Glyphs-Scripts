#MenuTitle: Make Glyph Smart
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Turn the currently selected glyph(s) into smart glyphs, and establish the current font axes as the glyph’s smart axes.
"""

from GlyphsApp import GSSmartComponentAxis

def minMaxForLayer(layer, fontAxisID):
	# collect all values for this axis:
	glyph = layer.parent
	font = glyph.parent
	axisIndex = -1
	for i, axis in enumerate(font.axes):
		if axis.id == fontAxisID:
			axisIndex = i
			break
	if axisIndex < 0:
		return 0 # neither max nor min
	axisValues = []
	for master in font.masters:
		axisValues.append(master.axes[axisIndex])
	
	# is the current layer min or max?
	currentMaster = layer.associatedFontMaster()
	currentValue = currentMaster.axes[fontAxisID]
	if currentValue == max(axisValues):
		return 2 # max
	elif currentValue == min(axisValues):
		return 1 # min
	return 0 # neither


Glyphs.clearLog() # clears log in Macro window
thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	font = Glyphs.font # frontmost font
	for selectedLayer in font.selectedLayers:
		if not selectedLayer.parent:
			continue
		glyph = selectedLayer.parent
		if glyph is None:
			continue
		
		glyph.beginUndo()
		
		for fontAxis in font.axes:
			# add font axis as smart axis if necessary:
			smartAxis = None # glyph.smartComponentAxes[fontAxis.name]
			if glyph.smartComponentAxes:
				for existingAxis in glyph.smartComponentAxes:
					if existingAxis.name == fontAxis.name:
						smartAxis = existingAxis
			if not smartAxis:
				smartAxis = GSSmartComponentAxis()
				smartAxis.name = fontAxis.name
				glyph.smartComponentAxes.append(smartAxis)
			# layer assignments:
			for layer in glyph.layers:
				layer.smartComponentPoleMapping[smartAxis.id] = minMaxForLayer(layer, fontAxis.id)

		glyph.endUndo()

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Make Glyph Smart\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e

finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
