#MenuTitle: Insert exit and entry Anchors to Selected Positional Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds exit and entry anchors to (Arabic) init, medi and fina glyphs, for cursive attachment.
"""

from Foundation import NSPoint

Glyphs.clearLog()
Glyphs.showMacroWindow()

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def findOncurveAtRSB( thisLayer ):
	layerWidth = thisLayer.width
	
	try:
		paths = [p for p in thisLayer.shapes if type(p)==GSPath]
	except:
		paths = thisLayer.paths
	
	rightMostPoint = None
	for thisPath in paths:
		print(thisPath)
		for thisNode in thisPath.nodes:
			print(thisNode.x)
			if thisNode.type != GSOFFCURVE and (rightMostPoint==None or rightMostPoint.x < thisNode.x):
				rightMostPoint = thisNode
	
	if rightMostPoint:
		return rightMostPoint
	else:
		print("%s: No potential entry point" % (thisLayer.parent.name))
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
				print("%s: exit" % glyphName)
	
	# add entry at RSB:
	if ".medi" in glyphName or ".fina" in glyphName:
		if "entry" not in listOfAnchorNames:
			myEntryPoint = findOncurveAtRSB( thisLayer )
			if myEntryPoint != None:
				myEntry = GSAnchor( "entry", NSPoint( myEntryPoint.x, myEntryPoint.y ) )
				thisLayer.anchors.append( myEntry )
				print("%s: entry" % glyphName)
	

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
