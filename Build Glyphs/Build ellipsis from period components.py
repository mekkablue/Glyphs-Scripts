#MenuTitle: Build ellipsis from period components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Inserts exit and entry anchors in the period glyph and rebuilds ellipsis with auto-aligned components of period.\n\nATTENTION: decomposes all period components used in other glyphs (e.g., colon).
"""

from AppKit import NSPoint

def decomposeGlyphsContaining(font, componentName, exceptions=[]):
	glyphNames = []
	for master in font.masters:
		for glyph in font.glyphsContainingComponentWithName_masterId_(componentName, master.id):
			if not glyph.name in glyphNames and not glyph.name in exceptions:
				glyphNames.append(glyph.name)
	if glyphNames:
		for glyphName in glyphNames:
			glyph = font.glyphs[glyphName]
			for layer in glyph.layers:
				if layer.components:
					for i in range(len(layer.components) - 1, -1, -1):
						component = layer.components[i]
						if component.componentName == componentName:
							layer.decomposeComponent_(component)
	return glyphNames

Glyphs.clearLog() # clears log in Macro window
thisFont = Glyphs.font # frontmost font
period = thisFont.glyphs["period"]

if not period:
	Message(title="Build ellipsis Script Error", message="No period glyph in font. Add it and try again.", OKButton=None)
	exit()

ellipsis = thisFont.glyphs["ellipsis"]
if not ellipsis:
	print("⚙️ Creating ellipsis glyph (did not exist)")
	ellipsis = GSGlyph("ellipsis")
	thisFont.glyphs.append(ellipsis)

# decomposing non-ellipsis components:
decomposedGlyphs = decomposeGlyphsContaining(thisFont, period.name, exceptions=(ellipsis.name, ))
if decomposedGlyphs:
	print("⚠️ Decomposed %s components in %i glyph%s: %s" % (period.name, len(decomposedGlyphs), "" if len(decomposedGlyphs) == 1 else "s", ", ".join(decomposedGlyphs)))

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisMaster in thisFont.masters:
		print("Ⓜ️ %s" % thisMaster.name)
		print("   Adding #exit and #entry in period...")
		mID = thisMaster.id
		periodLayer = period.layers[mID]
		distance = periodLayer.width - int((periodLayer.width - periodLayer.bounds.size.width) * 0.3)
		for anchorName, anchorX in zip(("#entry", "#exit"), (0, distance)):
			anchor = GSAnchor()
			anchor.name = anchorName
			anchor.position = NSPoint(anchorX, 0)
			periodLayer.anchors.append(anchor)

		print("   Backing up period...")
		ellipsisLayer = ellipsis.layers[mID]
		ellipsisLayer.swapForegroundWithBackground()
		ellipsisLayer.background.decomposeComponents()
		ellipsisLayer.shapes = None
		for i in range(3):
			ellipsisLayer.shapes.append(GSComponent("period"))
		for thisComponent in ellipsisLayer.components:
			thisComponent.setDisableAlignment_(False)
		ellipsisLayer.updateMetrics()

	print("🔢 Setting Metrics Keys for ellipsis...")
	ellipsis.leftMetricsKey = "=+20"
	ellipsis.rightMetricsKey = "=+20"

	thisFont.newTab(".…")
	print("✅Done.")

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Build ellipsis from period components\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
