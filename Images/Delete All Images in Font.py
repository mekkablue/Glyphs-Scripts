from __future__ import print_function
#MenuTitle: Remove All Images from Font
# -*- coding: utf-8 -*-
__doc__="""
Deletes all placed images from the frontmost font.
"""

thisFont = Glyphs.font

def process( thisGlyph ):
	deleteCount = 0
	for thisLayer in thisGlyph.layers:
		if thisLayer.backgroundImage:
			thisLayer.setBackgroundImage_(None)
			deleteCount += 1
	return deleteCount

thisFont.disableUpdateInterface()

print("Removing images in %s glyphs ..." % len( thisFont.glyphs ))

totalCount = 0

for thisGlyph in thisFont.glyphs:
	thisGlyph.beginUndo()
	numberOfDeletedImages = process( thisGlyph )
	if numberOfDeletedImages:
		plural = 0
		if numberOfDeletedImages > 1:
			plural = 1
		print("   Deleted %i image%s in %s." % ( numberOfDeletedImages, "s"*plural, thisGlyph.name ))
	totalCount += numberOfDeletedImages
	thisGlyph.endUndo()

thisFont.enableUpdateInterface()

print("Removed links to %i images in total." % totalCount)
