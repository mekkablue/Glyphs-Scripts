#MenuTitle: New Tab with Transformed Corner Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new Edit tab containing all glyphs with scaled corner components.
"""

def isLayerAffected( thisLayer ):
	thisLayer.selection = None
	for thisHint in thisLayer.hints:
		if thisHint.type == CORNER:
			if abs(thisHint.scale.x) != 1.0 or abs(thisHint.scale.y) != 1.0:
				thisHint.selected = True
				return True
	return False

Glyphs.clearLog() # clears log of Macro window
thisFont = Glyphs.font # frontmost font
affectedLayers = []
for thisGlyph in thisFont.glyphs: # loop through all glyphs
	#print "Analysing %s" % thisGlyph.name # report status in Macro window
	for thisLayer in thisGlyph.layers: # loop through all layers
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
		message = "Could not find any glyphs with scaled corner components.",
		OKButton = None
	)
	
