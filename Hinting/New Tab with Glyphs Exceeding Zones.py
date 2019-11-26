#MenuTitle: New Tab with Glyphs Exceeding Zones
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Opens a new tab with all glyphs where the extremums do not lie within zones.
"""

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
thisFontMasterID = thisFontMaster.id
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def zoneList( master ):
	zoneList = []
	for z in master.alignmentZones:
		zoneOrigin, zoneSize = int(z.position), int(z.size)
		zoneList.append( ( zoneOrigin, zoneOrigin+zoneSize ) )
	return zoneList

def isInZones( thisLayer, zones ):
	# ignore empty glyphs:
	if len(thisLayer.paths) == 0 and len(thisLayer.components) == 0:
		return True
	
	bottom = thisLayer.bounds.origin.y
	top = bottom + thisLayer.bounds.size.height
	
	isBottomInZone = False
	isTopInZone = False
	
	for thisZone in zones:
		zoneOrigin, zoneEnd = thisZone[0], thisZone[1]
		
		if zoneOrigin < zoneEnd:
			# top zone
			if zoneOrigin <= top <= zoneEnd:
				isTopInZone = True
				
		elif zoneOrigin > zoneEnd:
			# bottom zone
			if zoneOrigin >= bottom >= zoneEnd:
				isBottomInZone = True
	
	if isBottomInZone and isTopInZone:
		return True
	else:
		return False

tabString = ""
masterZones = zoneList( thisFontMaster )
for thisGlyph in thisFont.glyphs:
	thisLayer = thisGlyph.layers[thisFontMasterID]
	if not isInZones( thisLayer, masterZones ):
		tabString += "/%s" % thisGlyph.name

# opens new Edit tab:
from PyObjCTools.AppHelper import callAfter
callAfter( Glyphs.currentDocument.windowController().addTabWithString_, tabString )
