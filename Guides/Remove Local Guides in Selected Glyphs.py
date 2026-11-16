# MenuTitle: Remove Local Guides in Selected Glyphs
__doc__ = """
Delete all local (blue) guides in selected glyphs.
"""

from mekkablue import clearGuides
from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font
if thisFont is None:
	print("⚠️ No font open.")
else:
	print("Deleting guides in:")
	for thisLayer in thisFont.selectedLayers:
		thisGlyph = thisLayer.parent
		# thisGlyph.beginUndo()  # undo grouping causes crashes
		clearGuides(thisLayer)
		# thisGlyph.endUndo()  # undo grouping causes crashes
		print("  %s" % thisGlyph.name)
