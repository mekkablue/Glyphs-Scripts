# MenuTitle: Center punt volat
__doc__ = """
Shifts all periodcentered.loclCAT glyphs horizontally so they fit between two L’s.
Suffixed variants (e.g. .loclCAT.ss01) are centered between L’s with the same suffix, or between the default L’s if no such L exists.
If one of periodcentered.loclCAT, .loclCAT.case and .loclCAT.sc does not exist, it is built from period first: 92% size, centered at 45% of the ascender (lowercase) or 62% of the cap height or small cap height.
⚠️ Hold down ⌘ Cmd and ⇧ Shift for processing ALL open fonts.
"""

from AppKit import NSMidX, NSMidY, NSAffineTransform, NSEvent, NSEventModifierFlagCommand, NSEventModifierFlagShift
from GlyphsApp import Glyphs, GSControlLayer, Message
from mekkablue import newLineControlLayer, newGlyphWithName
from mekkablue.geometry import transform

PUNT_VOLAT_SCALE = 0.92
LOWERCASE_HEIGHT_FACTOR = 0.45  # of the ascender
CAPS_HEIGHT_FACTOR = 0.62  # of cap height or small cap height


def smallCapHeightOfMaster(thisFont, thisMaster):
	"""The small cap height parameter of the master, else the height of H.sc, else the x-height."""
	smallCapHeight = thisMaster.customParameters["smallCapHeight"]
	if smallCapHeight:
		return float(smallCapHeight)
	hsc = thisFont.glyphs["H.sc"]
	if hsc:
		hscBounds = hsc.layers[thisMaster.id].bounds
		if hscBounds is not None:
			return hscBounds.origin.y + hscBounds.size.height
	return thisMaster.xHeight


def buildPuntVolat(thisFont, puntVolatName):
	"""
	Builds a missing periodcentered.loclCAT glyph from period: decomposed copy at 92% size,
	vertically centered at 45% of the ascender (lowercase), or at 62% of the cap height (.case) or small cap height (.sc).
	Lowercase: LSB is half the LSB of period, rounded by 5u, RSB is =|.
	Uppercase and small cap variants: width is the LSB of period, but at least 0.
	"""
	period = thisFont.glyphs["period"]
	if not period:
		print(f"❌ Cannot build {puntVolatName}: no period in ‘{thisFont.familyName}’.")
		return False
	if not all(layer.shapes for layer in period.layers if layer.isMasterLayer):
		print(f"🚫 Cannot build {puntVolatName}: period is empty on a master.")
		return False

	puntVolatGlyph = newGlyphWithName(puntVolatName)
	thisFont.glyphs.append(puntVolatGlyph)
	puntVolatGlyph.updateGlyphInfo()
	isLowercase = puntVolatName == "periodcentered.loclCAT"
	isSmallCap = puntVolatName.endswith(".sc")

	for master in thisFont.masters:
		periodLayer = period.layers[master.id]
		puntVolatLayer = puntVolatGlyph.layers[master.id]
		puntVolatLayer.clear()
		for shape in periodLayer.copyDecomposedLayer().shapes:
			puntVolatLayer.shapes.append(shape.copy())

		# scale down around its own center:
		bounds = puntVolatLayer.bounds
		centerX, centerY = NSMidX(bounds), NSMidY(bounds)
		if isLowercase:
			targetY = master.ascender * LOWERCASE_HEIGHT_FACTOR
		elif isSmallCap:
			targetY = smallCapHeightOfMaster(thisFont, master) * CAPS_HEIGHT_FACTOR
		else:
			targetY = master.capHeight * CAPS_HEIGHT_FACTOR
		for matrix in (
			transform(shiftX=-centerX, shiftY=-centerY),
			transform(scale=PUNT_VOLAT_SCALE),
			transform(shiftX=centerX, shiftY=targetY),
		):
			puntVolatLayer.applyTransform(matrix.transformStruct())

		periodLSB = periodLayer.LSB
		if isLowercase:
			# LSB is half of period’s, rounded by 5u; RSB follows through the metrics key:
			targetLSB = 5 * round(periodLSB * 0.5 / 5)
			shiftX = targetLSB - puntVolatLayer.bounds.origin.x
			puntVolatLayer.applyTransform(transform(shiftX=shiftX).transformStruct())
		else:
			puntVolatLayer.width = max(0, round(periodLSB))

	if isLowercase:
		puntVolatGlyph.leftMetricsKey = None
		puntVolatGlyph.rightMetricsKey = "=|"
		for layer in puntVolatGlyph.layers:
			if layer.isMasterLayer:
				layer.syncMetrics()
	print(f"🔨 Built {puntVolatName} from period.")
	return True


keysPressed = NSEvent.modifierFlags()
commandKeyPressed = (keysPressed & NSEventModifierFlagCommand) == NSEventModifierFlagCommand
shiftKeyPressed = (keysPressed & NSEventModifierFlagShift) == NSEventModifierFlagShift

Glyphs.clearLog()  # clears log in Macro window
print("Report for ‘Center punt volat’")

if commandKeyPressed and shiftKeyPressed:
	theseFonts = Glyphs.fonts
	print("⚠️ Processing ALL open fonts.")
else:
	theseFonts = [Glyphs.font]

