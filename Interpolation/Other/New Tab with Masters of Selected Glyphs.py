#MenuTitle: New Tab with Masters of Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Opens a new Edit tab containing all masters of selected glyphs.
"""

import masterNavigation as nav

thisFont = Glyphs.font # frontmost font
if thisFont and thisFont.selectedLayers:
	glyphNames = [l.parent.name for l in Font.selectedLayers if l.parent and l.parent.name]
	nav.showAllMastersOfGlyphs( glyphNames )
