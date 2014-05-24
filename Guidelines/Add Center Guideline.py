#MenuTitle: Create Center Guideline
# -*- coding: utf-8 -*-
__doc__="""
Creates a guideline, horizontally or vertically centered between two selected nodes.
"""

import GlyphsApp

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers
selection = selectedLayers[0].selection()

def addAndSelectGuideline( thisLayer, originPoint, angle ):
	"""Adds a guideline in thisLayer at originPoint, at angle."""
	try:
		myGuideline = GSGuideLine()
		myGuideline.position = originPoint
		myGuideline.angle = angle
		thisLayer.addGuideLine_( myGuideline )
		thisLayer.setSelection_( NSMutableArray.arrayWithObject_(myGuideline) )
		return True
	except Exception as e:
		print e
		return False

if len(selectedLayers) == 1 and len(selection) == 2:
	thisLayer = selectedLayers[0]
	thisGlyph = thisLayer.parent
	firstNode = selection[0]
	secondNode = selection[1]
	
	centerX = ( firstNode.x + secondNode.x ) / 2.0
	centerY = ( firstNode.y + secondNode.y ) / 2.0
	guidelineOrigin = NSPoint( centerX, centerY )
	
	guidelineAngle = 90.0
	xDiff = firstNode.x - secondNode.x
	yDiff = firstNode.y - secondNode.y
	if xDiff < yDiff:
		guidelineAngle = 0.0
	
	thisGlyph.beginUndo()	
	if not addAndSelectGuideline( thisLayer, guidelineOrigin, guidelineAngle ):
		print "Error: Could not add guideline."
	thisGlyph.endUndo()
