#MenuTitle: Combining Mark Maker
# -*- coding: utf-8 -*-
"""Goes through your selected marks and adds a combining, non-spacing copy of it to your font, e.g., for acute and dieresis.case, it will add acutecomb and dieresiscomb.case."""

import GlyphsApp
from math import tan, pi

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers
selection = selectedLayers[0].selection()

italicAngle   = FontMaster.italicAngle
allGlyphNames = [ g.name for g in Font.glyphs ]
marksSpacing  = [ "acute", "breve", "caron", "cedilla", "circumflex", "dieresis", "dotaccent", "grave", "hungarumlaut", "macron", "ring", "tilde" ]
defaultTop    = FontMaster.capHeight + 10.0
defaultBottom = FontMaster.descender
suffix = "comb"

def addAnchor( thisLayer, anchorName, x, y ):
	newAnchorPosition = NSPoint()
	newAnchorPosition.x = x
	newAnchorPosition.y = y
	newAnchor = GSAnchor( anchorName, newAnchorPosition )
	thisLayer.addAnchor_( newAnchor )

def addCombiningAnchors( thisLayer ):
	theseBounds = thisLayer.bounds
	for thisAnchor in thisLayer.anchors:
		if thisAnchor.name == "_top":
			oldX, oldY = thisAnchor.position # NSPoint is brided as a tupel
			
			newY = NSMaxY(theseBounds)
			if newY == 0.0:
				newY = defaultTop
			newX = oldX + ( newY - oldY ) * tan( italicAngle / 180.0 * pi )
			
			addAnchor( thisLayer, "top", newX, newY )
			
		if thisAnchor.name == "_bottom":
			oldX, oldY = thisAnchor.position
			
			newY = NSMinY(theseBounds)
			if newY == 0.0:
				newY = defaultBottom
			newX = oldX + ( newY - oldY ) * tan( italicAngle / 180.0 * pi )
			
			addAnchor( thisLayer, "bottom", newX, newY)

def process( spacingAccent ):
	thisGlyphName = spacingAccent.name
	
	for thisMarkName in marksSpacing:
		if thisGlyphName.find( thisMarkName ) == 0:
			myCombName = thisGlyphName.replace( thisMarkName, thisMarkName + suffix )
			if myCombName not in allGlyphNames:
				
				# Create new glyph:
				combiningAccent = spacingAccent.copy()
				combiningAccent.name = myCombName
				
				# Add glyph to font
				Font.glyphs.append( combiningAccent )
				
				# Add _top and _bottom anchors
				for thisLayer in Font.glyphs[ myCombName ].layers:
					addCombiningAnchors( thisLayer )

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	process( thisGlyph )

Font.enableUpdateInterface()
