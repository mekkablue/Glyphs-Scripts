# MenuTitle: Reset Image Transformations
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Resets all placed images to 100% scale and 0/0 position.
"""

from GlyphsApp import Glyphs

Font = Glyphs.font
selectedLayers = Font.selectedLayers


def process(thisLayer):
	thisImage = thisLayer.backgroundImage
	if thisImage:
		thisImage.transform = ((1.0, 0.0, 0.0, 1.0, 0.0, 0.0))


Font.disableUpdateInterface()
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		print("Resetting image in", thisGlyph.name)
		# thisGlyph.beginUndo()  # undo grouping causes crashes
		process(thisLayer)
		# thisGlyph.endUndo()  # undo grouping causes crashes
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	Font.enableUpdateInterface()  # re-enables UI updates in Font View
