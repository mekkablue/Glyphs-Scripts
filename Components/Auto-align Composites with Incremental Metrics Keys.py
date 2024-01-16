# MenuTitle: Auto-align Composites with Incremental Metrics Keys
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
For the frontmost font, auto-aligns composites where only the first component’s alignment is disabled. Ignores .tf, .tosf and math operators. Will open a tab with affected glyph layers.
"""

from GlyphsApp import Glyphs, Message

thisFont = Glyphs.font

tabLayers = []
for g in thisFont.glyphs:
	if ".tf" in g.name or ".tosf" in g.name or g.subCategory == "Math":
		continue
		# skip where acceptable
	for layer in g.layers:
		if (layer.isMasterLayer or layer.isSpecialLayer) and layer.components and not layer.paths and layer.components[0].alignment == -1:
			firstComp = layer.components[0]
			if len(layer.components) > 0:
				otherAlignments = [c.alignment == 1 for c in layer.components[1:]]
				if not all(otherAlignments):
					tabLayers.append(layer)
					print(f"⚠️ {g.name}, {layer.name}: subsequent components aligned ({', '.join([c.name for c in layer.components[1:]])})")
					continue
			left = int(round(firstComp.x))
			if left != 0:
				leftIncrement = f"=={left:+}"
				layer.leftMetricsKey = leftIncrement
			right = int(round(layer.width - firstComp.componentLayer.width - firstComp.x))
			if right != 0:
				rightIncrement = f"=={right:+}"
				layer.rightMetricsKey = rightIncrement
			firstComp.makeEnableAlignment()
			print(f"✅ {g.name}, {layer.name}: {leftIncrement} ↔️ {rightIncrement}, width kept at {layer.width}")
			tabLayers.append(layer)
if tabLayers:
	newTab = thisFont.newTab()
	newTab.layers = tabLayers
else:
	Message(
		"Did not find any composites where the first component was not aligned. (Note: math operators and tabular figures are ignored.)",
		title='Nothing to align'
	)
