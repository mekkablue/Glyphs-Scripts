#MenuTitle: Add All Missing Color Layers to Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Adds a duplicate of the fallback (master) layer for each color defined in the Color Palettes parameter, for each selected glyph.
"""

def glyphAlreadyHasLayerForThisColor(glyph, mID, colorIndex):
	for layer in glyph.layers:
		if layer.associatedMasterId == mID:
			try:
				# GLYPHS 3
				if layer.isColorPaletteLayer() and layer.attributeForKey_("colorPalette") == i:
					return True
			except:
				# GLYPHS 2
				if layer.name == "Color %i" % colorIndex:
					return True
	return False

def process(thisGlyph, mID, paletteSize):
	for i in range(paletteSize):
		if glyphAlreadyHasLayerForThisColor(thisGlyph, mID, i):
			print("⚠️ Skipping Color %i: already exists" % i)
		else:
			newLayer = thisGlyph.layers[mID].copy()
			try:
				# GLYPHS 3
				newLayer.setColorPaletteLayer_(1)
				newLayer.setAttribute_forKey_(i, "colorPalette")
			except:
				# GLYPHS 2
				newLayer.name = "Color %i" % i
			thisGlyph.layers.append(newLayer)
			print("✅ Added: Color %i" % i)

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
selectedGlyphs = [l.parent for l in selectedLayers]
Glyphs.clearLog() # clears log in Macro window

CPAL = None
parameterName = "Color Palettes"

for m in thisFont.masters:
	mID = m.id
	CPAL = m.customParameters[parameterName]

if not CPAL:
	CPAL = thisFont.customParameters[parameterName]

if CPAL:
	paletteSize = len(CPAL[0])
	for thisGlyph in selectedGlyphs:
		print("\n🔠 %s" % thisGlyph.name)
		process(thisGlyph, mID, paletteSize)
else:
	Message(
		title="No Palette Found",
		message="No ‘Color Palettes’ parameter found in Font Info > Font or Font Info > Masters. Please add the parameter and try again.",
		OKButton=None,
		)
