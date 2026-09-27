# MenuTitle: Toggle RTL/LTR
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Toggle frontmost tab between LTR and RTL writing direction. Useful for setting a keyboard shortcuts.
"""

from GlyphsApp import Glyphs
if Glyphs.versionNumber < 4.0:
	# Glyphs 3 only had the old names, dropped in Glyphs 4:
	from GlyphsApp import LTR as GSLTR, RTL as GSRTL
else:
	from GlyphsApp import GSLTR, GSRTL

if Glyphs.font:
	thisTab = Glyphs.font.currentTab
	if thisTab:
		if thisTab.direction == GSLTR:
			newDirection = GSRTL
		else:  # RTL or TTB
			newDirection = GSLTR
		thisTab.direction = newDirection
#     else:
#         print("ERROR: No Edit tab open. Cannot switch writing direction.")
# else:
#     print("ERROR: No font open. Cannot switch writing direction.")
