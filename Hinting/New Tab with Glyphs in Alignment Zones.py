#MenuTitle: New Tab with Glyphs in Alignment Zones
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from collections import OrderedDict
__doc__ = """
Opens a new tab and lists all glyphs that reach into alignment zones.
"""

def glyphs2Solution(thisFont):
	thisFontMaster = thisFont.selectedFontMaster # active master
	bottomZones = sorted([z for z in thisFontMaster.alignmentZones if z.size < 0.0], key=lambda thisZone: -thisZone.position)
	topZones = sorted([z for z in thisFontMaster.alignmentZones if z.size > 0.0], key=lambda thisZone: thisZone.position)
	exportingGlyphs = [g for g in thisFont.glyphs if g.export]
	tabText = "Master: %s" % thisFontMaster.name

	for zoneGroupInfo in ((bottomZones, False), (topZones, True)):
		zones = zoneGroupInfo[0]
		isTopZone = zoneGroupInfo[1]

		zoneType = "bottom"
		if isTopZone:
			zoneType = "top"

		for thisZone in zones:
			tabText += ("\n\n%s %i+%i:\n" % (zoneType, thisZone.position, thisZone.size)).replace("+-", "/minus ").replace("-", "/minus ").replace("bottom 0", "baseline 0")

			for thisGlyph in exportingGlyphs:
				thisLayer = thisGlyph.layers[thisFontMaster.id]
				if thisLayer.bounds.size.height:
					if isTopZone:
						topEdge = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
						if topEdge >= thisZone.position and topEdge <= (thisZone.position + thisZone.size):
							tabText += "/%s" % thisGlyph.name
					else:
						bottomEdge = thisLayer.bounds.origin.y
						if bottomEdge <= thisZone.position and bottomEdge >= (thisZone.position + thisZone.size):
							tabText += "/%s" % thisGlyph.name
	return tabText

def glyphs3Solution(thisFont):
	thisFontMaster = thisFont.selectedFontMaster # active master
	exportingGlyphs = [g for g in thisFont.glyphs if g.export]
	tabText = "Master: %s" % thisFontMaster.name

	# collecting data into OrderedDict (so the order of the elements won't be messed)
	zoneData = OrderedDict()

	for thisGlyph in exportingGlyphs:
		thisLayer = thisGlyph.layers[thisFontMaster.id]
		bottomZones = sorted([z for z in thisLayer.metrics if z.size < 0.0], key=lambda thisZone: -thisZone.position)
		topZones = sorted([z for z in thisLayer.metrics if z.size > 0.0], key=lambda thisZone: thisZone.position)

		for zones, isTopZone in ((bottomZones, False), (topZones, True)):
			for thisZone in zones:
				zoneType = "bottom"
				if isTopZone:
					zoneType = "top"
				zoneDescription = ("\n\n%s %i+%i:\n" % (zoneType, thisZone.position, thisZone.size)).replace("+-",
																												"/minus ").replace("-",
																																	"/minus ").replace("bottom 0", "baseline 0")
				if not zoneDescription in zoneData.keys():
					zoneData[zoneDescription] = []

				if thisLayer.bounds.size.height:
					if isTopZone:
						topEdge = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
						if topEdge >= thisZone.position and topEdge <= (thisZone.position + thisZone.size):
							zoneData[zoneDescription].append("/%s" % thisGlyph.name)
					else:
						bottomEdge = thisLayer.bounds.origin.y
						if bottomEdge <= thisZone.position and bottomEdge >= (thisZone.position + thisZone.size):
							zoneData[zoneDescription].append("/%s" % thisGlyph.name)

	# merging collected data into string
	for key, value in zoneData.items():
		tabText += key
		tabText += " ".join(value)

	return tabText

thisFont = Glyphs.font # frontmost font
if Glyphs.versionNumber >= 3:
	# Glyphs 3 code
	tabText = glyphs3Solution(thisFont)
else:
	# Glyphs 2 code
	tabText = glyphs2Solution(thisFont)

thisFont.newTab(tabText)
