#MenuTitle: Capitalize Glyph Names
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Turns aacute.sc into Aacute.sc, etc.
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # user selection

# function for returning the first part of the glyph name:
def firstPartOfGlyphName(name):
	"""Returns the glyph name until the first dot."""
	dotPosition = name.find(".")
	if dotPosition != -1: # found a dot
		return name[:dotPosition]
	else: # no dot found
		return name
		
# function for returning the cap'd glyph name:
def capitalizeGlyphName(name):
	# capitalize the first name part (until first dot)
	firstPart = firstPartOfGlyphName(name).capitalize()
	
	# check for AE, OE (E must be cap too):
	firstPart = firstPart.replace("Ae","AE").replace("Oe","OE")
	
	# stitch whole name together again:
	# firstPart plus the rest of the name
	name = firstPart + name[len(firstPart):]
	
	return name

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

# iterate through selection:
for thisLayer in selectedLayers:
	# get the glyph:
	thisGlyph = thisLayer.parent
	thisGlyph.name = capitalizeGlyphName( thisGlyph.name )
	
thisFont.enableUpdateInterface() # re-enables UI updates in Font View
