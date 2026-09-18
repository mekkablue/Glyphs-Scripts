# MenuTitle: Delete Duplicate Components
# -*- coding: utf-8 -*-
__doc__ = """
Delete components of the same base glyph and in the same position. Useful for accidental double 
"""

from GlyphsApp import Glyphs, GSComponent

def process(thisLayer):
	for i in range(len(thisLayer.shapes)-1, 0, -1):
		shape = thisLayer.shapes[i]
		if not isinstance(shape, GSComponent):
			continue
		for j in range(i-1, -1, -1):
			otherShape = thisLayer.shapes[j]
			if not isinstance(otherShape, GSComponent):
				continue
			areSameComponent = shape.componentName == otherShape.componentName
			areInSameSpot = shape.position == otherShape.position
			if areInSameSpot and areSameComponent:
				del thisLayer.shapes[i]
				break


Glyphs.clearLog()  # clears log in Macro window
thisFont = Glyphs.font  # frontmost font
selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs

print(f"Deleting duplicate components in {thisFont.familyName}...\n")
thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	for thisLayer in set(selectedLayers):
		thisGlyph = thisLayer.parent
		print(f"🔠 {thisGlyph.name}, layer ‘{thisLayer.name}’")
		thisGlyph.beginUndo()  # begin undo grouping
		process(thisLayer)
		thisGlyph.endUndo()    # end undo grouping
	print("\n✅ Done.")
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Delete Duplicate Components\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
