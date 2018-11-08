#MenuTitle: Convert Layerfont to CPAL+COLR Font
# -*- coding: utf-8 -*-
__doc__="""
Turns a layered color font into a single-master font with a CPAL and COLR layers in each glyph. It will take the first master as default.
"""

thisFont = Glyphs.font # frontmost font
fallbackMaster = thisFont.masters[0] # first master
fallbackMasterID = fallbackMaster.id
namesOfMasters = [ m.name for m in thisFont.masters ]

def masterColorFromColor( thisMaster, thisColor ):
	#(NSColor*)contrastingLabelColor {NSColor *rgbColor = [self colorUsingColorSpaceName:NSCalibratedRGBColorSpace];
	red = thisColor.redComponent()
	green = thisColor.greenComponent()
	blue = thisColor.blueComponent()
	alpha = thisColor.alphaComponent()
	colorText = "%i,%i,%i,%i" % ( red, green, blue, alpha )
	thisMaster.setCustomParameter_forKey_( colorText, "Master Color" )
	
def createCPALfromMasterColors( theseMasters, indexOfTargetMaster ):
	colorList = []
	for i in range(len(theseMasters)):
		thisMaster = theseMasters[i]
		thisMasterColor = thisMaster.customParameters["Master Color"]
		colorList.append( thisMasterColor )
	
	colorTuple = tuple([tuple(colorList)])
	targetMaster = theseMasters[indexOfTargetMaster]
	targetMaster.setCustomParameter_forKey_( colorTuple, "Color Palettes" )
	targetMaster.removeObjectFromCustomParametersForKey_( "Master Color" )

def keepOnlyFirstMaster( thisFont ):
	for i in range(len(thisFont.masters))[:0:-1]:
		thisFont.removeFontMasterAtIndex_(i)

def process( thisGlyph ):
	for i in range(len(namesOfMasters))[::-1]:
		colorLayerName = "Color %i" % i
		originalLayerName = namesOfMasters[i]
		originalLayer = thisGlyph.layerForName_(originalLayerName)
		thisGlyph.layers[colorLayerName] = originalLayer.copy()
		thisGlyph.layers[colorLayerName].setAssociatedMasterId_(fallbackMasterID)
		thisGlyph.layers[colorLayerName].setName_(colorLayerName)
		
	for i in range(len(thisGlyph.layers))[::-1]:
		thisLayer = thisGlyph.layers[i]
		if thisLayer.name == "orphan":
			del thisLayer
	
thisFont.disableUpdateInterface() # suppresses UI updates in Font View
createCPALfromMasterColors( thisFont.masters, 0 )

for thisGlyph in thisFont.glyphs:
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisGlyph )
	thisGlyph.endUndo()   # end undo grouping

keepOnlyFirstMaster( thisFont )
thisFont.enableUpdateInterface() # re-enables UI updates in Font View

print "Done."
