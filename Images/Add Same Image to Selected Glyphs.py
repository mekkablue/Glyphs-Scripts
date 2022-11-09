#MenuTitle: Add Same Image to Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Asks you for an image file and inserts it as background image into all selected layers.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process(thisLayer, imageFilePath):
	try:
		thisImage = GSBackgroundImage.alloc().initWithPath_(imageFilePath)
		thisLayer.setBackgroundImage_(thisImage)
	except Exception as e:
		if "NoneType" in str(e):
			return "No image found."
		else:
			return "Error: %s." % e
	return "OK."

Font.disableUpdateInterface()
try:
	imageFilePath = GetOpenFile(message="Select an image:", allowsMultipleSelection=False, filetypes=["jpeg", "png", "tif", "gif", "pdf"])

	print("Putting %s into:" % imageFilePath)

	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		# thisGlyph.beginUndo() # undo grouping causes crashes
		print("-- %s: %s" % (thisGlyph.name, process(thisLayer, imageFilePath)))
		# thisGlyph.endUndo() # undo grouping causes crashes

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e

finally:
	Font.enableUpdateInterface()
