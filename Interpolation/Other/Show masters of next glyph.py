# MenuTitle: Show Masters of Next Glyph
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Shows all masters for the next glyph.
"""

import masterNavigation as nav
newGlyphName = nav.glyphNameForIndexOffset(+1)
if newGlyphName:
	nav.showAllMastersOfGlyphInCurrentTab(newGlyphName)
