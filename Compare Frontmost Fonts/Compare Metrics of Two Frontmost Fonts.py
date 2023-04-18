#MenuTitle: Compare Metrics
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Compare widths of two frontmost fonts. Tolerates 2 unit
"""

font1 = Glyphs.font # frontmost font
font2 = Glyphs.fonts[1] # other font

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print(f"Comparing:\nFont 1: {font1.filepath}\nFont 2: {font2.filepath}\n"

masterIndexesInBothFonts = range(min(len(font1.masters), len(font2.masters)))
for g1 in [g for g in font1.glyphs if g.export]:
	glyphname = g1.name
	g2 = font2.glyphs[glyphname]
	if g2:
		for mi in masterIndexesInBothFonts:
			m1 = font1.masters[mi]
			m2 = font2.masters[mi]
			l1 = g1.layers[m1.id]
			l2 = g2.layers[m2.id]
			if abs(l1.width - l2.width) > 2.0:
				print("/%s : widths: %.1f <> %.1f (%s)" % (glyphname, l1.width, l2.width, m1.name))
	else:
		print("  %s not in font 2" % (glyphname))
