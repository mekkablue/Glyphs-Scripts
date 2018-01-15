#MenuTitle: Align Selection to Ascender
# -*- coding: utf-8 -*-
__doc__="""
Align selected paths (and parts of paths) in the frontmost layer to the Ascender.
"""



Font = Glyphs.font
Doc = Glyphs.currentDocument
myAscender = Font.selectedFontMaster.ascender
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
		thisNode.y += ( myAscender - highestY )

	Font.enableUpdateInterface()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
