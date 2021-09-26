#MenuTitle: Convert Layerfont to CPAL+COLR Font
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Turns a layered color font into a single-master font with a CPAL and COLR layers in each glyph. It will take the first master as default.
"""

from timeit import default_timer as timer
from AppKit import NSMutableArray, NSColorSpace, NSColorSpaceColor

# start taking time:
start = timer()

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
	
def createCPALfromMasterColors( thisFont, theseMasters, indexOfTargetMaster ):
	# create color palette:
	palette = NSMutableArray.alloc().init()
	
	# go through all masters and collect their color info:
	for thisMaster in theseMasters:
		# black as fallback:
		r,g,b,a = 0,0,0,1
		
		try:
			if Glyphs.versionNumber>=3:
				# GLYPHS 3
				color = thisMaster.customParameters["Master Color"]
				color = color.colorUsingSRGBColorSpace()
				r,g,b,a = (
					color.redComponent(),
					color.greenComponent(),
					color.blueComponent(),
					color.alphaComponent(),
				)
			else:
				# GLYPHS 2
				# query master color:
				colorString = thisMaster.customParameters["Master Color"]
				# black as fallback:
				if not colorString:
					colorString = "0,0,0,255"
				# derive RGBA values:
				r,g,b,a = [ float(value)/255 for value in colorString.split(",") ]
		except:
			print("⚠️ Could not convert color of master %s, defaulting to black." % thisMaster.name)
		
		# create SRGB color:
		color = NSColorSpaceColor.colorWithRed_green_blue_alpha_(r,g,b,a)
		color = color.colorUsingColorSpace_(NSColorSpace.sRGBColorSpace())
		# and add it to the palette:
		palette.addObject_( color )
	
	# create array of palettes, containing the one palette we just created:
	paletteArray = NSMutableArray.alloc().initWithObject_(palette)
	
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		thisFont.customParameters["Color Palettes"] = paletteArray
	else:
		# GLYPHS 2
		# add that array as "Color Palettes" parameter to target (=usually first) master
		targetMaster = theseMasters[indexOfTargetMaster]
		del targetMaster.customParameters["Master Color"]
		targetMaster.customParameters["Color Palettes"] = paletteArray
	
	print("Created CPAL palette with %i colors." % len(theseMasters))

def keepOnlyFirstMaster( thisFont ):
	# delete all masters except first one:
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		while len(Font.masters)>1:
			del Font.masters[-1]
	else:
		# GLYPHS 2
		for i in range(len(thisFont.masters))[:0:-1]:
			thisFont.removeFontMasterAtIndex_(i)
		
	# rename remaining first master:
	thisFont.masters[0].name = "Fallback"
	print("Deleted all masters except first, and renamed it to: %s" % thisFont.masters[0].name)
		
def cleanUpNamelessLayers(thisGlyph):
	for i in range(len(thisGlyph.layers))[:0:-1]:
		thisLayer = thisGlyph.layers[i]
		if not thisLayer.name:
			del thisGlyph.layers[i]
		elif not thisLayer.name.startswith("Color"):
			del thisGlyph.layers[i]

def duplicatePathsIntoFallbackMaster(thisGlyph):
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		fallbackLayer = thisGlyph.layers[0]
		fallbackLayer.shapes = None
		for thatLayer in thisGlyph.layers[1:]:
			if thatLayer.name and thatLayer.name.startswith("Color"):
				if thatLayer.shapes:
					for thatShape in thatLayer.shapes:
						fallbackLayer.shapes.append( thatShape.copy() )
	else:
		# GLYPHS 2
		fallbackLayer = thisGlyph.layers[0]
		fallbackLayer.paths = None
		for thatLayer in thisGlyph.layers[1:]:
			if thatLayer.name and thatLayer.name.startswith("Color"):
				for thatPath in thatLayer.paths:
					fallbackLayer.paths.append( thatPath.copy() )


def enableOnlyColorLayers(thisGlyph):
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		for thisLayer in thisGlyph.layers:
			if thisLayer.isColorPaletteLayer():
				thisLayer.setVisible_(1)
			else:
				thisLayer.setVisible_(0)
	else:
		# GLYPHS 2
		for thisLayer in thisGlyph.layers:
			if thisLayer.name and thisLayer.name.startswith("Color"):
				thisLayer.setVisible_(1)
			else:
				thisLayer.setVisible_(0)

	
def process( thisGlyph ):
	for i in range(len(namesOfMasters))[::-1]:
		colorLayerName = "Color %i" % i
		originalLayerName = namesOfMasters[i]
		originalLayer = thisGlyph.layerForName_(originalLayerName)
		thisGlyph.layers[colorLayerName] = originalLayer.copy()
		thisGlyph.layers[colorLayerName].setAssociatedMasterId_(fallbackMasterID)
		thisGlyph.layers[colorLayerName].setName_(colorLayerName)
		if Glyphs.versionNumber >= 3:
			# GLYPHS 3
			thisGlyph.layers[colorLayerName].setColorPaletteLayer_(1)
			thisGlyph.layers[colorLayerName].setAttribute_forKey_(i, "colorPalette")
	
# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print("Converting %s to CPAL/COLR:" % thisFont.familyName)

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	createCPALfromMasterColors( thisFont, thisFont.masters, 0 )
	print()

	for thisGlyph in thisFont.glyphs:
		print("Creating 'Color' layers for: %s" % thisGlyph.name)
		thisGlyph.beginUndo() # begin undo grouping
		process( thisGlyph )
		duplicatePathsIntoFallbackMaster( thisGlyph )
		thisGlyph.endUndo()   # end undo grouping

	print()
	keepOnlyFirstMaster( thisFont )
	print()

	for thisGlyph in thisFont.glyphs:
		print("Cleaning up layer debris in: %s" % thisGlyph.name)
		thisGlyph.beginUndo() # begin undo grouping
		cleanUpNamelessLayers(thisGlyph)
		enableOnlyColorLayers(thisGlyph)
		thisGlyph.endUndo()   # end undo grouping
	
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
	
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View

# take time:
end = timer()
seconds = end - start
if seconds > 60.0:
	timereport = "%i:%02i minutes" % ( seconds//60, seconds%60 )
elif seconds < 1.0:
	timereport = "%.2f seconds" % seconds
elif seconds < 20.0:
	timereport = "%.1f seconds" % seconds
else:
	timereport = "%i seconds" % seconds


print()
print("Done. Time elapsed: %s." % timereport)
