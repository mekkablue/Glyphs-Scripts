#MenuTitle: New Tab with Zero Handles
# -*- coding: utf-8 -*-
__doc__="""
Opens a new tab with glyphs containing zero handles.
"""

import GlyphsApp

thisFont = Glyphs.font # frontmost font
thisFontMasterID = thisFont.selectedFontMaster.id # active master

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		numberOfNodes = len(thisPath.nodes)
		for i in range(numberOfNodes-1):
			thisNode = thisPath.nodes[i]
			if thisNode.type == 65:
				prevNodeIndex = (i-1) % numberOfNodes
				nextNodeIndex = (i+1) % numberOfNodes
				prevNode = thisPath.nodes[prevNodeIndex]
				nextNode = thisPath.nodes[nextNodeIndex]
				if thisNode.position == prevNode.position or thisNode.position == nextNode.position:
					return True
	return False

listOfGlyphNames = []

for thisGlyph in thisFont.glyphs:
	thisLayer = thisGlyph.layers[thisFontMasterID]
	if process( thisLayer ):
		glyphName = thisGlyph.name
		print "Found Zero Handle in", glyphName
		listOfGlyphNames.append( glyphName )

if listOfGlyphNames:
	# opens new Edit tab:
	from PyObjCTools.AppHelper import callAfter
	callAfter( Glyphs.currentDocument.windowController().addTabWithString_, "/%s" % ("/".join(listOfGlyphNames)) )
else:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print "No glyphs with zero handles found."