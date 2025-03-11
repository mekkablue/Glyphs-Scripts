# MenuTitle: New tab with uneven symmetric kernings
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds kern pairs for symmetric letters like ATA AVA TOT WIW etc. and sees if AT is the same as TA, etc.
"""

from GlyphsApp import Glyphs, Message

Font = Glyphs.font

UC = "AHIMNOTUVWXYАЖИМНОПТФХШЏЫІΑΗΘΙΛΜΝΞΟΠΤΥΦΧΨΩ"
SC = [f"{x.lower()}.sc" for x in UC]
LC = "ilovwxжимноптфхшџыθοχω"
SY = ["period", "colon", "ellipsis", "periodcentered", "hyphen", "endash", "emdash", "quotesingle", "quotedbl", "at", "space", "asterisk", "bar", "brokenbar"]

thisFont = Glyphs.font  # frontmost font
m = thisFont.selectedFontMaster  # active master
Glyphs.clearLog()  # clears log in Macro window

allDottedGlyphNames = [x.name for x in thisFont.glyphs if "." in x.name and x.export]
extraUC, extraSC, extraLC = [], [], []
for x in allDottedGlyphNames:
	for S in SC:
		if x.startswith(f"{S}."):
			extraSC.append(x)
	for U in UC:
		if x.startswith(f"{U}.") and x not in SC and x not in extraSC:
			extraUC.append(x)
	for L in LC:
		if x.startswith(f"{L}.") and x not in SC and x not in extraSC:
			extraLC.append(x)

tabString = ""
for glyphnames in (list(UC) + extraUC + SY, list(LC) + extraLC + SY, SC + extraSC + SY):
	print(glyphnames)
	for i, glyphname1 in enumerate(glyphnames):
		for glyphname2 in glyphnames[i:]:
			if glyphname1 != glyphname2:  # AAA makes no sense
				if not thisFont.glyphs[glyphname1] or not thisFont.glyphs[glyphname2]:
					for g in (glyphname1, glyphname2):
						if not thisFont[g]:
							print(f"⚠️ glyph ‘{g}’ does not exist.")
				else:
					# kerning exceptions:
					leftKern = Font.kerningForPair(m.id, glyphname1, glyphname2)
					rightKern = Font.kerningForPair(m.id, glyphname2, glyphname1)
					if leftKern != rightKern:
						print(f"{glyphname1}-{glyphname2}-{glyphname1}: exception not symmetric: {leftKern} vs. {rightKern}")
						tabString += f"/{glyphname1}/{glyphname2}/{glyphname1}\n"
					else:
						glyph1 = thisFont.glyphs[glyphname1]
						glyph2 = thisFont.glyphs[glyphname2]
						if glyph1.rightKerningGroup and glyph2.leftKerningGroup and glyph2.rightKerningGroup and glyph1.leftKerningGroup:
							# group kerning:
							leftKern = Font.kerningForPair(m.id, "@MMK_L_" + glyph1.rightKerningGroup, "@MMK_R_" + glyph2.leftKerningGroup)
							rightKern = Font.kerningForPair(m.id, "@MMK_L_" + glyph2.rightKerningGroup, "@MMK_R_" + glyph1.leftKerningGroup)
							if leftKern != rightKern:
								print("@%s-@%s-@%s: group kerning not symmetric: %s vs. %s" % (
									glyph1.name,
									glyph2.name,
									glyph1.name,
									leftKern,
									rightKern,
								))
								tabString += f"/{glyphname1}/{glyphname2}/{glyphname1}\n"
						else:
							print(f"⚠️ missing kerning groups in glyphs: {glyphname1}, {glyphname2}.")

if tabString:
	# opens new Edit tab:
	thisFont.newTab(tabString)
else:
	Message(title="No Asymmetries", message="Found no asymmetries in the kerning of this master.", OKButton=None)
