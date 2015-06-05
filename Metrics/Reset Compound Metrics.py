#MenuTitle: Reset Compound Metrics to First Component
# -*- coding: utf-8 -*-
__doc__="""
Looks for the first component in a compound glyph and sets it back to x=0 and inherits its width. Useful for syncing numerators and denominators.
"""

import GlyphsApp


Font = Glyphs.font
FontMasterID = Font.selectedFontMaster.id
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	if len( thisLayer.components ) > 0:
		myComp = thisLayer.components[0]
		myCompName = myComp.componentName
		print "-- W: %.1f; first Comp: %s (%i, %i)" % ( thisLayer.width, myCompName, myComp.position.x, myComp.position.y )
		
		myCompLayer = Font.glyphs[ myCompName ].layers[ FontMasterID ]
		print "-- W: %.1f, LSB: %.1f, RSB: %.1f" % ( myCompLayer.width, myCompLayer.LSB, myCompLayer.RSB )
		
		newCompPos = NSPoint( 0, myComp.position.y )
		myComp.position = newCompPos
		thisLayer.width = myCompLayer.width

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()
	print

Font.enableUpdateInterface()
