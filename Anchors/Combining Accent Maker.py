#MenuTitle: Combining Mark Maker
# -*- coding: utf-8 -*-
"""Goes through your selected marks and adds a combining, non-spacing copy of it to your font, e.g., for acute and dieresis.case, it will add acutecomb and dieresiscomb.case."""

import GlyphsApp
from math import tan, pi

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers

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
			oldX, oldY = thisAnchor.position
			newY = theseBounds.origin.y + theseBounds.size.height # or: NSMaxY(theseBounds)

			if newY == 0.0:
				newY = defaultTop
			newX = oldX + ( newY - oldY ) * tan( italicAngle / 180.0 * pi )
			
			addAnchor( thisLayer, "top", newX, newY )
			
		if thisAnchor.name == "_bottom":
			oldX, oldY = thisAnchor.position
			newY = theseBounds.origin.y # or: NSMinY(theseBounds)

			if newY == 0.0:
				newY = defaultBottom
			newX = oldX + ( newY - oldY ) * tan( italicAngle / 180.0 * pi )
				
			addAnchor( thisLayer, "bottom", newX, newY )

def process( spacingAccent ):
	thisGlyphName = spacingAccent.name
	
	for thisMarkName in marksSpacing:
		if thisGlyphName.find( thisMarkName ) == 0:
			myCombName = thisGlyphName.replace( thisMarkName, thisMarkName + suffix )
			if myCombName not in allGlyphNames:
				
				# Create new glyph:
				combiningAccent = spacingAccent.copy()
				combiningAccent.name = myCombName
				
				# Add glyph to font:
				Font.glyphs.append( combiningAccent )
				
				for thisLayer in Font.glyphs[ myCombName ].layers:
					# Clear out the layer:
					thisLayer.components = ()
					thisLayer.paths = ()
					# Add spacing anchor as component:
					spacingAccentComp = GSComponent( spacingAccent, NSPoint( 0.0, 0.0 ) )
					thisLayer.addComponent_( spacingAccentComp )
					# Add _top and _bottom anchors:
					addCombiningAnchors( thisLayer )

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	process( thisGlyph )

Font.enableUpdateInterface()
