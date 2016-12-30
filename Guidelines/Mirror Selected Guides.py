#MenuTitle: Mirror Selected Guides
# -*- coding: utf-8 -*-
__doc__="""
Mirrors all Selected Guides in the current glyph.
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def mirrorSelectedGuidesOnLayer( thisLayer ):
	for selectedItem in thisLayer.selection:
		if type(selectedItem) == GSGuideLine:
			selectedItem.angle = 180.0 - selectedItem.angle

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Mirroring selected guides on %s" % thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	mirrorSelectedGuidesOnLayer( thisLayer )
	thisGlyph.endUndo()   # end undo grouping
