#MenuTitle: Lines by Master
# -*- coding: utf-8 -*-
__doc__="""
Reduplicates your edit text across masters, will add one line per master. Careful, ignores everything after the first newline.
"""


cutoff = []
names = []
for i,l in enumerate(Font.currentTab.layers):
	if type(l) == GSControlLayer:
		cutoff.append(i)
	else:
		if not cutoff:
			names.append( l.parent.name )

Font.currentTab.layers = []
for m in Font.masters:
	for gname in names:
		layer = Font.glyphs[gname].layers[m.id]
		print layer
		Font.currentTab.layers.append( layer )
	Font.currentTab.layers.append( GSControlLayer.newline() )