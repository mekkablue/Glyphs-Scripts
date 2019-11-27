#MenuTitle: New Tab with Glyphs in Alignment Zones
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new tab and lists all glyphs that reach into alignment zones.
"""

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
bottomZones = sorted( [z for z in thisFontMaster.alignmentZones if z.size < 0.0], key = lambda thisZone: -thisZone.position )
topZones    = sorted( [z for z in thisFontMaster.alignmentZones if z.size > 0.0], key = lambda thisZone: thisZone.position )
exportingGlyphs = [g for g in thisFont.glyphs if g.export]
tabText = "Master: %s" % thisFontMaster.name

for zoneGroupInfo in ( (bottomZones,False), (topZones, True) ):
	zones = zoneGroupInfo[0]
	isTopZone = zoneGroupInfo[1]
	
	zoneType = "bottom"
	if isTopZone:
		zoneType = "top"

	for thisZone in zones:
		tabText += ("\n\n%s %i+%i:\n" % (zoneType, thisZone.position, thisZone.size)).replace("+-","/minus ").replace("-","/minus ").replace("bottom 0","baseline 0")
	
		for thisGlyph in exportingGlyphs:
			thisLayer = thisGlyph.layers[thisFontMaster.id]
			if thisLayer.bounds.size.height:
				if isTopZone:
					topEdge = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
					if topEdge >= thisZone.position and topEdge <= (thisZone.position+thisZone.size):
						tabText += "/%s" % thisGlyph.name
				else:
					bottomEdge = thisLayer.bounds.origin.y
					if bottomEdge <= thisZone.position and bottomEdge >= (thisZone.position+thisZone.size):
						tabText += "/%s" % thisGlyph.name

# opens new Edit tab:
thisFont.newTab( tabText )
