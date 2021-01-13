#MenuTitle: Remove all Open Paths
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Deletes all paths in visible layers of selected glyphs.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	count = 0

	thisLayer.parent.beginUndo()
	for i in range( len( thisLayer.paths ))[::-1]:
		if thisLayer.paths[i].closed == False:
			thisPath = thisLayer.paths[i]
			if Glyphs.versionNumber >= 3:
				index = thisLayer.shapes.index(thisPath)
				del thisLayer.shapes[index]
			else:
				del thisLayer.paths[i]
			count += 1
	thisLayer.parent.endUndo()
	
	return count

Font.disableUpdateInterface()
try:
	for thisLayer in selectedLayers:
		print("Removing %i open paths in %s." % ( process( thisLayer ), thisLayer.parent.name ))
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	Font.enableUpdateInterface() # re-enables UI updates in Font View
