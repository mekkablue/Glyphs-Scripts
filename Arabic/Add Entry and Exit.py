#MenuTitle: Add Entry and Exit Anchors
# -*- coding: utf-8 -*-
__doc__="""
Adds exit and entry anchors to Arabic init, medi and fina glyphs.
"""

import GlyphsApp

Glyphs.clearLog()
Glyphs.showMacroWindow()

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def findOncurveAtRSB( thisLayer ):
	layerWidth = thisLayer.width
	myRSBnodes = []
	
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			if thisNode.type != GSOFFCURVE and abs( thisNode.x - layerWidth ) < 1.0:
				myRSBnodes.append( thisNode )
	
	if len( myRSBnodes ) == 1:
		return myRSBnodes[0]
	else:
		print "%s: %s potential entry points" % ( thisLayer.parent.name, len( myRSBnodes ) )
		return None

def process( thisLayer ):
	listOfAnchorNames = [ a.name for a in thisLayer.anchors ]
	glyphName = thisLayer.parent.name
	
	# add exit at 0,0:
	if ".init" in glyphName or ".medi" in glyphName:
		if len( thisLayer.paths ) > 0:
			if "exit" not in listOfAnchorNames:
				myExit = GSAnchor( "exit", NSPoint( 0.0, 0.0 ) )
				thisLayer.addAnchor_( myExit )
				print "%s: exit" % glyphName
	
	# add entry at RSB:
	if ".medi" in glyphName or ".fina" in glyphName:
		if "entry" not in listOfAnchorNames:
			myEntryPoint = findOncurveAtRSB( thisLayer )
			if myEntryPoint != None:
				myEntry = GSAnchor( "entry", NSPoint( myEntryPoint.x, myEntryPoint.y ) )
				thisLayer.addAnchor_( myEntry )
				print "%s: entry" % glyphName
	

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
