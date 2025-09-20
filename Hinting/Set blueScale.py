# MenuTitle: Set blueScale
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Sets maximum blueScale value (determining max size for overshoot suppression) possible in Font Info > Font. Outputs other options in Macro Window.
"""

from GlyphsApp import Glyphs


def maxZoneInFont(thisFont):
	"""
	Returns the size of the largest zone in the font.
	"""
	maxSize = 0.0
	for thisMaster in thisFont.masters:
		for thisZone in thisMaster.alignmentZones:
			if maxSize < abs(thisZone.size):
				maxSize = abs(thisZone.size)
	return maxSize


def maxPPMforOvershootSuppressionInFont(thisFont):
	"""
	Returns max PPM at which overshoot can be suppressed for this font.
	"""
	maxZone = maxZoneInFont(thisFont)
	if maxZone < 1:
		maxZone = 16  # fallback value (Glyphs default)
	maxPPM = int(2.04 + thisFont.upm / maxZone)
	return maxPPM


def blueScaleForPPMsize(ppmSize):
	"""
	Returns blueZone value for given PPM size,
	up to which overshoots will be suppressed.
	"""
	return (float(ppmSize) - 2.04) / 1000.0


def maxBlueScaleForFont(thisFont):
	"""
	Returns the maximum blueZone possible for this font.
	"""
	pixelsize = maxPPMforOvershootSuppressionInFont(thisFont)
	blueScale = blueScaleForPPMsize(pixelsize)
	return blueScale


def maxZoneForBlueScale(blueScale):
	ppm = int(1000.0 * blueScale + 2.04)
	zoneSize = int(1000.0 // (ppm - 2.04))
	return zoneSize


def setMacroDivider(position=0.1):
	from Foundation import NSHeight
	splitview = Glyphs.delegate().macroPanelController().consoleSplitView()
	height = NSHeight(splitview.frame())
	splitview.setPosition_ofDividerAtIndex_(height * position, 0)
	

# open Font Info at Font tab:
thisFont = Glyphs.font  # frontmost font
thisFont.parent.windowController().showFontInfoWindowWithTabSelected_(0) # font tab index

# prepare Macro window:
Glyphs.clearLog()
Glyphs.showMacroWindow()
setMacroDivider()

print(f"📄 {thisFont.familyName}")
# save old blueScale:
if thisFont.customParameters["blueScale"]:
	print(f"💾 Existing blueScale {float(thisFont.customParameters['blueScale'])} stored in font parameter ‘OLD blueScale’.")
	thisFont.customParameters["OLD blueScale"] = thisFont.customParameters["blueScale"]
	thisFont.customParameterForKey_("OLD blueScale").active = False

minSize = 16
maxSize = maxPPMforOvershootSuppressionInFont(thisFont)
maxBlueScale = maxBlueScaleForFont(thisFont)
thisFont.customParameters["blueScale"] = maxBlueScale
print(f"✅ Max blueScale: {maxBlueScale} (max {maxSize} PPM, largest zone {int(maxZoneInFont(thisFont))}u)\n")

if maxSize > minSize:
	print("Possible font size limits for overshoot suppression:")
	print()
	print("    PPM    96dpi  144dpi  300dpi  600dpi  blueScale  max zone")
	print("------- -------- ------- ------- ------- ---------- ---------")
	for size in range(minSize, maxSize + 1):
		# for size in range(30,71,2):
		print(
			"%4i px  % 4.0f pt % 4.0f pt % 4.0f pt % 4.0f pt    %.5f     %3i u" % (
				size,
				(size / 96.0) * 72.0,
				(size / 144.0) * 72.0,
				(size / 300.0) * 72.0,
				(size / 600.0) * 72.0,
				blueScaleForPPMsize(size),
				maxZoneForBlueScale(blueScaleForPPMsize(size)),
			)
		)
