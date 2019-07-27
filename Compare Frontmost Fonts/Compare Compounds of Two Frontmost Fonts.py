#MenuTitle: Compare Compounds
# -*- coding: utf-8 -*-
__doc__="""
Reports diverging component structures of compound glyphs, e.g., iacute built with acutecomb in one font, and acutecomb.narrow in the other.
"""

Font1 = Glyphs.font
Font2 = Glyphs.fonts[1]

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print "Comparing:\nFont 1: %s\nFont 2: %s\n" % (Font1.filepath, Font2.filepath)

for g1 in [g for g in Font1.glyphs if g.export]:
	glyphname = g1.name
	g2 = Font2.glyphs[glyphname]
	if g2:
		for mi, m1 in enumerate(Font1.masters):
			m2 = Font2.masters[mi]
			l1 = g1.layers[m1.id]
			l2 = g2.layers[m2.id]
			
			compound1 = "+".join([c.componentName for c in l1.components])
			compound2 = "+".join([c.componentName for c in l2.components])
			
			if compound1 != compound2:
				print "/%s : %s <> %s" % (glyphname, compound1, compound2)
	else:
		print "  %s not in Font 2" % (glyphname)
