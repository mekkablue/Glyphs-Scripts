# MenuTitle: Snap selected points to nearest metric in all masters
# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

__doc__ = """
Select points and run this script to snap them to the nearest metric in each compatible layer, given they are no more than 2 units away from the metric. Reports in the Macro window.
"""

from GlyphsApp import Glyphs, GSNode

threshold = 2
alignedNodesCount = 0

for selectedLayer in Glyphs.font.selectedLayers:
	glyph = selectedLayer.parent
	originalCompareString = selectedLayer.compareString()

	for node in selectedLayer.selection:
		if not isinstance(node, GSNode):
			continue
		pathIndex = selectedLayer.indexPathOfNode_(node)[0]
		nodeIndex = selectedLayer.indexPathOfNode_(node)[1]

		for layer in glyph.layers:
			if layer.compareString() != originalCompareString:
				continue

			node = layer.paths[pathIndex].nodes[nodeIndex]
			metrics = sorted(set([m.position for m in layer.metrics]))
			for metric in metrics:
				diff = abs(node.y - metric)
				if diff != 0 and diff <= threshold:
					node.y = metric
					alignedNodesCount += 1
					break

print(f"Aligned {alignedNodesCount} points in {', '.join([selectedLayer.parent.name for l in Glyphs.font.selectedLayers])}.")
