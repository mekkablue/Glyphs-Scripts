#MenuTitle: Refresh features without reordering
# -*- coding: utf-8 -*-
__doc__="""
Refreshes all existing OT features without changing their order or adding new features.
"""


Font = Glyphs.font

for thisFeature in Font.features:
	thisFeature.update()
	print "Feature %s updated." % thisFeature.name

print "Done."