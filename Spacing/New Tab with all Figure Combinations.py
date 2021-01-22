#MenuTitle: New Tab with all Figure Combinations
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new edit tab and outputs all possible figure combos: 00010203..., 10111213... etc.
"""


figures = "0123456789"
text = ""
for z1 in figures:
	text += z1
	for z2 in figures:
		text += z2 + z1
	text += "\n"

# in case last line fails, the text is in the macro window:
Glyphs.clearLog() # clears macro window log
print(text)

# opens new Edit tab with figure combos:
Glyphs.currentDocument.windowController().addTabWithString_(text)
