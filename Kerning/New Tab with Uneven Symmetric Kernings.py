# MenuTitle: New tab with uneven symmetric kernings
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds kern pairs for symmetric letters like ATA AVA TOT WIW etc. and sees if AT is the same as TA, etc.
"""

from GlyphsApp import Glyphs, Message, GSBIDI, GSLTR
from AppKit import NSNotFound

UC = "AHIMNOTUVWXYАЖИМНОПТФХШЏЫІΑΗΘΙΛΜΝΞΟΠΤΥΦΧΨΩ"
SC = [f"{x.lower()}.sc" for x in UC]
LC = "ilovwxжимноптфхшџыθοχω"
SY = ["period", "colon", "ellipsis", "periodcentered", "hyphen", "endash", "emdash", "quotesingle", "quotedbl", "at", "space", "asterisk", "bar", "brokenbar"]

thisFont = Glyphs.font  # frontmost font
m = thisFont.selectedFontMaster  # active master
Glyphs.clearLog()  # clears log in Macro window
print(f"🔠 Font: {thisFont.familyName}\nⓂ️ Master: {m.name}\n\nFinding uneven kerning symmetries...\n")

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
	for i, glyphname1 in enumerate(glyphnames):
		glyph1 = thisFont.glyphs[glyphname1]
		if not glyph1:
			continue
		for glyphname2 in glyphnames[i:]:
			if glyphname1 == glyphname2:  # AAA makes no sense
				continue
			glyph2 = thisFont.glyphs[glyphname2]
			if not glyph2:
				continue
			if glyph1.script != glyph2.script and not None in (glyph1.script, glyph2.script):
				continue

			layer1 = thisFont.glyphs[glyphname1].layers[m.id]
			layer2 = thisFont.glyphs[glyphname2].layers[m.id]
			direction = glyph1.direction
			if direction == GSBIDI: # no direction
				direction = glyph2.direction
			if direction == GSBIDI: # no direction
				direction = GSLTR # fallback to LTR
			leftKern = layer1.nextKerningForLayer_direction_(layer2, direction)
			if leftKern >= NSNotFound: # NSNotFound
				leftKern = 0
			rightKern = layer2.nextKerningForLayer_direction_(layer1, direction)
			if rightKern >= NSNotFound: # NSNotFound
				rightKern = 0
			if leftKern != rightKern:
				print(f"⚠️ {glyphname1}-{glyphname2}-{glyphname1} not symmetric: {leftKern} vs. {rightKern}")
				tabString += f"/{glyphname1}/{glyphname2}/{glyphname1}\n"
print("\n✅ Done.")

if tabString:
	# opens new Edit tab:
	thisFont.newTab(tabString.strip())
else:
	Message(title="No Asymmetries", message="Found no asymmetries in the kerning of this master.", OKButton=None)
