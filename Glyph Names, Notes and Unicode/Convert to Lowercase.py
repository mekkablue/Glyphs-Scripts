# MenuTitle: Convert to Lowercase
# -*- coding: utf-8 -*-
__doc__ = """
Turns uppercase names into lowercase names, e.g., `A` → `a`, `Ccaron` → `ccaron`, `AEacute` → `aeacute`, etc. Useful for smallcap glyphs.
"""
from GlyphsApp import Glyphs


def lowercaseGlyphName(thisGlyph):
	originalGlyphName = thisGlyph.name
	glyphNameParts = originalGlyphName.split(".")
	coreName = glyphNameParts[0]
	coreInfo = Glyphs.glyphInfoForName(coreName)
	uppercaseCharacter = coreInfo.unicharString()
	if uppercaseCharacter is None:
		print("⚠️ Cannot determine character for: %s" % originalGlyphName)
		return 0
	else:
		lowercaseCharacter = uppercaseCharacter.lower()
		if uppercaseCharacter == lowercaseCharacter:
			print("🆗 %s: unchanged, cannot be lowercased." % originalGlyphName)
			return 0
		else:
			lowercaseCoreName = Glyphs.niceGlyphName(lowercaseCharacter)
			glyphNameParts[0] = lowercaseCoreName
			lowercaseGlyphName = ".".join(glyphNameParts)
			thisFont = thisGlyph.parent
			if thisFont.glyphs[lowercaseGlyphName]:
				print("❌ %s: cannot convert to %s, glyph already exists." % (originalGlyphName, lowercaseGlyphName))
				return 0
			else:
				thisGlyph.name = lowercaseGlyphName
				thisGlyph.updateGlyphInfo()
				print(
					"✅ %s → %s" % (
						originalGlyphName,
						thisGlyph.name if thisGlyph.name == lowercaseGlyphName else "%s → %s (updated glyph info)" % (lowercaseGlyphName, thisGlyph.name),
					)
				)
				return 1


Glyphs.clearLog()  # clears macro window log
Font = Glyphs.font
if not Font:
	print("Please open a font first.")
else:
	selectedGlyphs = [layer.parent for layer in Font.selectedLayers]
	countSelectedGlyphs = len(selectedGlyphs)
	convertedCount = 0
	print("Converting %i selected glyphs to lowercase:\n" % countSelectedGlyphs)

	Font.disableUpdateInterface()
	try:
		for thisGlyph in selectedGlyphs:
			convertedCount += lowercaseGlyphName(thisGlyph)
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
		"%s: LC Conversion Finished" % (Font.familyName),
		"Of %i selected glyph%s, %i %s converted to lowercase. Details in Macro Window." % (
			countSelectedGlyphs,
			"" if countSelectedGlyphs == 1 else "s",
			convertedCount,
			"was" if convertedCount == 1 else "were",
		),
	)

	print("\n%i glyph%s converted to lowercase.\nDone." % (
		convertedCount,
		"" if convertedCount == 1 else "s",
	))
