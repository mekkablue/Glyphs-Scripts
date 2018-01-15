#MenuTitle: Remove Images
# -*- coding: utf-8 -*-
__doc__="""
Deletes placed images from selected glyphs on all layers.
"""


Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisGlyph ):
	deleteCount = 0
	for thisLayer in thisGlyph.layers:
		if thisLayer.backgroundImage:
			thisLayer.setBackgroundImage_(None)
			deleteCount += 1
	return deleteCount

Font.disableUpdateInterface()

print "Removing images in %s selected glyphs ..." % len( selectedLayers )

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	numberOfDeletedImages = process( thisGlyph )
	if numberOfDeletedImages:
		plural = 0
		if numberOfDeletedImages > 1:
			plural = 1
		print "  Deleted %i image%s in %s." % ( numberOfDeletedImages, "s"*plural, thisGlyph.name )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
