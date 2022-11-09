#MenuTitle: Compare Kerning Groups
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Compares the kerning groups of exporting glyphs in the two frontmost fonts and outputs a report in the Macro Window.
"""

thisFont = Glyphs.fonts[0] # frontmost font
otherFont = Glyphs.fonts[1] # second font

thisGlyphSet = [g.name for g in thisFont.glyphs if g.export]
commonGlyphSet = [g.name for g in otherFont.glyphs if g.export and g.name in thisGlyphSet]

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print("Differing kerning groups between:")
print(u"1. %s\n   %s\n" % (thisFont.familyName, thisFont.filepath))
print(u"2. %s\n   %s\n" % (otherFont.familyName, otherFont.filepath))

columnHead = u"◀️ ▶️ GLYPHNAME"
print(columnHead)
print("-" * len(columnHead))

sameInBothFonts = []
differencesBetweenFonts = []
for glyphName in commonGlyphSet:
	thisGlyph = thisFont.glyphs[glyphName]
	otherGlyph = otherFont.glyphs[glyphName]

	leftGroupSame = thisGlyph.leftKerningGroup == otherGlyph.leftKerningGroup
	rightGroupSame = thisGlyph.rightKerningGroup == otherGlyph.rightKerningGroup

	if leftGroupSame and rightGroupSame:
		sameInBothFonts.append(glyphName)
	else:
		differencesBetweenFonts.append(glyphName)
		print(u"%s %s %s" % (u"✅" if leftGroupSame else u"❌", u"✅" if rightGroupSame else u"❌", glyphName))

print()
print(u"✅ Glyphs with same goups:")
print("/" + "/".join(sameInBothFonts))
print()
print(u"❌ Glyphs with different groups:")
print("/" + "/".join(differencesBetweenFonts))
print()
