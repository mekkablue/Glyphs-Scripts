#MenuTitle: Report Black to White Ratios
# -*- coding: utf-8 -*-
__doc__="""
Calculates the area of each selected glyph, and outputs a CSV that contains the area, and its ratio to the bounding box and the glyph areas between baseline and x-height, baseline and cap height, baseline and ascender, and descender and ascender. Increase precision by changing the value for PRECISION in line 10 (script will slow down).
"""

import GlyphsApp, commands
from types import *

PRECISION = 2   # higher numbers = more precision, but slower
SEPARATOR = ";" # spec says this should be a comma, but only semicolon seems to work

GLYPHSAPPVERSION = NSBundle.bundleForClass_(GSMenu).infoDictionary().objectForKey_("CFBundleShortVersionString")
if GLYPHSAPPVERSION.startswith("1."):
	measurementTool = NSClassFromString("GlyphsToolMeasurement").alloc().init()
else:
	measurementTool = NSClassFromString("GSGuideLine")
	
def saveTextToFile( thisText, filePath ):
	try:
		thisFile = open( filePath, 'w' )
		thisFile.write( thisText )
		thisFile.close()
		return True
	except Exception as e:
		raise e

def saveFileDialog( message=None, ProposedFileName=None, filetypes=None ):
	if filetypes is None:
		filetypes = []
	Panel = NSSavePanel.savePanel().retain()
	if message is not None:
		Panel.setTitle_(message)
	Panel.setCanChooseFiles_(True)
	Panel.setCanChooseDirectories_(False)
	Panel.setAllowedFileTypes_(filetypes)
	if ProposedFileName is not None:
		Panel.setNameFieldStringValue_(ProposedFileName)
	pressedButton = Panel.runModalForTypes_(filetypes)
	if pressedButton == 1: # 1=OK, 0=Cancel
		return Panel.filename()
	return None
	
def sliceIntersections( thisLayer, startPoint, endPoint ):
	if GLYPHSAPPVERSION.startswith("2."):
		return thisLayer.calculateIntersectionsStartPoint_endPoint_( startPoint, endPoint )	
	else:
		return measurementTool.calculateIntersectionsForLayer_startPoint_endPoint_( thisLayer, startPoint, endPoint )	

def sizeOfSlice( thisLayer, y ):
	theseBounds = thisLayer.bounds
	startPointX = theseBounds.origin.x - 10
	endPointX = startPointX + theseBounds.size.width + 20
	startPoint = NSPoint( startPointX, y )
	endPoint   = NSPoint( endPointX, y )
	listOfIntersections = sliceIntersections( thisLayer, startPoint, endPoint )
	totalLength = 0.0
	if len(listOfIntersections) >= 4:
		listOfIntersections.pop(0)
		listOfIntersections.pop(-1)
		for thisPairIndex in range(len(listOfIntersections)/2):
			firstNode = listOfIntersections[ thisPairIndex*2 ].pointValue()
			secondNode = listOfIntersections[ thisPairIndex*2+1 ].pointValue()
			totalLength += abs( secondNode.x - firstNode.x )
	return totalLength

def areaForLayer( thisLayer, precision = 2, precisionOffset = 0.001 ):
	cleanLayer = thisLayer.copyDecomposedLayer()
	cleanLayer.removeOverlap()
	cleanLayer.addExtremePointsForce_(True)
	cleanBounds = cleanLayer.bounds
	lowerY = int( cleanBounds.origin.y )
	upperY = lowerY + int( cleanBounds.size.height + 2 )
	area = 0.0
	for thisY in range(lowerY,upperY):
		for thisRound in range(precision):
			measurementHeight = float(thisY) + ( float(thisRound) / float(precision) ) + precisionOffset
			area += sizeOfSlice( cleanLayer, measurementHeight )
	return area / precision

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
xHeight = thisFontMaster.xHeight
capHeight = thisFontMaster.capHeight
ascender = thisFontMaster.ascender
descenderToAscender = ascender - thisFontMaster.descender

columns = ( 
	"Glyph",
	"Black Area",
	"Bounding Box Ratio",
	"x-Height Ratio",
	"Cap Height Ratio",
	"Ascender Ratio",
	"Descender to Ascender Ratio" 
)
reportText = "%s\n" % SEPARATOR.join( columns )

# calculates areas and ratios for each selected layer:
for thisLayer in thisFont.selectedLayers:
	thisGlyphName = thisLayer.parent.name
	
	boundingBoxSize = thisLayer.bounds.size
	boundingBoxArea = boundingBoxSize.width * boundingBoxSize.height
	
	if not boundingBoxArea == 0.0: # avoid division by zero
		blackArea = areaForLayer( thisLayer, PRECISION )

		thisWidth = thisLayer.width
		xHeightArea = xHeight * thisWidth
		capHeightArea = capHeight * thisWidth
		ascenderArea = ascender * thisWidth
		descenderToAscenderArea = descenderToAscender * thisWidth
		
		reportValues = (
			thisGlyphName,                                            # Glyph Name
			"%.1f" % blackArea,                                       # Black Area
			"%.1f" % ( blackArea * 100.0 / boundingBoxArea ),         # Bounding Box Ratio
			"%.1f" % ( blackArea * 100.0 / xHeightArea ),             # x-Height Ratio
			"%.1f" % ( blackArea * 100.0 / capHeightArea ),           # Cap Height Ratio
			"%.1f" % ( blackArea * 100.0 / ascenderArea ),            # Ascender Ratio
			"%.1f" % ( blackArea * 100.0 / descenderToAscenderArea )  # Descender to Ascender Ratio
		)
	else:
		reportValues = (
			thisGlyphName, # Glyph Name
			"0.0",         # Black Area
			"0.0",         # Bounding Box Ratio
			"0.0",         # x-Height Ratio
			"0.0",         # Cap Height Ratio
			"0.0",         # Ascender Ratio
			"0.0"          # Descender to Ascender Ratio
		)
	
	reportText += "%s\n" % SEPARATOR.join( reportValues )

# ask user for file path
filePath = saveFileDialog(
	message = "Export Ratio CSV",
	ProposedFileName = "Ratios for %s %s" % ( thisFont.familyName, thisFontMaster.name ),
	filetypes = [ "csv", "txt" ] 
)

# save and confirm
saveTextToFile( reportText, filePath )
print "Saved Ratio CSV to: %s" % filePath
