#MenuTitle: Compare Sidebearings
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Compare sidebearings of two frontmost fonts.
"""

Font1 = Glyphs.font # frontmost font
Font2 = Glyphs.fonts[1] # other font
tolerance = 2.0

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print("Comparing:\nFont 1: %s\nFont 2: %s\n" % (Font1.filepath, Font2.filepath))

count = 0
for g1 in [g for g in Font1.glyphs if g.export]:
	glyphname = g1.name
	g2 = Font2.glyphs[glyphname]
	if g2:
		for mi, m1 in enumerate(Font1.masters):
			m2 = Font2.masters[mi]
			l1 = g1.layers[m1.id]
			l2 = g2.layers[m2.id]
			if not l1.isAligned and not l2.isAligned:
				reportGlyph = False
				reportString = "/%s : " % glyphname
				if abs(l1.LSB-l2.LSB) > tolerance:
					reportGlyph = True
					reportString += "LSB %i <> %i  " % (l1.LSB, l2.LSB)
				if abs(l1.RSB-l2.RSB) > tolerance:
					reportGlyph = True
					reportString += "RSB %i <> %i  " % (l1.RSB, l2.RSB)
				if reportGlyph:
					count += 1
					print("%s  (%s)" % (reportString, m1.name))
	else:
		print("  %s not in Font 2" % (glyphname))

print("Found %i discrepancies beyond %i units in all masters." % (count, tolerance))