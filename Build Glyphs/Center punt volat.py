# MenuTitle: Center punt volat
__doc__ = """
Shifts all periodcentered.loclCAT glyphs horizontally so they fit between two L’s.
Suffixed variants (e.g. .loclCAT.ss01) are centered between L’s with the same suffix, or between the default L’s if no such L exists.
⚠️ Hold down ⌘ Cmd and ⇧ Shift for processing ALL open fonts.
"""

from AppKit import NSMidY, NSAffineTransform, NSEvent, NSCommandKeyMask, NSShiftKeyMask
from GlyphsApp import Glyphs, GSControlLayer
from mekkablue import newLineControlLayer

keysPressed = NSEvent.modifierFlags()
commandKeyPressed = (keysPressed & NSCommandKeyMask) == NSCommandKeyMask
shiftKeyPressed = (keysPressed & NSShiftKeyMask) == NSShiftKeyMask

Glyphs.clearLog()  # clears log in Macro window
print("Report for ‘Center punt volat’")

if commandKeyPressed and shiftKeyPressed:
	theseFonts = Glyphs.fonts
	print("⚠️ Processing ALL open fonts.")
else:
	theseFonts = [Glyphs.font]

for thisFont in theseFonts:
	thisFontPath = thisFont.filepath
	if thisFontPath:
		thisFontFileName = thisFontPath.lastPathComponent()
	else:
		thisFontFileName = "<UNSAVED DOCUMENT>"
	print(f"\n📄 Preparing {thisFontFileName}...\n🖥️ Path: {thisFontPath}")

	baseDict = {
		"periodcentered.loclCAT.case": "L",
		"periodcentered.loclCAT": "l",
		"periodcentered.loclCAT.sc": "l.sc",
	}
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
