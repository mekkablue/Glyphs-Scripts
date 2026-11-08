# MenuTitle: Build APL Greek
__doc__ = """
Create APL Greek glyphs.
"""

from GlyphsApp import Glyphs, GSGlyph, GSComponent

thisFont = Glyphs.font  # frontmost font
aplGlyphNames = ("APLiota", "APLrho", "APLomega", "APLalpha")
Glyphs.clearLog()

if thisFont is None:
	Glyphs.showMacroWindow()
	print("⚠️ Build APL Greek: No font open.")
else:
	for glyphName in aplGlyphNames:
		original = glyphName.replace("APL", "")
		if thisFont.glyphs[original]:
			thisGlyph = thisFont.glyphs[glyphName]
			if not thisGlyph:
				thisGlyph = GSGlyph()
				thisGlyph.name = glyphName
				thisFont.glyphs.append(thisGlyph)

			for thisLayer in thisGlyph.layers:
				thisLayer.clear()
				comp = GSComponent(original)
				thisLayer.shapes.append(comp)
				comp.automaticAlignment = True
		else:
			print(f"{original}: not found in font.")
			Glyphs.showMacroWindow()
