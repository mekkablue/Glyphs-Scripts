#MenuTitle: Delete all paths
# -*- coding: utf-8 -*-
__doc__="""
Deletes all paths in visible layers of selected glyphs.
"""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	thisLayer.parent.beginUndo()
	
	for i in range( len( thisLayer.paths ))[::-1]:
		del thisLayer.paths[i]
		
	thisLayer.parent.endUndo()	

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print "Clearing %s." % thisLayer.parent.name
	process( thisLayer )

Font.enableUpdateInterface()

