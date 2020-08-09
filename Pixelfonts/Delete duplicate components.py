#MenuTitle: Delete Duplicate Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Looks for duplicate components (same component, same x/y values) and keeps only one of them.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def getAttr( thisLayer, compNumber ):
	return [thisLayer.components[compNumber].componentName, thisLayer.components[compNumber].x, thisLayer.components[compNumber].y]


def scanForDuplicates( thisLayer, compNumber ):
	if compNumber == len( thisLayer.components ) - 1:
		return []
	else:
		indexList = scanForDuplicates( thisLayer, compNumber + 1 )
		currAttr = getAttr( thisLayer, compNumber )
		
		for i in range( compNumber + 1, len( thisLayer.components ) ):
			if currAttr == getAttr( thisLayer, i ):
				indexList.append(i)
		
		return sorted( set( indexList ) )


def process( thisLayer ):
	if len( thisLayer.components ) != 0:
		thisLayer.parent.beginUndo()
		indexesToBeDeleted = scanForDuplicates( thisLayer, 0 )
		for indexToBeDeleted in indexesToBeDeleted[::-1]:
			del thisLayer.components[indexToBeDeleted]
		thisLayer.parent.endUndo()
		return len( indexesToBeDeleted )
	else:
		return 0


Font.disableUpdateInterface()
try:
	for thisLayer in selectedLayers:
		numOfDeletedComponents = process( thisLayer )
		print("%i components deleted in: %s (%s)" % (numOfDeletedComponents, thisLayer.parent.name, thisLayer.name)
		
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
	
finally:
	Font.enableUpdateInterface() # re-enables UI updates in Font View

