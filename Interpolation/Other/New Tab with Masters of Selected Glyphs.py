# MenuTitle: New Tab with Masters of Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Opens a new Edit tab containing all masters of selected glyphs.
"""

import masterNavigation as nav
from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font
if thisFont and thisFont.selectedLayers:
	glyphNames = [layer.parent.name for layer in thisFont.selectedLayers if layer.parent and layer.parent.name]
	nav.showAllMastersOfGlyphs(glyphNames)
