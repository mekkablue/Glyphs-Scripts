#MenuTitle: Color Composites in Shade of Base Glyph
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Color Composites in a lighter shade of the base glyph. E.g., if your A is has a red label color, then ÄÁÀĂ... will have a lighter shade of red.
"""

from Foundation import NSColor, NSNotFound
prefID = "com.mekkablue.colorCompositesInShadeOfBaseGlyph"

thisFont = Glyphs.font # frontmost font
thisMasterID = thisFontMaster = thisFont.selectedFontMaster.id # active master ID
glyphNamesWithColors = [g.name for g in thisFont.glyphs if g.color != NSNotFound and g.category != "Mark"]

def registerPref(prefID, prefName, fallbackValue):
	prefDomain = "%s.%s" % (prefID, prefName)
	Glyphs.registerDefault(prefDomain, fallbackValue)
	if Glyphs.defaults[prefDomain] is None:
		Glyphs.defaults[prefDomain] = fallbackValue

def getPref(prefID, prefName):
	prefDomain = "%s.%s" % (prefID, prefName)
	return Glyphs.defaults[prefDomain]

def rgbaForColorObject(colorObject):
	r = colorObject.redComponent()
	g = colorObject.greenComponent()
	b = colorObject.blueComponent()
	a = colorObject.alphaComponent()
	return r, g, b, a

# retrieve current values:
registerPref(prefID, "shadeFactor", 0.5)
factor = getPref(prefID, "shadeFactor")

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print("Shading composites:\n")

for thisComposite in [g for g in thisFont.glyphs if g.layers[thisMasterID].components]:
	firstComponent = thisComposite.layers[thisMasterID].components[0]
	baseGlyph = firstComponent.component
	if baseGlyph.colorObject:
		r, g, b, a = rgbaForColorObject(baseGlyph.colorObject)
		# brightening up RGB, keeping A the same:
		r += (1.0 - r) * factor
		g += (1.0 - g) * factor
		b += (1.0 - b) * factor
		compositeColor = NSColor.colorWithRed_green_blue_alpha_(r, g, b, a)
		thisComposite.colorObject = compositeColor
		print("✅ %03ir %03ig %03ib → %s" % (100 * r, 100 * g, 100 * b, thisComposite.name))
	else:
		print("⚠️ %s: no color set in %s" % (thisComposite.name, baseGlyph.name))
