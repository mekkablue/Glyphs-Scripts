# MenuTitle: Toggle Macro Window Separator
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Toggles the separator position in the Macro Window between 80% and 20%.
"""

from GlyphsApp import Glyphs


if Glyphs.versionNumber < 4:
	from Foundation import NSHeight
	splitview = Glyphs.delegate().macroPanelController().consoleSplitView()
	frame = splitview.frame()
	height = NSHeight(frame)
	currentPos = splitview.positionOfDividerAtIndex_(0) / height
	if currentPos > 0.5:
		newPos = 0.2
	else:
		newPos = 0.8
	splitview.setPosition_ofDividerAtIndex_(height * newPos, 0)
