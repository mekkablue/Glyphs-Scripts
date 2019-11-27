#MenuTitle: New Tab with Unusual Compounds
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Open a new tab containing all compound glyphs that have an unusual component order or an unorthodox component structure. Useful for finding wrong component orders.
"""

thisFont = Glyphs.font # frontmost font
fontMasterIDs = [m.id for m in thisFont.masters]
fontMasterReports = [ "%s:\n" % m.name for m in thisFont.masters ]

def orthodoxComponentsForGlyph( thisGlyph ):
	glyphInfo = thisGlyph.glyphInfo
	if glyphInfo:
		componentInfo = glyphInfo.components
		if componentInfo:
			glyphNameTuple = tuple(c.name for c in componentInfo)
			return glyphNameTuple
	return None

def nameStrippedOfSuffixes( glyphName ):
	return glyphName[:glyphName.find(".")%(len(glyphName)+1)]

def layerAdheresToStructure( thisLayer, glyphNameTuple ):
	layerComponents = thisLayer.components
	numOfLayerComponents = len(layerComponents)
	if numOfLayerComponents != len(glyphNameTuple):
		return False
		
	for i in range(numOfLayerComponents):
		thisComponentName = thisLayer.components[i].componentName
		orthodoxComponentName = glyphNameTuple[i]
		if thisComponentName != orthodoxComponentName:
			componentBaseName = nameStrippedOfSuffixes(thisComponentName)
			orthodoxBaseName = nameStrippedOfSuffixes(orthodoxComponentName)
			if componentBaseName != orthodoxBaseName:
				return False
	
	return True

for thisGlyph in thisFont.glyphs:
	componentStructure = orthodoxComponentsForGlyph( thisGlyph )
	if componentStructure:
		for i in range(len(fontMasterIDs)):
			masterID = fontMasterIDs[i]
			thisLayer = thisGlyph.layers[masterID]
			if not layerAdheresToStructure( thisLayer, componentStructure ):
				fontMasterReports[i] += "/%s" % thisGlyph.name

tabText = "\n\n".join( fontMasterReports )
thisFont.newTab( tabText )
