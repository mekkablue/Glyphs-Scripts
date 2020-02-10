#MenuTitle: New Tab with Locked Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new Edit tab containing all glyphs that have locked components in them.
"""

def isLayerAffected( l ):
	if l.isMasterLayer or l.isSpecialLayer:
		for c in l.components:
			if c.locked:
				return True
	return False

Glyphs.clearLog() # clears log of Macro window
thisFont = Glyphs.font # frontmost font
affectedLayers = []
for thisGlyph in thisFont.glyphs: # loop through all glyphs
	for thisLayer in thisGlyph.layers: # loop through all layers
		# print("Analysing %s" % thisGlyph.name) # report status in Macro window
		# collect affected layers:
		if isLayerAffected( thisLayer ): 
			affectedLayers.append(thisLayer)

# open a new tab with the affected layers:
if affectedLayers:
	newTab = thisFont.newTab()
	newTab.layers = affectedLayers
# otherwise send a message:
else:
	Message(
		title = "Nothing Found",
		message = "Could not find any glyphs with locked components.",
		OKButton = None
	)
	
