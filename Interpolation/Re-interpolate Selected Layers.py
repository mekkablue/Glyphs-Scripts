#MenuTitle: Re-interpolate Selected Layers
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Batch-reinterpolates all selected layers. Same as the Re-Interpolate command in the Layers palette, but for multiple selections.
"""

from GlyphsApp import Glyphs

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears log in Macro window
print(f"👩🏼‍🔬 Reinterpolating {len(selectedLayers)} layers:\n")
thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		print(f"- {thisGlyph.name}, layer: {thisLayer.name}")
		thisGlyph.beginUndo() # begin undo grouping
		thisLayer.reinterpolate()
		thisGlyph.endUndo()   # end undo grouping
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Re-interpolate Selected Layers\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
