#MenuTitle: Report Highest and Lowest Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Reports highest and lowest glyphs for each master in the Macro Window.
"""

thisFont = Glyphs.font
exportingGlyphs = [g for g in thisFont.glyphs if g.export]

Glyphs.clearLog()
Glyphs.showMacroWindow()

print("Highest and lowest glyphs for %s\n" % thisFont.familyName)
for thisMaster in thisFont.masters:
	masterID = thisMaster.id
	glyphsBottomsAndTops = [[g.name, g.layers[masterID].bounds.origin.y, g.layers[masterID].bounds.origin.y + g.layers[masterID].bounds.size.height] for g in exportingGlyphs]
	lowest = sorted(glyphsBottomsAndTops, key=lambda x: x[1])[0]
	highest = sorted(glyphsBottomsAndTops, key=lambda x: -x[2])[0]
	print("Master: %s" % thisMaster.name)
	print("   Highest: %s (top y: %.1f)" % (highest[0], highest[2]))
	print("   Lowest: %s (bottom y: %.1f)" % (lowest[0], lowest[1]))
	print()
