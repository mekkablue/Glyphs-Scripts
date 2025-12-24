#MenuTitle: Turn Dimensions into Stems
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Turns all H and V dimensions (in the Dimensions palette) into H and V stems.
"""

from GlyphsApp import GSMetric, GSInfoValue

font = Glyphs.font
dimensions = font.userData["GSDimensionPlugin.Dimensions"]

for masterID in dimensions.keys():
	master = font.fontMasterForId_(masterID)
	for dimKey in dimensions[masterID].keys():
		if dimKey[-1] not in "HV":
			continue
		if not font.stems or dimKey not in [s.name for s in font.stems]:
			stem = GSMetric()
			stem.name = dimKey
			stem.type = 0
			stem.horizontal = dimKey[-1] == "H"
			font.addStem_(stem)
		else:
			stem = font.stems[dimKey]
		value = dimensions[masterID][dimKey]
		info = GSInfoValue.alloc().initWithValue_(int(value) or 0)
		master.setStemValue_forId_(info, stem.id)

font.parent.windowController().showFontInfoWindowWithTabSelected_(1)