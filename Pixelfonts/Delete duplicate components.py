#MenuTitle: Delete Duplicate Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Looks for duplicate components (same component, same x/y values) and keeps only one of them.
"""

def getAttr(thisLayer, compNumber):
	thisComp = thisLayer.components[compNumber]
	return (thisComp.componentName, thisComp.x, thisComp.y, thisComp.transform)

def scanForDuplicates(thisLayer, compNumber):
	if compNumber == len(thisLayer.components) - 1:
		return []
	else:
		indexList = scanForDuplicates(thisLayer, compNumber + 1)
		currAttr = getAttr(thisLayer, compNumber)

		for i in range(compNumber + 1, len(thisLayer.components)):
			if currAttr == getAttr(thisLayer, i):
				indexList.append(i)

		return sorted(set(indexList))

def process(thisLayer):
	if len(thisLayer.components) != 0:
		# thisLayer.parent.beginUndo() # undo grouping causes crashes
		indexesToBeDeleted = scanForDuplicates(thisLayer, 0)
		for indexToBeDeleted in indexesToBeDeleted[::-1]:
			if Glyphs.versionNumber >= 3:
				# GLYPHS 3
				for i in range(len(thisLayer.shapes)):
					compToBeDeleted = thisLayer.components[indexToBeDeleted]
					thisShape = thisLayer.shapes[i]
					if thisShape == compToBeDeleted:
						del thisLayer.shapes[i]
			else:
				# GLYPHS 2
				del thisLayer.components[indexToBeDeleted]
		# thisLayer.parent.endUndo() # undo grouping causes crashes
		return len(indexesToBeDeleted)
	else:
		return 0

thisFont = Glyphs.font
thisFont.disableUpdateInterface()
try:
	Glyphs.clearLog()
	print("Deleting duplicate components: %s\n" % thisFont.familyName)
	totalCount = 0
	selectedLayers = thisFont.selectedLayers
	for thisLayer in selectedLayers:
		numOfDeletedComponents = process(thisLayer)
		totalCount += numOfDeletedComponents
		print("%i components deleted in: %s (%s)" % (numOfDeletedComponents, thisLayer.parent.name, thisLayer.name))
	print("\n✅ Done. Deleted %i component%s in total." % (totalCount, "" if totalCount == 1 else "s"))

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e

finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
