# MenuTitle: Activate Next Glyph
# -*- coding: utf-8 -*-
__doc__ = """
Will activate the next glyph in Edit view.
"""

from GlyphsApp import Glyphs

font = Glyphs.font
if font:
	tab = font.currentTab
	if tab and tab.text:
		tab.textCursor = (tab.textCursor + 1) % len(tab.text)
