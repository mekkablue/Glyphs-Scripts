# MenuTitle: Lines by Master
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Reduplicates your edit text across masters, will add one line per master. Careful, ignores everything after the first newline.
"""

from Foundation import NSMutableAttributedString, NSAttributedString
from GlyphsApp import Glyphs, GSControlLayer, GSLayer, GSBackgroundLayer

thisFont = Glyphs.font

glyphs3 = Glyphs.versionNumber >= 3
cutoff = []
names = []
for i, l in enumerate(thisFont.currentTab.layers):
	if isinstance(l, GSControlLayer):
		cutoff.append(i)
	else:
		if not cutoff:
			names.append(l.parent.name)

theseLayers = []
for m in thisFont.masters:
	for gname in names:
		layer = thisFont.glyphs[gname].layers[m.id]
		# print(layer)
		theseLayers.append(layer)

	theseLayers.append(GSControlLayer.newline())

if theseLayers:
	if glyphs3:
		thisFont.currentTab.layers.extend(theseLayers)
	else:
		for layer in theseLayers:
			thisFont.currentTab.layers.append(layer)
