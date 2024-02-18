# MenuTitle: Center punt volat
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Shifts all periodcentered.loclCAT glyphs horizontally so it fits between two L’s.
⚠️ Hold down ⌘ Cmd and ⇧ Shift for processing ALL open fonts.
"""

from AppKit import NSMidY, NSAffineTransform, NSEvent
from Foundation import NSMutableAttributedString, NSAttributedString
from GlyphsApp import Glyphs, GSControlLayer


keysPressed = NSEvent.modifierFlags()
commandKey = 1048576
shiftKey = 131072
commandKeyPressed = keysPressed & commandKey == commandKey
shiftKeyPressed = keysPressed & shiftKey == shiftKey

Glyphs.clearLog()  # clears log in Macro window
print("Report for ‘Center punt volat’")

if commandKeyPressed and shiftKeyPressed:
	theseFonts = Glyphs.fonts
	print("⚠️ Processing ALL open fonts.")
else:
	theseFonts = (Glyphs.font, )

for thisFont in theseFonts:
	thisFontPath = thisFont.filepath
	if thisFontPath:
		thisFontFileName = thisFontPath.lastPathComponent()
	else:
		thisFontFileName = "<UNSAVED DOCUMENT>"
	print(f"\n📄 Preparing {thisFontFileName}...\n🖥️ Path: {thisFontPath}")

	puntVolatDict = {
		"periodcentered.loclCAT.case": "L",
		"periodcentered.loclCAT": "l",
		"periodcentered.loclCAT.sc": "l.sc",
	}

	puntVolatNames = sorted(puntVolatDict.keys())
	allGlyphNames = [g.name for g in thisFont.glyphs if g.export]

	for puntVolatName in puntVolatNames:
		dotNames = [g.name for g in thisFont.glyphs if g.name not in puntVolatNames and g.name.startswith(puntVolatName)]
		for dotName in dotNames:
			suffix = dotName[len(puntVolatName):]
			dotLname = puntVolatDict[puntVolatName] + suffix
			if dotLname in allGlyphNames:
				puntVolatDict[dotName] = dotLname

	# rescan puntVolatNames (suffixed variants may have been added):
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
					theseLayers.append(GSControlLayer.newline())

				if theseLayers:
					if Glyphs.versionNumber >= 3:
						thisFont.currentTab.layers.extend(theseLayers)
					else:
						for layer in theseLayers:
							thisFont.currentTab.layers.append(layer)
