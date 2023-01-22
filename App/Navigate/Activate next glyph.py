#MenuTitle: Activate next glyph
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Will activate the next glyph in Edit view.
"""

font = Glyphs.font
if font:
	tab = font.currentTab
	if tab:
		tab.textCursor = (tab.textCursor + 1) % len(tab.text)
