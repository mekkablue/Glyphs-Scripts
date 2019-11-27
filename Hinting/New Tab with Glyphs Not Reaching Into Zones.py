#MenuTitle: New Tab with Glyphs Not Reaching Into Zones
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Opens a new tab with all glyphs that do NOT reach into any top or bottom alignment zone. Only counts glyphs that contain paths in the current master. Ignores empty glyphs and compounds.
"""

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
bottomZones = sorted( [z for z in thisFontMaster.alignmentZones if z.size < 0.0], key = lambda thisZone: -thisZone.position )
topZones    = sorted( [z for z in thisFontMaster.alignmentZones if z.size > 0.0], key = lambda thisZone: thisZone.position )
exportingGlyphs = [g for g in thisFont.glyphs if g.export and len(g.layers[thisFontMaster.id].paths)>0 ]
tabText = "Master: %s" % thisFontMaster.name

for zoneGroupInfo in ( (bottomZones,False), (topZones, True) ):
	zones = zoneGroupInfo[0]
	isTopZone = zoneGroupInfo[1]
	
	zoneType = "bottom"
	if isTopZone:
		zoneType = "top"

	tabText += ("\n\nNo %s zone:\n" % zoneType)

	for thisGlyph in exportingGlyphs:
		thisLayer = thisGlyph.layers[thisFontMaster.id]

		# exclude diacritic compounds:
		isDiacriticCompound = (
			isTopZone and 
			thisGlyph.category == "Letter" and 
			len(thisLayer.paths)==0 and 
			len(thisLayer.components)>0 and 
			thisLayer.components[0].component.category=="Letter"
		)
			
		if thisLayer.bounds.size.height and not isDiacriticCompound:
			doesNotReachZone = True
			if isTopZone:
				topEdge = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
				for thisZone in zones:
					if topEdge >= thisZone.position and topEdge <= (thisZone.position+thisZone.size):
						doesNotReachZone = False
			else:
				bottomEdge = thisLayer.bounds.origin.y
				for thisZone in zones:
					if bottomEdge <= thisZone.position and bottomEdge >= (thisZone.position+thisZone.size):
						doesNotReachZone = False
			if doesNotReachZone:
				tabText += "/%s" % thisGlyph.name
					
# opens new Edit tab:
thisFont.newTab( tabText )
