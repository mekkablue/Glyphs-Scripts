#MenuTitle: Align Selection to x-Height
# -*- coding: utf-8 -*-
__doc__="""
Align selected paths (and parts of paths) in the frontmost layer to the x-Height.
"""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
myXHeight = Font.selectedFontMaster.xHeight
selectedLayer = Font.selectedLayers[0]

try:
	try:
		# until v2.1:
		selection = selectedLayer.selection()
	except:
		# since v2.2:
		selection = selectedLayer.selection
	
	highestY = max( ( n.y for n in selection ) )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.y += ( myXHeight - highestY )

	Font.enableUpdateInterface()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
