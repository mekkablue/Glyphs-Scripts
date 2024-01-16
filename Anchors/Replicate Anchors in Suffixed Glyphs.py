# MenuTitle: Replicate Anchors in Suffixed Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Goes through your selected, dot-suffixed glyphs and copies the anchors and anchor positions of the base glyph into them. E.g. A.ss01 will have the same anchor positions as A.
"""

from GlyphsApp import Glyphs, Message


def process(thisLayer):
	glyphName = thisLayer.parent.name
	baseGlyphName = glyphName[:glyphName.find(".")]
	baseGlyph = Font.glyphs[baseGlyphName]
	baseLayer = baseGlyph.layers[thisLayer.master.id]

	print("Layer: %s, replicating from %s" % (thisLayer.name, baseGlyphName))

	anchorCount = 0
	for baseAnchor in baseLayer.anchors:
		thisAnchor = baseAnchor.copy()
		thisLayer.anchors[thisAnchor.name] = thisAnchor
		anchorCount += 1
		print("   Added %s at %i, %i" % (thisAnchor.name, thisAnchor.x, thisAnchor.y))

	return anchorCount


Font = Glyphs.font
selectedGlyphs = [layer.parent for layer in Font.selectedLayers if "." in layer.parent.name]

Glyphs.clearLog()  # clears macro window log
print("Replicate Anchors in Suffixed Glyphs\nFont: ‘%s’" % Font.familyName)
print("%i glyph%s selected, %i of which suffixed." % (
	len(Font.selectedLayers),
	"" if len(Font.selectedLayers) == 1 else "s",
	len(selectedGlyphs),
))

anchorCount, layerCount = 0, 0
for thisGlyph in selectedGlyphs:
	print("\n%s" % thisGlyph.name)
	# thisGlyph.beginUndo()  # undo grouping causes crashes
	for thisLayer in thisGlyph.layers:
		if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
			layerCount += 1
			anchorCount += process(thisLayer)
	# thisGlyph.endUndo()  # undo grouping causes crashes

print("\nDone.")

Message(
	title="Replicate Anchors Report",
	message="Set or reset %i anchor%s on %i layer%s of %i glyph%s. Detailed report in Macro Window." % (
		anchorCount,
		"" if anchorCount == 1 else "s",
		layerCount,
		"" if layerCount == 1 else "s",
		len(selectedGlyphs),
		"" if len(selectedGlyphs) == 1 else "s",
	),
	OKButton=None,
)
