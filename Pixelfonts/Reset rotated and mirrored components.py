# MenuTitle: Reset Rotated and Mirrored Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Looks for mirrored and rotated components and resets them to their original orientation.
"""

from GlyphsApp import Glyphs

thisFont = Glyphs.font
selectedLayers = thisFont.selectedLayers
grid = thisFont.grid

# brings macro window to front and clears its log:
Glyphs.clearLog()
print("Fixing rotated components: %s" % thisFont.familyName)
print("Processing %i selected glyph%s:\n" % (len(selectedLayers), "" if len(selectedLayers) == 1 else "s"))

thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	for layer in selectedLayers:
		thisGlyph = layer.parent
		glyphName = thisGlyph.name
		# thisGlyph.beginUndo()  # undo grouping causes crashes
		compCount = 0
		for comp in layer.components:
			transform = comp.transform  # this is computed in Glyphs 3. When dropping support for Glyphs 2, use the position/scale/rotate API
			if transform[0] != 1.0 or transform[3] != 1.0:
				position = comp.position
				if transform[0] < 0:
					position.x -= grid
				if transform[3] < 0:
					position.y -= grid
				comp.transform = (1, 0, 0, 1, position.x, position.y)
				compCount += 1
		if compCount > 0:
			print("✅ Fixed %i component%s in %s" % (compCount, "" if compCount == 1 else "s", glyphName))
		else:
			print("🆗 No transformed components found: %s" % glyphName)
		# thisGlyph.endUndo()  # undo grouping causes crashes
	print("\nDone.")

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: \n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e

finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
