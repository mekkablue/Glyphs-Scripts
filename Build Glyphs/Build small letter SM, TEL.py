# MenuTitle: Build small letter SM, TEL
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates the glyphs: servicemark, telephone.
"""

from GlyphsApp import Glyphs, GSGlyph, GSComponent
from mekkaCore.geometry import transform, offsetLayer

expansion = 5
newGlyphs = {
	"servicemark": "SM",
	"telephone": "TEL"
}

thisFont = Glyphs.font  # frontmost font
selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs

reference = thisFont.glyphs["M"]
trademark = thisFont.glyphs["trademark"]

thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
try:
	for thisMaster in thisFont.masters:
		tmLayer = trademark.layers[thisMaster.id]
		smallscale = tmLayer.bounds.size.height - 2 * expansion
		largescale = reference.layers[thisMaster.id].bounds.size.height
		scale = smallscale / largescale
		upshift = tmLayer.bounds.origin.y + expansion

		measureLayer = tmLayer.copyDecomposedLayer()
		measureLayer.removeOverlap()
		distance = measureLayer.paths[1].bounds.origin.x - (measureLayer.paths[0].bounds.origin.x + measureLayer.paths[0].bounds.size.width)

		for newGlyphName in newGlyphs:
			newGlyph = thisFont.glyphs[newGlyphName]
			if not newGlyph:
				newGlyph = GSGlyph(newGlyphName)
				thisFont.glyphs.append(newGlyph)

			newGlyph.leftKerningGroup = trademark.leftKerningGroup
			newGlyph.rightKerningGroup = trademark.rightKerningGroup
			newLayer = newGlyph.layers[thisMaster.id]
			newLayer.clear()
			for i, letter in enumerate(newGlyphs[newGlyphName]):
				letterComp = GSComponent(letter)
				newLayer.components.append(letterComp)
				letterComp.disableAlignment = True
				scaleDown = transform(scale=scale).transformStruct()
				letterComp.applyTransform(scaleDown)
				if i > 0:
					prevComp = newLayer.components[i - 1]
					newOrigin = prevComp.bounds.origin.x + prevComp.bounds.size.width + distance + 2 * expansion
					currentOrigin = letterComp.bounds.origin.x
					shiftRight = transform(shiftX=(newOrigin - currentOrigin)).transformStruct()
					letterComp.applyTransform(shiftRight)

			newLayer.decomposeComponents()
			newLayer.anchors = None
			shiftUp = transform(shiftY=upshift).transformStruct()
			newLayer.applyTransform(shiftUp)
			offsetLayer(newLayer, expansion)
			newLayer.LSB = tmLayer.LSB
			newLayer.RSB = tmLayer.RSB
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
