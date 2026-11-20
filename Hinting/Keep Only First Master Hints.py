# MenuTitle: Keep First Master Hints Only
# -*- coding: utf-8 -*-
__doc__ = """
In selected glyphs, delete all hints in all layers except for the first master. Respects Bracket Layers.
"""

from GlyphsApp import Glyphs

Font = Glyphs.font

Glyphs.clearLog()
if Font is None:
	print("⚠️ No font open.")
else:
	selectedGlyphs = [layer.parent for layer in Font.selectedLayers]
	firstMasterName = Font.masters[0].name

	print("Only keeping first-master hints in:")

	for thisGlyph in selectedGlyphs:
		print("- %s" % thisGlyph.name)
		layersToBeProcessed = [layer for layer in thisGlyph.layers if not layer.name.startswith(firstMasterName)]
		for layer in layersToBeProcessed:
			layer.hints = None

	print("Done.")
