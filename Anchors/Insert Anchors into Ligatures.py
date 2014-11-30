#MenuTitle: Insert Anchors into Ligatures
# -*- coding: utf-8 -*-
__doc__="""
Inserts base glyph anchors into ligatures with appropriate extensions. E.g. c_e will have top_1, bottom_1, top_2, bottom_2, and ogonek_2.
"""

import GlyphsApp

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
thisFontMasterID = thisFontMaster.id
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def totalWidth( listOfNames ):
	totalWidth = 0
	for thisName in listOfNames:
		try:
			totalWidth += thisFont.glyphs[thisName].layers[thisFontMasterID].width
		except Exception as e:
			print "Error. Could not find the width of %s: %s" % ( thisName, e )
	return totalWidth

def process( thisLayer ):
	thisLayer.setAnchors_(None)
	xOffset = 0
	componentNames = thisLayer.parent.name.split(".")[0].split("_")
	
	offsetFactor = thisLayer.width / totalWidth( componentNames )
	
	for thisIndex in range(len(componentNames)):
		thatName = componentNames[ thisIndex ]
		thatGlyph = thisFont.glyphs[ thatName ]
		thisSuffix = thisIndex + 1
		
		if thatGlyph:
			thatGlyphName = thatGlyph.name
			thatLayer = thatGlyph.layers[ thisFontMasterID ]
			
			for thatAnchor in thatLayer.anchors:
				newAnchor = GSAnchor()
				newAnchor.name = "%s_%i" % ( thatAnchor.name, thisSuffix )
				newAnchor.position = NSPoint( offsetFactor * (thatAnchor.position.x + xOffset), thatAnchor.position.y )
				thisLayer.addAnchor_( newAnchor )
				
			xOffset += thatLayer.width

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyphName = thisGlyph.name
	if "_" in thisGlyphName:
		print "Processing", thisGlyphName
		thisGlyph.beginUndo() # begin undo grouping
		process( thisLayer )
		thisGlyph.endUndo()   # end undo grouping
	else:
		print "Not a ligature: Skipping %s." % thisGlyphName

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
