#MenuTitle: Delete Hints in Visible Layers
# -*- coding: utf-8 -*-
__doc__="""
Deletes all hints in active layers of selected glyphs.
"""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers
print "Deleting hints in active layer:"

def process( thisLayer ):
	for x in reversed( range( len( thisLayer.hints ))):
		del thisLayer.hints[x]
		
Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print "Processing", thisLayer.parent.name
	process( thisLayer )

Font.enableUpdateInterface()
