# MenuTitle: Build Ldot and ldot
__doc__ = """
Builds Ldot, ldot and ldot.sc from existing L, l, l.sc and periodcentered.loclCAT(.case/.sc).
"""

import traceback
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSComponent
from mekkablue import newGlyphWithName


def buildLdot(thisFont, targetGlyphName, baseName, accentName):
	try:
		print("\n%s + %s = %s" % (baseName, accentName, targetGlyphName))
		for thisMaster in thisFont.masters:
			print("\tProcessing master: %s" % thisMaster.name)
			thisMasterID = thisMaster.id
			baseWidth = thisFont.glyphs[baseName].layers[thisMasterID].width
			accentWidth = thisFont.glyphs[accentName].layers[thisMasterID].width
			targetGlyph = thisFont.glyphs[targetGlyphName]
			if not targetGlyph:
				targetGlyph = newGlyphWithName(targetGlyphName)
				thisFont.glyphs.append(targetGlyph)
			else:
				targetGlyph.leftMetricsKey = None
				targetGlyph.rightMetricsKey = None
			targetLayer = targetGlyph.layers[thisMasterID]
			targetLayer.shapes = None
			targetLayer.shapes.append(GSComponent(baseName))
			targetLayer.shapes.append(GSComponent(accentName, NSPoint(baseWidth, 0.0)))
			for thisComp in targetLayer.components:
				thisComp.disableAlignment = False
			targetLayer.width = baseWidth + accentWidth
			targetLayer.leftMetricsKey = None
			targetLayer.rightMetricsKey = None
		return 1
	except Exception:
		print(traceback.format_exc())
		return 0


thisFont = Glyphs.font  # frontmost font
Glyphs.clearLog()  # clears macro window log

if thisFont is None:
	Glyphs.showMacroWindow()
	print("⚠️ Build Ldot and ldot: No font open.")
else:
	print(f"Report for {thisFont.familyName}:")
	if thisFont.filepath:
		print(thisFont.filepath)

	buildGlyphs = [
		("ldot", "l", "periodcentered.loclCAT"),
		("Ldot", "L", "periodcentered.loclCAT.case"),
		("ldot.sc", "l.sc", "periodcentered.loclCAT.sc"),
	]

	createdGlyphs = []
	tabText = ""
	for target, base, accent in buildGlyphs:
		if thisFont.glyphs[base] and thisFont.glyphs[accent]:
			if buildLdot(thisFont, target, base, accent):
				createdGlyphs.append(target)
				tabText += f"/{target}/{base}"

	reportMessage = "%i glyph%s created" % (
		len(createdGlyphs),
		"" if len(createdGlyphs) == 1 else "s",
	)

	print(f"\nDone: {reportMessage}.")

	if tabText:
		thisFont.newTab(tabText)
	else:
		Glyphs.showMacroWindow()
