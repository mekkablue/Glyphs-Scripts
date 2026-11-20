# MenuTitle: Center Glyphs
# -*- coding: utf-8 -*-
__doc__ = """
Center all selected glyphs inside their respective widths.
"""

from AppKit import NSAffineTransform
from GlyphsApp import Glyphs, GSNode, Message


def shiftMatrix(xShift):
	transform = NSAffineTransform.transform()
	transform.translateXBy_yBy_(xShift, 0)
	return transform.transformStruct()


Font = Glyphs.font
if Font:
	Font.disableUpdateInterface()
	try:
		selectedLayers = Font.selectedLayers
		if len(selectedLayers) == 1 and selectedLayers[0].selection:
			currentLayer = selectedLayers[0]
			selectionOrigin = currentLayer.selectionBounds.origin.x
			selectionWidth = currentLayer.selectionBounds.size.width
			shift = shiftMatrix((currentLayer.width - selectionWidth) * 0.5 - selectionOrigin)
			for item in currentLayer.selection:
				try:
					if isinstance(item, GSNode):
						item.x += shift.tX
					else:
						item.applyTransform(shift)
				except Exception as e:
					print(e)
		else:
			for thisLayer in selectedLayers:
				thisMaster = thisLayer.master
				shift = shiftMatrix((thisLayer.LSB - thisLayer.RSB) * -0.5)
				thisLayer.applyTransform(shift)

	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ 'Center Glyphs' Script Error:\n")
		import traceback
		print(traceback.format_exc())
		print()
		raise e

	finally:
		Font.enableUpdateInterface()  # re-enables UI updates in Font View

	print("✅ Centered: %s" % (", ".join([layer.parent.name for layer in selectedLayers])))
else:
	Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
