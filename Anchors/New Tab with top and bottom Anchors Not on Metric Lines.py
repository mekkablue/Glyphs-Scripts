#MenuTitle: New Tab with top and bottom Anchors Not on Metric Lines
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Reports the y positions of top and bottom anchors to the Macro Window if the anchors are not on a metric line (baseline, x-height, etc.).
"""

thisFont = Glyphs.font

print("Looking for misplaced top/bottom anchors")
print("Font: %s" % thisFont.familyName)
if thisFont.filepath:
	print("📄 %s" % thisFont.filepath)
else:
	print("⚠️ File not saved yet.")
print()
	
Glyphs.clearLog()
anchorCount = 0

def isAnchorOffMetrics( thisLayer, thisAnchorName ):
	try:
		myMaster = thisLayer.associatedFontMaster()
		myY = thisLayer.anchors[ thisAnchorName ].y
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

anchorsToLookFor = ("top","bottom")

# prepare dictionary:
collectedLayers = {}
for thisAnchorName in anchorsToLookFor:
	collectedLayers[thisAnchorName] = []
	collectedLayers["_%s"%thisAnchorName] = []

# step through all glyphs
for thisGlyph in thisFont.glyphs:
	for thisAnchorName in anchorsToLookFor:
		for thisLayer in thisGlyph.layers:
			if thisLayer.isSpecialLayer or thisLayer.isMasterLayer:

				# check for _top instead of top if it exists:
				connectingAnchorName = "_%s"%thisAnchorName
				if thisLayer.anchors[connectingAnchorName]:
					thisAnchorName = connectingAnchorName
			
				# check for position:
				if isAnchorOffMetrics( thisLayer, thisAnchorName ):
					collectedLayers[thisAnchorName].append(thisLayer)
					anchorCount += 1

tab = None
for thisAnchorName in sorted(collectedLayers.keys()):
	layers = collectedLayers[thisAnchorName]
	if layers:
		if not tab:
			# Open new Edit tab if it is not open yet:
			tab = thisFont.newTab()
			tab.scale=0.04
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
	# Floating notification:
	Glyphs.showNotification( 
		u"%s: %i misplaced anchors" % (thisFont.familyName, anchorCount),
		u"Opened new tab with %i anchors not on metric lines. Details in Macro Window." % anchorCount,
		)
	
else:
	reporttext = "Could not find %s anchors off metric lines on master layers." % " or ".join(anchorsToLookFor)
	print(reporttext) # just in case opening a tab fails
	Message(title="All is good", message=reporttext, OKButton="Cool")
	
