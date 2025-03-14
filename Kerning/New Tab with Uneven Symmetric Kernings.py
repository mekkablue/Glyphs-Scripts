# MenuTitle: New tab with uneven symmetric kernings
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds kern pairs for symmetric letters like ATA AVA TOT WIW etc. and sees if AT is the same as TA, etc.
"""

from GlyphsApp import Glyphs, Message

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
		glyph1 = thisFont.glyphs[glyphname1]
		if not glyph1:
			continue
		for glyphname2 in glyphnames[i:]:
			if glyphname1 != glyphname2:  # AAA makes no sense
				glyph2 = thisFont.glyphs[glyphname2]
				if not glyph2:
					continue
				else:
					layer1 = thisFont.glyphs[glyphname1].layers[m.id]
					layer2 = thisFont.glyphs[glyphname2].layers[m.id]
					direction = glyph1.direction
					if direction == 1:
						direction = glyph2.direction
					if direction == 1:
						direction = 0
					leftKern = layer1.nextKerningForLayer_direction_(layer2, direction)
					rightKern = layer2.nextKerningForLayer_direction_(layer1, direction)
					if leftKern != rightKern:
						print(f"{glyphname1}-{glyphname2}-{glyphname1}: exception not symmetric: {leftKern} vs. {rightKern}")
						tabString += f"/{glyphname1}/{glyphname2}/{glyphname1}\n"

if tabString:
	# opens new Edit tab:
	thisFont.newTab(tabString)
else:
	Message(title="No Asymmetries", message="Found no asymmetries in the kerning of this master.", OKButton=None)
