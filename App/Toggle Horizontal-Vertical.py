#MenuTitle: Toggle Horizontal-Vertical
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Toggle frontmost tab between LTR (horizontal) and vertical writing direction. Useful for setting a keyboard shortcuts.
"""

if Glyphs.font:
	thisTab = Glyphs.font.currentTab
	if thisTab:
		if thisTab.direction == LTR:
			newDirection = LTRTTB
		else:
			newDirection = LTR
		thisTab.direction = newDirection
	else:
		print("ERROR: No Edit tab open. Cannot switch writing direction.")
else:
	print("ERROR: No font open. Cannot switch writing direction.")
