#MenuTitle: New Tab with top and bottom Anchors Not on Metric Lines
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Reports the y positions of top and bottom anchors to the Macro Window if the anchors are not on a metric line (baseline, x-height, etc.).
"""

thisFont = Glyphs.font

Glyphs.clearLog()
# Glyphs.showMacroWindow()

def isAnchorOnMetricLine( thisLayer, thisAnchorName ):
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
			print("%s: %s @ y=%s" % (thisLayer.parent.name, thisAnchorName, myY))
			return True
	except Exception as e:
		return False

anchorsToLookFor = ("top","bottom")
collectedGlyphNames = {}
for thisAnchor in anchorsToLookFor:
	collectedGlyphNames[thisAnchor] = []

for thisGlyph in thisFont.glyphs:
	for thisAnchor in anchorsToLookFor:
		relevantLayers = [l for l in thisGlyph.layers if l and (l.isSpecialLayer or l.isMasterLayer)]
		for thisVeryLayer in relevantLayers:
			if isAnchorOnMetricLine( thisVeryLayer, thisAnchor ):
				collectedGlyphNames[thisAnchor].append(thisGlyph.name)

offAnchorsFound = False
reporttext = ""
for thisAnchor in anchorsToLookFor:
	glyphNames = collectedGlyphNames[thisAnchor]
	# opens new Edit tab:
	if glyphNames:
		offAnchorsFound = True
		reporttext += "Anchor '%s' off metrics:\n/%s\n\n" % (thisAnchor, "/".join(set(glyphNames)))
thisFont.newTab( reporttext.strip() )

if not offAnchorsFound:
	reporttext = "Could not find %s anchors off metric lines on master layers." % " or ".join(anchorsToLookFor)
	print(reporttext) # just in case opening a tab fails
	Message(title="All is good", message=reporttext, OKButton="Cool")
	
