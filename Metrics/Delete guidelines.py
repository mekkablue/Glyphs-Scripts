#MenuTitle: Delete guidelines
# -*- coding: utf-8 -*-
"""Delete all local guidelines in selected glyphs."""

import GlyphsApp

selectedLayers = Glyphs.font.selectedLayers

def process( thisLayer ):
	thisLayer.setGuideLines_([])

for thisLayer in selectedLayers:
	print "Processing", thisLayer.parent.name
	process( thisLayer )
