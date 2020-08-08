#MenuTitle: Remove Metrics Keys
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Deletes left and right metrics keys, in all layers of all selected glyphs.
"""

Glyphs.clearLog() # clears macro window log
thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = [ l for l in thisFont.selectedLayers if hasattr(l.parent, 'name')]
 # active layers of selected glyphs

def process( thisGlyph ):
	thisGlyph.setLeftMetricsKey_(None)
	thisGlyph.setRightMetricsKey_(None)
	thisGlyph.setWidthMetricsKey_(None)
	for thisLayer in thisGlyph.layers:
		thisLayer.setLeftMetricsKey_(None)
		thisLayer.setRightMetricsKey_(None)
		thisLayer.setWidthMetricsKey_(None)

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in listOfSelectedLayers:
		thisGlyph = thisLayer.parent
		print("Deleted metrics keys: %s" % thisGlyph.name)
		thisGlyph.beginUndo() # begin undo grouping
		process( thisGlyph )
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
