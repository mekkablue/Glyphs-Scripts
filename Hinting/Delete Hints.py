#MenuTitle: Delete Hints
"""Delete all hints in active layer of selected glyphs."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedLayers = Doc.selectedLayers()
print "Deleting hints in active layer:"

def process( thisLayer ):
	for x in reversed( range( len( thisLayer.hints ))):
		del thisLayer.hints[x]
		
Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print "Processing", thisLayer.parent.name
	process( thisLayer )

Font.enableUpdateInterface()
