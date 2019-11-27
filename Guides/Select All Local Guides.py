#MenuTitle: Select All Local Guides in Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Selects all guides in the selected glyph(s).
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def selectGuidesOnLayer( thisLayer ):
	thisLayer.clearSelection()
	for thisGuide in thisLayer.guides:
		thisLayer.selection.append( thisGuide )
	return len(thisLayer.selection)

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	numberOfGuides = selectGuidesOnLayer( thisLayer )
	print("Selected %i guides in %s" % ( numberOfGuides, thisGlyph.name ))
	