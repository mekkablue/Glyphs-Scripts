# MenuTitle: Update Features without Reordering
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Refreshes all existing OT features without changing their order or adding new features.
"""

from GlyphsApp import Glyphs

Glyphs.clearLog()
thisFont = Glyphs.font
if not thisFont:
	print("Please open a font first.")
else:

	for thisFeature in thisFont.features:
		thisFeature.update()
		print("Feature %s updated." % thisFeature.name)

	print("Done.")
