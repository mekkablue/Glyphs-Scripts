#MenuTitle: Remove Stray Points and Empty Paths
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Deletes stray points (single-node paths) and empty paths (zero-node paths) in selected glyphs. Careful: a stray point can be used as a quick hack to disable automatic alignment.
"""

def process(thisLayer):
	countStrayPoints = 0
	countEmptyPaths = 0
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		for i in range(len(thisLayer.shapes))[::-1]:
			thisPath = thisLayer.shapes[i]
			if thisPath.shapeType == GSShapeTypePath:
				if len(thisPath.nodes) <= 1:
					if len(thisPath.nodes):
						countStrayPoints += 1
					else:
						countEmptyPaths += 1
					del thisLayer.shapes[i]
	else:
		# GLYPHS 2
		for i in range(len(thisLayer.paths))[::-1]:
			thisPath = thisLayer.paths[i]
			if len(thisPath.nodes) <= 1:
				if len(thisPath.nodes):
					countStrayPoints += 1
				else:
					countEmptyPaths += 1
				thisLayer.removePathAtIndex_(i)
	
	return countStrayPoints, countEmptyPaths

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears macro window log:
thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	namesOfAffectedGlyphs = []
	totalCountStrayPoints, totalCountEmptyPaths = 0, 0
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		numberOfDeletedStrayPoints, numberOfDeletedEmptyPaths = process(thisLayer)
		totalCountStrayPoints += numberOfDeletedStrayPoints
		totalCountEmptyPaths += numberOfDeletedEmptyPaths

		# Report deleted nodes:
		glyphName = thisGlyph.name
		if numberOfDeletedStrayPoints+numberOfDeletedEmptyPaths > 0:
			print(f"⚠️ Deleted {numberOfDeletedStrayPoints} stray nodes and {numberOfDeletedEmptyPaths} empty paths in {glyphName}.")
			namesOfAffectedGlyphs.append(glyphName)
		else:
			print(f"✅ No stray points or empty paths in {glyphName}.")

	# Report affected glyphs:
	if namesOfAffectedGlyphs:
		print(
			"\nWARNING:\nStray nodes can be used as a hack to disable automatic alignment. It may be a good idea to check these glyphs for unwanted shifts, and undo if necessary:\n\n/{'/'.join(namesOfAffectedGlyphs)}\n"
			)

	print(f"🔢 {len(selectedLayers)} selected glyphs (of {len(thisFont.glyphs)} in total in the font).")
	print(f"🔢 {len(namesOfAffectedGlyphs)} affected glyphs with {totalCountStrayPoints} stray points and {totalCountEmptyPaths} empty paths.")

	Message(
		title=f"Fixed {thisFont.familyName}",
		message=f"Deleted {totalCountStrayPoints} stray points and {totalCountEmptyPaths} empty paths in {len(selectedLayers)} selected glyphs. Details in Macro Window.",
		OKButton=None,
		)

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e

finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
