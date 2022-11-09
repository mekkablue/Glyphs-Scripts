#MenuTitle: Compare Metrics
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Compare widths of two frontmost fonts.
"""

Font1 = Glyphs.font # frontmost font
Font2 = Glyphs.fonts[1] # other font

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print("Comparing:\nFont 1: %s\nFont 2: %s\n" % (Font1.filepath, Font2.filepath))

for g1 in [g for g in Font1.glyphs if g.export]:
	glyphname = g1.name
	g2 = Font2.glyphs[glyphname]
	if g2:
		for mi, m1 in enumerate(Font1.masters):
			m2 = Font2.masters[mi]
			l1 = g1.layers[m1.id]
			l2 = g2.layers[m2.id]
			if abs(l1.width - l2.width) > 2.0:
				print("/%s : widths: %.1f <> %.1f (%s)" % (glyphname, l1.width, l2.width, m1.name))
	else:
		print("  %s not in Font 2" % (glyphname))
