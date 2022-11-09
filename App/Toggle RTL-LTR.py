#MenuTitle: Toggle RTL/LTR
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Toggle frontmost tab between LTR and RTL writing direction. Useful for setting a keyboard shortcuts.
"""

# quick and dirty fix for name change in 3121
try:
	from GlyphsApp import GSLTR as LTR, GSRTL as RTL
except:
	from GlyphsApp import LTR, RTL

if Glyphs.font:
	thisTab = Glyphs.font.currentTab
	if thisTab:
		if thisTab.direction == LTR:
			newDirection = RTL
		else: # RTL or TTB
			newDirection = LTR
		thisTab.direction = newDirection
#     else:
#         print("ERROR: No Edit tab open. Cannot switch writing direction.")
# else:
#     print("ERROR: No font open. Cannot switch writing direction.")
