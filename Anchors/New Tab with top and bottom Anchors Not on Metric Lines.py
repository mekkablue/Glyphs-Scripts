#MenuTitle: New Tab with top and bottom Anchors Not on Metric Lines
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
For all open fonts, reports the y positions of top and bottom anchors to the Macro Window if the anchors are not on a metric line (baseline, x-height, etc.).
"""

def isAnchorOffMetrics(thisLayer, thisAnchorName):
	try:
		myMaster = thisLayer.associatedFontMaster()
		myY = thisLayer.anchors[thisAnchorName].y
		masterMetrics = [0.0, myMaster.xHeight, myMaster.descender, myMaster.ascender, myMaster.capHeight]
		scHeight = myMaster.customParameters["smallCapHeight"]
		if scHeight:
			masterMetrics.append(float(scHeight))
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
	except Exception as e:
		return False


# brings macro window to front and clears its log:
Glyphs.clearLog()
anchorsToLookFor = ("top", "bottom")

for thisFont in Glyphs.fonts:
	print("Looking for misplaced top/bottom anchors")
	print(f"Font: {thisFont.familyName}")
	if thisFont.filepath:
		print("📄 {thisFont.filepath}")
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

	tab = None
	for thisAnchorName in sorted(collectedLayers.keys()):
		layers = collectedLayers[thisAnchorName]
		if layers:
			if not tab:
				# Open new Edit tab if it is not open yet:
				tab = thisFont.newTab()
				tab.scale = 0.04
				tab.initialZoom()
			else:
				# Otherwise add two newlines:
				tab.layers.append(GSControlLayer.newline())
				tab.layers.append(GSControlLayer.newline())

			# Add layers for anchor name:
			for char in thisAnchorName:
				charGlyph = thisFont.glyphs[char]
				if charGlyph:
					charLayer = charGlyph.layers[thisFont.selectedFontMaster.id]
					tab.layers.append(charLayer)
			tab.layers.append(GSControlLayer.newline())

			# add found anchors:
			for layerWithMisplacedAnchor in collectedLayers[thisAnchorName]:
				tab.layers.append(layerWithMisplacedAnchor)

	if tab:
		print(f"{anchorCount} anchors not on metric lines.\n")
	else:
		print(f"Could not find {' or '.join(anchorsToLookFor)} anchors off metric lines on master layers.\n")

print("✅ Done.")