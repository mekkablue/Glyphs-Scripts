# MenuTitle: Toggle Horizontal-Vertical
# -*- coding: utf-8 -*-
__doc__ = """
Toggle frontmost tab between LTR (horizontal) and vertical writing direction. Useful for setting a keyboard shortcuts.
"""

from GlyphsApp import Glyphs

if Glyphs.versionNumber < 4.0:
	# Glyphs 3 only had the old name, dropped in Glyphs 4:
	from GlyphsApp import LTR as GSLTR, LTRTTB as GSVertical
else:
	from GlyphsApp import GSLTR, GSVertical

if Glyphs.font:
	thisTab = Glyphs.font.currentTab
	if thisTab:
		if thisTab.direction == GSLTR:
			newDirection = GSVertical
		else:
			newDirection = GSLTR
		thisTab.direction = newDirection
	else:
		print("ERROR: No Edit tab open. Cannot switch writing direction.")
else:
	print("ERROR: No font open. Cannot switch writing direction.")
