#MenuTitle: Delete guidelines
# -*- coding: utf-8 -*-
__doc__="""
Delete all local guidelines in selected glyphs.
"""

import GlyphsApp

selectedLayers = Glyphs.currentDocument.selectedLayers()

def process( thisLayer ):
	thisLayer.setGuideLines_([])

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Deleting guidelines in:", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()
