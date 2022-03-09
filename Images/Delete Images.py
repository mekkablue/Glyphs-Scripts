#MenuTitle: Remove Images
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
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
try:
	print("Removing images in %s selected glyphs ..." % len( selectedLayers ))

	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		# thisGlyph.beginUndo() # undo grouping causes crashes
		numberOfDeletedImages = process( thisGlyph )
		if numberOfDeletedImages:
			plural = 0
			if numberOfDeletedImages > 1:
				plural = 1
			print("  Deleted %i image%s in %s." % ( numberOfDeletedImages, "s"*plural, thisGlyph.name ))
		# thisGlyph.endUndo() # undo grouping causes crashes
		
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
	
finally:
	Font.enableUpdateInterface()
