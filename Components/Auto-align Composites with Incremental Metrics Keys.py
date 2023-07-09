#MenuTitle: Auto-align Composites with Incremental Metrics Keys
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
For the frontmost font, auto-aligns composites where only the first component’s alignment is disabled. Ignores .tf, .tosf and math operators. Will open a tab with affected glyph layers.
"""

thisFont = Glyphs.font
tabLayers = []
for g in thisFont.glyphs:
	if ".tf" in g.name or ".tosf" in g.name or g.subCategory=="Math":
		continue
		# skip where acceptable
	for l in g.layers:
		if (l.isMasterLayer or l.isSpecialLayer) and l.components and not l.paths and l.components[0].alignment==-1:
			firstComp = l.components[0]
			if len(l.components) > 0:
				otherAlignments = [c.alignment==1 for c in l.components[1:]]
				if not all(otherAlignments):
					tabLayer.append(l)
					print(f"⚠️ {g.name}, {l.name}: subsequent components aligned ({', '.join([c.name for c in l.components[1:]])})")
					continue
			left = int(round(firstComp.x))
			if left != 0:
				leftIncrement = f"=={left:+}"
				l.leftMetricsKey = leftIncrement
			right = int(round(l.width-firstComp.componentLayer.width-firstComp.x))
			if right != 0:
				rightIncrement = f"=={right:+}"
				l.rightMetricsKey = rightIncrement
			firstComp.makeEnableAlignment()
			print(f"✅ {g.name}, {l.name}: {leftIncrement} ↔️ {rightIncrement}, width kept at {l.width}")
			tabLayers.append(l)
if tabLayers:
	newTab = thisFont.newTab()
	newTab.layers = tabLayers
else:
	Message("Did not find any composites where the first component was not aligned. (Note: math operators and tabular figures are ignored.)", title='Nothing to align', OKButton=None)

