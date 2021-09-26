#MenuTitle: Build rtlm Alternates
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Creates horizontally mirrored composite copies for selected glyphs, and updates the rtlm OpenType feature. Auto-aligns the components, also adds metrics keys that kick in in case you decompose.
"""

import math
from AppKit import NSAffineTransform, NSAffineTransformStruct

def flip():
	flipTransform = NSAffineTransform.transform()
	flipTransform.scaleXBy_yBy_(-1,1)
	return flipTransform

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
flipTransform = flip()
Glyphs.clearLog() # clears log in Macro window
thisFont.disableUpdateInterface() # suppresses UI updates in Font View

try:
	# adding composite glyphs:
	glyphNames = [l.parent.name for l in selectedLayers if not ".rtlm" in l.parent.name]
	for glyphName in glyphNames:
		rtlmName = "%s.rtlm" % glyphName
		rtlmGlyph = GSGlyph(rtlmName)
		thisFont.glyphs.append(rtlmGlyph)
		for rtlmLayer in rtlmGlyph.layers:
			component = GSComponent(glyphName)
			rtlmLayer.components.append(component)
			rtlmLayer.transform_checkForSelection_doComponents_(flipTransform,False,True)
			component.setDisableAlignment_(False)

		# metrics (in case of decomposition):
		rtlmMetricsKey = "=|%s" % glyphName
		rtlmGlyph.leftMetricsKey = rtlmMetricsKey
		rtlmGlyph.rightMetricsKey = rtlmMetricsKey
	
	# OT Feature:
	if not "rtlm" in [f.name for f in thisFont.features]:
		rtlmFeature = GSFeature()
		rtlmFeature.name = "rtlm"
		thisFont.features.append(rtlmFeature)
	else:
		rtlmFeature = thisFont.features["rtlm"]
		
	# update:
	rtlmFeature.automatic = True
	rtlmFeature.update()
		
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Create rtlm Alternates\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