if None in theseFonts:
	Message(title="No Font Open", message="This script requires a font. Open a font source and try again.", OKButton=None)
	raise SystemExit

for thisFont in theseFonts:
	thisFontPath = thisFont.filepath
	if thisFontPath:
		thisFontFileName = thisFontPath.lastPathComponent()
	else:
		thisFontFileName = f"{thisFont.familyName} (unsaved)"
	print(f"\n📄 Preparing {thisFontFileName}...\n🖥️ Path: {thisFontPath}")

	baseDict = {
		"periodcentered.loclCAT.case": "L",
		"periodcentered.loclCAT": "l",
		"periodcentered.loclCAT.sc": "l.sc",
	}

	# build missing punt volat glyphs from period:
	for baseName in baseDict:
		if not thisFont.glyphs[baseName]:
			buildPuntVolat(thisFont, baseName)

	allGlyphNames = [g.name for g in thisFont.glyphs if g.export]

	# suffixed variants are centered between L’s with the same suffix, or else between the default L’s:
	puntVolatDict = dict(baseDict)
	for glyphName in allGlyphNames:
		if glyphName in baseDict:
			continue
		# the longest base name wins, e.g. .loclCAT.sc.ss01 belongs to .loclCAT.sc, not .loclCAT
		baseNames = [n for n in baseDict if glyphName.startswith(n + ".")]
		if not baseNames:
			continue
		baseName = max(baseNames, key=len)
		suffix = glyphName[len(baseName):]
		suffixedLName = baseDict[baseName] + suffix
		if suffixedLName in allGlyphNames:
			puntVolatDict[glyphName] = suffixedLName
		else:
			puntVolatDict[glyphName] = baseDict[baseName]

	puntVolatNames = sorted(puntVolatDict.keys())

	tabText = ""
	for puntVolatName in puntVolatNames:
		puntVolatGlyph = thisFont.glyphs[puntVolatName]
		lName = puntVolatDict[puntVolatName]
		lGlyph = thisFont.glyphs[lName]
		if not puntVolatGlyph:
			print(f"❌ No glyph {puntVolatName} in ‘{thisFontFileName}’.")
		elif not all(layer.shapes for layer in puntVolatGlyph.layers if layer.isMasterLayer):
			print(f"🚫 No shapes in {puntVolatName} in ‘{thisFontFileName}’.")
		elif not lGlyph:
			print(f"❌ No glyph {lName} in ‘{thisFontFileName}’.")
		elif not all(layer.shapes for layer in lGlyph.layers if layer.isMasterLayer):
			print(f"🚫 No shapes in {lName} in ‘{thisFontFileName}’.")
		else:
			tabText += f"/{lName}/{puntVolatName}/{lName}"
			# shift punt volat into center on every master:
			for master in thisFont.masters:
				mID = master.id
				# punt volat
				puntVolatLayer = puntVolatGlyph.layers[mID]
				centerY = NSMidY(puntVolatLayer.bounds)
				lsbPunt = puntVolatLayer.lsbAtHeight_(centerY)
				rsbPunt = puntVolatLayer.rsbAtHeight_(centerY)
				# L
				lLayer = lGlyph.layers[mID]
				lsbL = lLayer.lsbAtHeight_(centerY)
				rsbL = lLayer.rsbAtHeight_(centerY)
				# calculate shift
				targetSB = int((lsbPunt + rsbPunt + lsbL + rsbL + 1) * 0.5)  # round up 1u, avoid negative width
				move = targetSB - (rsbL + lsbPunt)
				if master.italicAngle != 0.0:  # optical correction for italics
					move -= int(master.italicAngle / 4)
				shift = NSAffineTransform.transform()
				shift.translateXBy_yBy_(move, 0)
				# shift punt volat
				puntVolatLayer.applyTransform(shift.transformStruct())
				# report
				print(f"✅ Shifted {puntVolatName} on master ‘{master.name}’.")

			# reinterpolate sidebearings for brace layers:
			for puntVolatLayer in puntVolatGlyph.layers:
				if puntVolatLayer.isSpecialLayer:
					puntVolatLayer.reinterpolateMetrics()
					print(f"✅ Reinterpolated {puntVolatName} on special layer ‘{puntVolatLayer.name}’.")

	if not tabText:
		Glyphs.showMacroWindow()
	else:
		print("Preparing report in Edit View...")
		thisTab = thisFont.currentTab
		if not thisTab:
			thisTab = thisFont.newTab()
		thisTab.text = tabText

		# display line for each master:
		cutoff = []
		names = []
		for i, layer in enumerate(thisTab.layers):
			if isinstance(layer, GSControlLayer):
				cutoff.append(i)
			else:
				if not cutoff:
					names.append(layer.parent.name)

		theseLayers = []
		for m in thisFont.masters:
			for gname in names:
				layer = thisFont.glyphs[gname].layers[m.id]
				theseLayers.append(layer)
			theseLayers.append(newLineControlLayer())

		if theseLayers:
			if Glyphs.versionNumber >= 3:
				thisFont.currentTab.layers = list(thisFont.currentTab.layers) + theseLayers
			else:
				for layer in theseLayers:
					thisFont.currentTab.layers.append(layer)
