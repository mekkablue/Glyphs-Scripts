# MenuTitle: Show Masters of Next Glyph
__doc__ = """
Shows all masters for the next glyph.
"""

import masterNavigation as nav
newGlyphName = nav.glyphNameForIndexOffset(+1)
if newGlyphName:
	nav.showAllMastersOfGlyphInCurrentTab(newGlyphName)
