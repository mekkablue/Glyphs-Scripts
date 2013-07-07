#MenuTitle: Insert BCPs into straight segments
# -*- coding: utf-8 -*-
"""Inserts BCPs into straight segments of selected glyphs. The opposite of what the Tidy Up Paths command does. Useful if you want to bend the shape later."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
FontMaster = Doc.selectedFontMaster()
selectedLayers = Doc.selectedLayers()
selection = selectedLayers[0].selection()
minimumLength = 20.0

def triplets( x1, y1, x2, y2 ):
	third1 = NSPoint()
	third1.x = ( x1 * 2 + x2 ) / 3
	third1.y = ( y1 * 2 + y2 ) / 3

	third2 = NSPoint()
	third2.x = ( x1 + x2 * 2 ) / 3
	third2.y = ( y1 + y2 * 2 ) / 3
	
	BCP1 = GSNode()
	BCP1.type = GSOFFCURVE
	BCP1.position = third1
	BCP1.connection = 0
	
	BCP2 = GSNode()
	BCP2.type = GSOFFCURVE
	BCP2.position = third2
	BCP2.connection = 0
	
	return [ BCP1, BCP2 ]

def segmentLength( Node1, Node2 ):
	cath1 = Node2.x - Node1.x
	cath2 = Node2.y - Node1.y
	return ( cath1 ** 2 + cath2 ** 2 ) ** 0.5

def addBCPs( thisLayer ):
	virtualPaths = []
	
	for thisPath in thisLayer.paths:
		# go through all paths and deposit copies of them in vitualPaths
		
		currentNodes = thisPath.nodes
		virtualPath = GSPath()
		
		for i in range( len( currentNodes )):
			thisNode = currentNodes[ i ]
			try:
				previousNode = currentNodes[ i-1 ]
			except:
				previousNode = currentNodes[ -1 ]
			thisType = thisNode.type
			previousType = previousNode.type
			
			# copy the node:
			
			virtualNode = GSNode()
			virtualNode.position = thisNode.position
			virtualNode.connection = thisNode.connection
			virtualNode.type = thisType

			# insert BCPs if straight segment:
			
			if ( thisType == GSLINE or thisType == GSCURVE) and ( previousType == GSLINE or previousType == GSCURVE ):
				if segmentLength( thisNode, previousNode ) > minimumLength:
					[ BCP1, BCP2 ] = triplets( thisNode.position.x, thisNode.position.y, previousNode.position.x, previousNode.position.y )
					virtualPath.nodes.append( BCP2 )
					virtualPath.nodes.append( BCP1 )
				
					# change virtual node type to curve:
					virtualNode.type = GSCURVE
				
			# insert node:
			
			virtualPath.nodes.append( virtualNode )
			
		
		if thisPath.closed:
			virtualPath.closed = True
		
		virtualPaths.append( virtualPath )
	
	# delete the original paths:
	for i in range( len( thisLayer.paths ) )[::-1]:
		thisLayer.removePath_( thisLayer.paths[i] )
	
	# add the virtual paths:
	for thisVirtualPath in virtualPaths:
		thisLayer.paths.append( thisVirtualPath )
		
	#Doc.windowController().activeEditViewController().forceRedraw()
	
Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.undoManager().beginUndoGrouping()
	addBCPs( thisLayer )
	thisGlyph.undoManager().endUndoGrouping()

Font.enableUpdateInterface()
