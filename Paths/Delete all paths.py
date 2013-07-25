#MenuTitle: Delete all paths
"""Deletes all paths in visible layers of selected glyphs."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	thisLayer.parent.beginUndo()
	
	for i in range( len( thisLayer.paths ))[::-1]:
		del thisLayer.paths[i]
		
	thisLayer.parent.endUndo()	

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print "Clearing", thisLayer.parent.name
	process( thisLayer )

Font.enableUpdateInterface()

