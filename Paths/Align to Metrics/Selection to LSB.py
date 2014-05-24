#MenuTitle: Align Selection to LSB
# -*- coding: utf-8 -*-
__doc__="""
Align selected paths (and parts of paths) in the frontmost layer to the LSB.
"""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
selectedLayer = Font.selectedLayers[0]

try:
	selection = selectedLayer.selection()
	leftMostX = min( ( n.x for n in selection ) )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.x -= leftMostX

	Font.enableUpdateInterface()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
