# MenuTitle: New Tab with top and bottom Anchors Not on Metric Lines
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Reports the y positions of top and bottom anchors to the Macro Window if the anchors are not on a metric line (baseline, x-height, etc.). Hold down OPTION and SHIFT to run for all open fonts.
"""

from AppKit import NSEvent, NSEventModifierFlagOption, NSEventModifierFlagShift
from GlyphsApp import Glyphs, GSControlLayer


def isAnchorOffMetrics(thisLayer, thisAnchorName):
	try:
		myAnchor = thisLayer.anchors[thisAnchorName]
		if not myAnchor:
			return False
		myY = myAnchor.y
		masterMetrics = [m.position for m in thisLayer.metrics if hasattr(m, "position")]
		if myY in masterMetrics:
			return False
		else:
			print("%s in %s, layer ‘%s’: %i" % (
				thisAnchorName,
				thisLayer.parent.name,
				thisLayer.name,
				myY,
			))
			return True
	except Exception as e:  # noqa: F841
		return False


keysPressed = NSEvent.modifierFlags()
optionKeyPressed = keysPressed & NSEventModifierFlagOption == NSEventModifierFlagOption
shiftKeyPressed = keysPressed & NSEventModifierFlagShift == NSEventModifierFlagShift

# brings macro window to front and clears its log:
Glyphs.clearLog()
anchorsToLookFor = ("top", "bottom")

if optionKeyPressed and shiftKeyPressed:
	fonts = Glyphs.fonts
else:
	fonts = [Glyphs.font]

for thisFont in fonts:
	thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
	try:
		print("Looking for misplaced top/bottom anchors")
		print(f"Font: {thisFont.familyName}")
		if thisFont.filepath:
			print(f"📄 {thisFont.filepath}")
		else:
			print("⚠️ File not saved yet.")
		print()

		anchorCount = 0

		# prepare dictionary:
		collectedLayers = {}
		for thisAnchorName in anchorsToLookFor:
			collectedLayers[thisAnchorName] = []
			collectedLayers["_%s" % thisAnchorName] = []

		# step through all glyphs
		for thisGlyph in thisFont.glyphs:
			for thisAnchorName in anchorsToLookFor:
				for thisLayer in thisGlyph.layers:
					if thisLayer.isSpecialLayer or thisLayer.isMasterLayer:

						# check for _top instead of top if it exists:
						connectingAnchorName = f"_{thisAnchorName}"
						if thisLayer.anchors[connectingAnchorName]:
							thisAnchorName = connectingAnchorName

						# check for position:
						if isAnchorOffMetrics(thisLayer, thisAnchorName):
							collectedLayers[thisAnchorName].append(thisLayer)
							anchorCount += 1

		tabLayers = []
		for thisAnchorName in sorted(collectedLayers.keys()):
			layers = collectedLayers[thisAnchorName]
			if layers:
				if tabLayers:
					# Otherwise add two newlines:
					tabLayers.append(GSControlLayer.newline())
					tabLayers.append(GSControlLayer.newline())

				# Add layers for anchor name:
				for char in thisAnchorName:
					charGlyph = thisFont.glyphs[char]
					if charGlyph:
						charLayer = charGlyph.layers[thisFont.selectedFontMaster.id]
						tabLayers.append(charLayer)
				tabLayers.append(GSControlLayer.newline())

				# add found anchors:
				for layerWithMisplacedAnchor in collectedLayers[thisAnchorName]:
					tabLayers.append(layerWithMisplacedAnchor)

		# Open new Edit tab if it is not open yet:
		if tabLayers:
			tab = thisFont.newTab()
			tab.scale = 0.04
			tab.initialZoom()
			tab.layers = tabLayers
			print(f"⚠️ {anchorCount} anchors not on metric lines.\n")
		else:
			print(f"🎉 Could not find {' or '.join(anchorsToLookFor)} anchors off metric lines on master layers.\n")

	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ Error in script: \n")
		import traceback
		print(traceback.format_exc())
		print()
		raise e
	finally:
		thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

print("✅ Done.")
