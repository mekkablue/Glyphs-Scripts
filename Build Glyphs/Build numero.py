# MenuTitle: Build numero
__doc__ = """
Builds numero (№) from the components N, ordmasculine and period. Adds a _#numero anchor in the bounding box center of period, and a #numero anchor in ordmasculine, horizontally centered under its shape (respecting the italic angle). The anchor height is chosen so that, in numero, the space between period and baseline is twice the space between period and ordmasculine.
"""

from Foundation import NSPoint
from GlyphsApp import Glyphs, GSComponent, Message
from mekkablue import newAnchorWithName, newGlyphWithName
from mekkablue.geometry import italicize

ANCHOR_NAME = "#numero"
MARK_ANCHOR_NAME = "_#numero"


def setAnchor(layer, anchorName, position):
	if anchorName in layer.anchors:
		del layer.anchors[anchorName]
	layer.anchors.append(newAnchorWithName(anchorName, position))


Glyphs.clearLog()
font = Glyphs.font
if font is None:
	Message(title="No Font Open", message="This script requires a font. Open a font source and try again.", OKButton=None)
else:
	print(f"Build numero for {font.familyName}\n")
	missing = [name for name in ("N", "ordmasculine", "period") if font.glyphs[name] is None]
	if missing:
		Message(
			title="Build numero",
			message=f"Missing glyphs in font: {', '.join(missing)}. Add them and try again.",
			OKButton=None,
		)
	else:
		numero = font.glyphs["numero"]
		if numero is None:
			print("⚙️ Creating numero (did not exist)")
			numero = newGlyphWithName("numero")
			font.glyphs.append(numero)
		numero.leftMetricsKey = None
		numero.rightMetricsKey = None

		font.disableUpdateInterface()
		try:
			skippedMasters = []
			for master in font.masters:
				masterID = master.id
				print(f"Ⓜ️ {master.name}")
				nLayer = font.glyphs["N"].layers[masterID]
				ordLayer = font.glyphs["ordmasculine"].layers[masterID]
				periodLayer = font.glyphs["period"].layers[masterID]
				ordBounds = ordLayer.bounds
				periodBounds = periodLayer.bounds
				if not ordBounds.size.width or not periodBounds.size.width:
					print("\t⚠️ ordmasculine or period is empty, skipping")
					skippedMasters.append(master.name)
					continue

				# period: _#numero in bbox center
				setAnchor(
					periodLayer,
					MARK_ANCHOR_NAME,
					NSPoint(
						round(periodBounds.origin.x + periodBounds.size.width / 2.0),
						round(periodBounds.origin.y + periodBounds.size.height / 2.0),
					),
				)

				# numero (anchor on ordmasculine is a placeholder at first, then derived from the component bboxes)
				numeroLayer = numero.layers[masterID]
				if numeroLayer.shapes:
					hasSameStructure = (
						not numeroLayer.paths
						and [component.componentName for component in numeroLayer.components] == ["N", "ordmasculine", "period"]
						and not any(component.disableAlignment for component in numeroLayer.components)
					)
					if hasSameStructure:
						print("\tℹ️ existing numero already is auto-aligned N, ordmasculine, period, no backup needed")
					else:
						print("\t💾 backing up existing numero shapes in background")
						numeroLayer.background.shapes = None
						for shape in numeroLayer.shapes:
							numeroLayer.background.shapes.append(shape.copy())
				numeroLayer.shapes = None
				numeroLayer.shapes.append(GSComponent("N"))
				numeroLayer.shapes.append(GSComponent("ordmasculine", NSPoint(nLayer.width, 0)))
				numeroLayer.shapes.append(GSComponent("period"))
				for component in numeroLayer.components:
					component.disableAlignment = False
				numeroLayer.width = nLayer.width + ordLayer.width
				ordComponent = numeroLayer.components[1]
				periodComponent = numeroLayer.components[2]

				# ordmasculine: #numero horizontally centered under the shape, slanted along the italic angle.
				# Measured on the bbox of the ordmasculine component in numero, relative to its origin:
				ordBox = ordComponent.bounds
				periodHeight = periodComponent.bounds.size.height
				ordBottom = ordBox.origin.y
				# gap below period (to baseline) = 2 * gap above period (to ordmasculine bbox):
				# gapBelow = 2 * (ordBottom - gapBelow - periodHeight)
				gapBelow = 2.0 * (ordBottom - periodHeight) / 3.0
				if gapBelow < 0:
					print("\t⚠️ ordmasculine is too low for period to fit beneath it, spacing is negative")
				anchorY = gapBelow + periodHeight / 2.0
				ordCenter = NSPoint(
					ordBox.origin.x + ordBox.size.width / 2.0 - ordComponent.position.x,
					ordBox.origin.y + ordBox.size.height / 2.0 - ordComponent.position.y,
				)
				anchorPosition = italicize(NSPoint(ordCenter.x, anchorY - ordComponent.position.y), master.italicAngle, ordCenter.y)
				setAnchor(ordLayer, ANCHOR_NAME, NSPoint(round(anchorPosition.x), round(anchorY - ordComponent.position.y)))
				numeroLayer.updateMetrics()
				numeroLayer.alignComponents()

				# verify with the real bounding boxes of the components
				ordBox = numeroLayer.components[1].bounds
				periodBox = numeroLayer.components[2].bounds
				gapBelowMeasured = periodBox.origin.y
				gapAboveMeasured = ordBox.origin.y - (periodBox.origin.y + periodBox.size.height)
				print(f"\t✅ numero built: period to baseline {gapBelowMeasured:.1f}, period to ordmasculine {gapAboveMeasured:.1f}")

				# kerning N-ordmasculine like N-o, but only if N-o is negative and N-ordmasculine has none
				if font.glyphs["o"]:
					existingKerning = font.kerningForPair(masterID, "N", "ordmasculine")
					kerningNo = font.kerningForPair(masterID, "N", "o")
					if existingKerning is not None and existingKerning < 100000:
						print(f"\tℹ️ N-ordmasculine kerning exists ({existingKerning:.0f}), left alone")
					elif kerningNo is None or kerningNo > 100000 or kerningNo >= 0:
						print("\tℹ️ no negative N-o kerning, no N-ordmasculine kerning added")
					else:
						font.setKerningForPair(masterID, "N", "ordmasculine", kerningNo)
						print(f"\t↔️ added N-ordmasculine kerning {kerningNo:.0f} (same as N-o)")
		finally:
			font.enableUpdateInterface()

		if skippedMasters:
			Glyphs.showMacroWindow()
		font.newTab("/numero")
		Glyphs.showNotification("Build numero", "Done. Details in Macro Window.")
