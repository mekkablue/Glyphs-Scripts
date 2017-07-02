#MenuTitle: Save Selected Glyphs as PNG
# -*- coding: utf-8 -*-
__doc__="""
Saves selected glyphs as PNGs. Uses ascender and descender for top and bottom edges of the images.
"""

def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX,shiftY)
	return myTransform

def saveLayerAsPNG( thisLayer, baseurl ):
	# create a bitmap 1u = 1px, width of glyph, from descender to ascender
	thisMaster = thisLayer.associatedFontMaster()
	offscreenRect = NSMakeRect(
		0.0, 0.0, # x y
		thisLayer.width, # width
		thisMaster.ascender-thisMaster.descender # height
	)
	bitmap = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bitmapFormat_bytesPerRow_bitsPerPixel_(
		None, #BitmapDataPlanes
		int(offscreenRect.size.width), #pixelsWide
		int(offscreenRect.size.height), #pixelsHigh
		8, #bitsPerSample
		4, #samplesPerPixel
		True, #hasAlpha
		False, #isPlanar
		NSCalibratedRGBColorSpace, #colorSpaceName
		0, #bitmapFormat
		int(4 * offscreenRect.size.width), #bytesPerRow
		32 #bitsPerPixel
	)

	# save the current graphics context and lock focus on the bitmap
	originalContext = NSGraphicsContext.currentContext()
	NSGraphicsContext.setCurrentContext_(NSGraphicsContext.graphicsContextWithBitmapImageRep_(bitmap))
	NSGraphicsContext.saveGraphicsState()

	# draw the image
	NSBezierPath.bezierPathWithRect_(offscreenRect).addClip() # set the rectangle as a clipping path
	baselineShift = -thisMaster.descender
	shiftTransform = transform(shiftY=baselineShift) # shift from bottom edge (y=0 in PNG) to baseline (y=0 in glyph)
	image = thisLayer.bezierPath.copy() # otherwise your glyphs start floating in mid air :)
	image.transformUsingAffineTransform_(shiftTransform)
	image.fill()

	# restore the original graphics context
	NSGraphicsContext.restoreGraphicsState()
	NSGraphicsContext.setCurrentContext_(originalContext)

	# file name (prefix uppercase letters with an underscore to avoid overwrite)
	thisGlyph = thisLayer.parent
	pngName = thisGlyph.name
	if thisGlyph.subCategory == "Uppercase":
		pngName = "_%s" % pngName
		
	# construct filepath URL and write the file
	fullURL = "%s/%s.png" % (baseurl, pngName)
	url = NSURL.fileURLWithPath_( fullURL )
	pngData = bitmap.representationUsingType_properties_( NSPNGFileType, None ) # get PNG data from image rep
	pngData.writeToURL_options_error_( url, NSDataWritingAtomic, None ) # write
	
	return fullURL # for status message in Macro Window

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
saveDir = GetFolder(message="Select a folder for saving the images:", allowsMultipleSelection = False)
# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print "Saving PNG files:"
for thisLayer in selectedLayers:
	print saveLayerAsPNG( thisLayer, saveDir )
