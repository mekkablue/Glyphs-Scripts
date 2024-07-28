#MenuTitle: Snap selected points to nearest metric in all masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Select points and run this script to snap them to the nearest metric in each compatible layer, given they are no more than 2 units away from the metric. Reports in the Macro window.
"""

threshold = 2
alignedNodesCount = 0

for l in Glyphs.font.selectedLayers:
	glyph = l.parent
	originalCompareString = l.compareString()

	for node in l.selection:
		if not isinstance(node, GSNode):
			continue
		pathIndex = l.indexPathOfNode_(node)[0]
		nodeIndex = l.indexPathOfNode_(node)[1]

		for layer in glyph.layers:
			if layer.compareString() != originalCompareString:
				continue
				
			node = layer.paths[pathIndex].nodes[nodeIndex]
			metrics = sorted(set([m.position for m in l.metrics]))
			for metric in metrics:
				diff = abs(node.y - metric)
				if diff != 0 and diff <= threshold:
					node.y = metric
					alignedNodesCount += 1
					break

print(f"Aligned {alignedNodesCount} points in {', '.join([l.parent.name for l in Glyphs.font.selectedLayers])}.")