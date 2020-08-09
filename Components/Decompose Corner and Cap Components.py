#MenuTitle: Decompose Corner and Cap Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Recreates the current paths without caps or components.
"""

thisFont = Glyphs.font # frontmost font
	
def process( thisLayer ):
	thisLayer.decomposeSmartOutlines()
	thisLayer.cleanUpPaths() # duplicate nodes at startpoint

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		print("Processing", thisGlyph.name)
		thisGlyph.beginUndo() # begin undo grouping
		process( thisLayer )
		thisGlyph.endUndo()   # end undo grouping
		
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
	
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
