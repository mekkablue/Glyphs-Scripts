#MenuTitle: Copy Kerning Exceptions to Double Accents
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Copies Kerning exceptions with abreve, acircumflex, ecircumflex, ocircumflex, udieresis into Vietnamese and Pinyin double accents.
"""

thisFont = Glyphs.font # frontmost font
allGlyphNames = [g.name for g in thisFont.glyphs if g.export]

baseGlyphNames = (
	"Abreve", "Acircumflex", "Ecircumflex", "Ocircumflex", "Udieresis", "Ohorn", "Uhorn", "abreve", "acircumflex", "ecircumflex", "ocircumflex", "udieresis", "ohorn", "uhorn"
	)

baseGlyphIDs = [thisFont.glyphs[g].id for g in baseGlyphNames if thisFont.glyphs[g] and thisFont.glyphs[g].export]

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

for i, baseGlyphID in enumerate(baseGlyphIDs):
	baseGlyphName = baseGlyphNames[i]
	doubleaccentIDs = [thisFont.glyphs[g].id for g in allGlyphNames if g.startswith(baseGlyphName) and g != baseGlyphName and not "." in g]
	print("\nCopying exceptions for: %s" % baseGlyphName)
	if doubleaccentIDs:
		for thisMaster in thisFont.masters:
			print(" Master: %s" % repr(thisMaster))
			masterKerning = thisFont.kerning[thisMaster.id]

			# abreve on the left side:
			if baseGlyphID in masterKerning:
				for rightKey in masterKerning[baseGlyphID]:
					kernValue = masterKerning[baseGlyphID][rightKey]
					for doubleaccentID in doubleaccentIDs:

						# get the name of the double accent:
						doubleaccentName = thisFont.glyphForId_(doubleaccentID).name

						# if rightKey is a glyph ID, it must be converted into a glyph name:
						rightKeyName = rightKey
						if rightKeyName[0] != "@":
							rightKeyName = thisFont.glyphForId_(rightKey).name

						thisFont.setKerningForPair(thisMaster.id, doubleaccentName, rightKeyName, kernValue)
						print("  Added: %s ⟺ %s (%.1f)" % (doubleaccentName, rightKeyName, kernValue))

			# abreve on the right side:
			for leftKey in masterKerning.keys():
				if baseGlyphID in masterKerning[leftKey].keys():
					kernValue = masterKerning[leftKey][baseGlyphID]
					for doubleaccentID in doubleaccentIDs:

						# get the name of the double accent:
						doubleaccentName = thisFont.glyphForId_(doubleaccentID).name

						# if rightKey is a glyph ID, it must be converted into a glyph name:
						leftKeyName = leftKey
						if leftKeyName[0] != "@":
							leftKeyName = thisFont.glyphForId_(leftKey).name

						thisFont.setKerningForPair(thisMaster.id, leftKeyName, doubleaccentName, kernValue)
						print("  Added: %s ⟺ %s (%.1f)" % (leftKeyName, doubleaccentName, kernValue))
