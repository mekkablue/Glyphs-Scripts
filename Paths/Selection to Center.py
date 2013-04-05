#MenuTitle: Align Selection to Horizontal Center
"""Align selected paths (and parts of paths) in the frontmost layer to the Horizontal Center."""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
selectedLayer = Doc.selectedLayers()[0]
layerCenter = selectedLayer.width // 2

try:
	selection = selectedLayer.selection()
	selectionXList = [ n.x for n in selection ]
	leftMostX = min( selectionXList )
	rightMostX = max( selectionXList )
	selectionCenter = ( leftMostX + rightMostX ) // 2
	centerOffset = float( layerCenter - selectionCenter )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.x += centerOffset

	Font.enableUpdateInterface()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
