#MenuTitle: Delete components
"""Delete Components for selected glyphs."""

import GlyphsApp

Doc  = Glyphs.currentDocument
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	while len(thisLayer.components) > 0:
		print "  Deleting component", thisLayer.components[0].componentName
		del thisLayer.components[0]

for thisLayer in selectedLayers:
	print "Processing", thisLayer.parent.name
	process( thisLayer )
