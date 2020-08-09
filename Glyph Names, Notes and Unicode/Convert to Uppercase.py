#MenuTitle: Convert to Uppercase
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Turns lowercase names into uppercase names, e.g., `a` → `A`, `ccaron` → `Ccaron`, `aeacute` → `AEacute`, etc.
"""

def uppercaseGlyphName( thisGlyph ):
	originalGlyphName = thisGlyph.name
	glyphNameParts = originalGlyphName.split(".")
	coreName = glyphNameParts[0]
	coreInfo = Glyphs.glyphInfoForName(coreName)
	lowercaseCharacter = coreInfo.unicharString()
	if lowercaseCharacter is None:
		print("⚠️ Cannot determine character for: %s" % originalGlyphName)
		return 0
	else:
		uppercaseCharacter = lowercaseCharacter.upper()
		if lowercaseCharacter == uppercaseCharacter:
			print("🆗 %s: unchanged, cannot be uppercased." % originalGlyphName)
			return 0
		else:
			uppercaseCoreName = Glyphs.niceGlyphName(uppercaseCharacter)
			glyphNameParts[0] = uppercaseCoreName
			uppercaseGlyphName = ".".join(glyphNameParts)
			thisFont = thisGlyph.parent
			if thisFont.glyphs[uppercaseGlyphName]:
				print("❌ %s: cannot convert to %s, glyph already exists." % (originalGlyphName, uppercaseGlyphName))
				return 0
			else:
				thisGlyph.name = uppercaseGlyphName
				thisGlyph.updateGlyphInfo()
				print("✅ %s → %s" % (
					originalGlyphName,
					thisGlyph.name if thisGlyph.name==uppercaseGlyphName else "%s → %s (updated glyph info)" % (uppercaseGlyphName, thisGlyph.name),
					))
				return 1

Glyphs.clearLog() # clears macro window log
Font = Glyphs.font
selectedGlyphs = [ l.parent for l in Font.selectedLayers ]
countSelectedGlyphs = len(selectedGlyphs)
convertedCount = 0
print("Converting %i selected glyphs to uppercase:\n" % countSelectedGlyphs)

Font.disableUpdateInterface()
try:
	for thisGlyph in selectedGlyphs:
		convertedCount += uppercaseGlyphName( thisGlyph )
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	Font.enableUpdateInterface()

# Floating notification:
Glyphs.showNotification( 
	"%s: UC Conversion Finished" % (Font.familyName),
	"Of %i selected glyph%s, %i %s converted to uppercase. Details in Macro Window." % (
		countSelectedGlyphs,
		"" if countSelectedGlyphs==1 else "s",
		convertedCount,
		"was" if convertedCount==1 else "were",
		),
	)

print("\n%i glyph%s converted to uppercase.\nDone." % (
	convertedCount,
	"" if convertedCount==1 else "s",
	))
