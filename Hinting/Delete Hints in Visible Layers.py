#MenuTitle: Delete Hints in Visible Layers
"""Delete all hints in active layers of selected glyphs."""

import GlyphsApp

print "Deleting hints in active layer:"
Layers = Glyphs.font.selectedLayers
for Layer in Layers:
	print "Processing:", thisLayer.parent.name
	if len(Layer.hints) > 0:
		Layer.hints = None