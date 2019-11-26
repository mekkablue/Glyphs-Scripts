from __future__ import print_function
#MenuTitle: Update Features without Reordering
# -*- coding: utf-8 -*-
__doc__="""
Refreshes all existing OT features without changing their order or adding new features.
"""

Glyphs.clearLog()
thisFont = Glyphs.font

for thisFeature in thisFont.features:
	thisFeature.update()
	print("Feature %s updated." % thisFeature.name)

print("Done.")