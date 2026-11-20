# MenuTitle: Show Masters of Previous Glyph
# -*- coding: utf-8 -*-
__doc__ = """
Shows all masters for the previous glyph.
"""

import masterNavigation as nav
newGlyphName = nav.glyphNameForIndexOffset(-1)
if newGlyphName:
	nav.showAllMastersOfGlyphInCurrentTab(newGlyphName)
