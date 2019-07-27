#MenuTitle: Set blueScale
# -*- coding: utf-8 -*-
__doc__="""
Sets maximum blueScale value (determining max size for overshoot suppression) possible in Font Info > Font. Outputs other options in Macro Window.
"""

def maxZoneInFont( thisFont ):
	"""
	Returns the size of the largest zone in the font.
	"""
	maxSize = 0.0
	for thisMaster in thisFont.masters:
		for thisZone in thisMaster.alignmentZones:
			if maxSize < abs(thisZone.size):
				maxSize = abs(thisZone.size)
	return maxSize

def maxPPMforOvershootSuppressionInFont( thisFont ):
	"""
	Returns max PPM at which overshoot can be suppressed for this font.
	"""
	maxZone = maxZoneInFont(thisFont)
	if maxZone < 1:
		maxZone = 16 # fallback value (Glyphs default)
	maxPPM = int(2.04 + 1000.0 / maxZone)
	return maxPPM

def blueScaleForPPMsize( ppmSize ):
	"""
	Returns blueZone value for given PPM size,
	up to which overshoots will be suppressed.
	"""
	return (float(ppmSize) - 2.04) / 1000.0

def maxBlueScaleForFont( thisFont ):
	"""
	Returns the maximum blueZone possible for this font.
	"""
	pixelsize = maxPPMforOvershootSuppressionInFont(thisFont)
	blueScale = blueScaleForPPMsize(pixelsize)
	return blueScale

def maxZoneForBlueScale( blueScale ):
	ppm = int(1000.0 * blueScale + 2.04)
	zoneSize = int(1000.0 // (ppm-2.04))
	return zoneSize

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

thisFont = Glyphs.font # frontmost font
if thisFont.customParameters["blueScale"]:
	print "Old blueScale value: %f" % float(thisFont.customParameters["blueScale"])
	print "(Stored in font parameter 'OLD blueScale'.)"
	print
	thisFont.customParameters["OLD blueScale"] = thisFont.customParameters["blueScale"]

minSize = 16
maxSize = maxPPMforOvershootSuppressionInFont( thisFont )
maxBlueScale = maxBlueScaleForFont( thisFont )
thisFont.customParameters["blueScale"] = maxBlueScale

print "blueScale set to maximum: OK"
print
print "Maximum blueScale for %s:\n%f (PPM: %i px)" % (
	thisFont.familyName,
	maxBlueScale,
	maxSize,
)
print 

if maxSize > minSize:
	print "Possible font size limits of overshoot suppression:"
	print 
	print "    PPM    96dpi  144dpi  300dpi  600dpi  blueScale  max zone"
	print "------- -------- ------- ------- ------- ---------- ---------"
	for size in range(minSize,maxSize+1):
	#for size in range(30,71,2):
		print "%4i px  % 4.0f pt % 4.0f pt % 4.0f pt % 4.0f pt    %.5f     %3i u" % (
			size,
			(size/96.0)*72.0,
			(size/144.0)*72.0,
			(size/300.0)*72.0,
			(size/600.0)*72.0,
			blueScaleForPPMsize(size),
			maxZoneForBlueScale(blueScaleForPPMsize(size)),
		)