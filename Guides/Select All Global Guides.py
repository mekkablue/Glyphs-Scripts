#MenuTitle: Select All Global Guides
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Selects all global guides.
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def selectGuidesOnLayer( thisLayer ):
	thisMaster = thisLayer.master
	thisLayer.clearSelection()
	for thisGuide in thisMaster.guides:
		thisLayer.selection.append( thisGuide )
	return len(thisLayer.selection)

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	numberOfGuides = selectGuidesOnLayer( thisLayer )
	print("Selected %i guides in %s" % ( numberOfGuides, thisGlyph.name ))
	