# MenuTitle: Remove All Images from Font
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Deletes all placed images from the frontmost font.
"""

from GlyphsApp import Glyphs

thisFont = Glyphs.font


def process(thisGlyph):
	deleteCount = 0
	# thisGlyph.beginUndo()  # undo grouping causes crashes

	for thisLayer in thisGlyph.layers:
		try:
			if thisLayer.backgroundImage:
				thisLayer.setBackgroundImage_(None)
				deleteCount += 1
		except Exception as e:
			print("   ⚠️ %s, layer ‘%s’: %s\n" % (thisGlyph.name, thisLayer.name, e))

	# thisGlyph.endUndo()  # undo grouping causes crashes
	return deleteCount


thisFont.disableUpdateInterface()
try:
	print("Removing images in %s glyphs ..." % len(thisFont.glyphs))

	totalCount = 0

	for thisGlyph in thisFont.glyphs:
		numberOfDeletedImages = process(thisGlyph)
		plural = min(numberOfDeletedImages, 1)  # 0 or 1
		print("   Deleted %i image%s in %s." % (numberOfDeletedImages, "s" * plural, thisGlyph.name))
		totalCount += numberOfDeletedImages

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e

finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

print("Removed links to %i images in total." % totalCount)
