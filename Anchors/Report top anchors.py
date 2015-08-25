#MenuTitle: Report top Positions Not on Metric Lines
# -*- coding: utf-8 -*-
__doc__="""
Reports the y positions of the top anchors of selected glyphs to the Macro Window if the anchors are not on a metric line (baseline, x height, etc.).
"""

import GlyphsApp

myAnchor = "top"
Font = Glyphs.font
selectedLayers = Font.selectedLayers

Glyphs.clearLog()
Glyphs.showMacroWindow()

def process( thisLayer ):
	try:
		myMaster = thisLayer.associatedFontMaster()
		myY = thisLayer.anchors[ myAnchor ].y
		if myY in [0.0, myMaster.xHeight, myMaster.descender, myMaster.ascender, myMaster.capHeight]:
			return False
		else:
			print thisLayer.parent.name, "--->", myY
			return True
	except Exception, e:
		return False

listOfGlyphNames = []
for thisLayer in selectedLayers:
	if process( thisLayer ):
		listOfGlyphNames.append(thisLayer.parent.name)

if listOfGlyphNames:
	print "\nGlyphs with off top anchors in this master:\n/%s" % "/".join(listOfGlyphNames)
else:
	print "\nAll anchors on metric lines."
