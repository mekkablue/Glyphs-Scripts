# MenuTitle: Compare Composites
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Reports diverging component structures of composite glyphs, e.g., iacute built with acutecomb in one font, and acutecomb.narrow in the other.
"""

from GlyphsApp import Glyphs

Font1 = Glyphs.font
Font2 = Glyphs.fonts[1]

filePath1 = "~/" + Font1.filepath.relativePathFromBaseDirPath_("~")
filePath2 = "~/" + Font2.filepath.relativePathFromBaseDirPath_("~")
fileName1 = Font1.filepath.lastPathComponent()
fileName2 = Font2.filepath.lastPathComponent()

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print("Comparing composites:\nFont 1: %s\nFont 2: %s\n\nFont 1: %s\nFont 2: %s\n" % (fileName1, fileName2, filePath1, filePath2))

for g1 in [g for g in Font1.glyphs if g.export]:
	glyphname = g1.name
	g2 = Font2.glyphs[glyphname]
	if g2:
		for mi, m1 in enumerate(Font1.masters):
			m2 = Font2.masters[mi]
			l1 = g1.layers[m1.id]
			l2 = g2.layers[m2.id]

			composite1 = "+".join([c.componentName for c in l1.components])
			composite2 = "+".join([c.componentName for c in l2.components])

			if composite1 != composite2:
				print("/%s : %s <> %s" % (glyphname, composite1, composite2))
	else:
		print("  %s not in ‘%s’" % (glyphname, fileName2))
