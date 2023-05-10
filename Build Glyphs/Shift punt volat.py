#MenuTitle: Center punt volat
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Shifts all periodcentered.loclCAT glyphs horizontally so it fits between two L’s. 
⚠️ Hold down ⌘ Cmd and ⇧ Shift for processing ALL open fonts.
"""

from AppKit import NSMidY, NSAffineTransform, NSEvent
from Foundation import NSMutableAttributedString, NSAttributedString

keysPressed = NSEvent.modifierFlags()
commandKey = 1048576
shiftKey = 131072
commandKeyPressed = keysPressed & commandKey == commandKey
shiftKeyPressed = keysPressed & shiftKey == shiftKey

Glyphs.clearLog() # clears log in Macro window
print("Report for ‘Center punt volat’")

if commandKeyPressed and shiftKeyPressed:
	theseFonts = Glyphs.fonts
	print("⚠️ Processing ALL open fonts.")
else:
	theseFonts = (Glyphs.font,)

for thisFont in theseFonts:
	thisFontPath = thisFont.filepath
	thisFontFileName = thisFontPath.lastPathComponent()
	print(f"\n📄 Preparing {thisFontFileName}...\n🖥️ Path: {thisFontPath}")

	puntVolatDict = {
		"periodcentered.loclCAT.case": "L",
		"periodcentered.loclCAT": "l",
		"periodcentered.loclCAT.sc": "l.sc",
	}

	puntVolatNames = sorted(puntVolatDict.keys())
	allGlyphNames = [g.name for g in thisFont.glyphs if g.export]

	for puntVolatName in puntVolatNames:
		dotNames = [
			g.name for g in thisFont.glyphs 
			if not g.name in puntVolatNames 
			and g.name.startswith(puntVolatName)
			]
		for dotName in dotNames:
			suffix = dotName[len(puntVolatName):]
			dotLname = puntVolatDict[puntVolatName] + suffix
			if dotLname in allGlyphNames:
				puntVolatDict[dotName] = dotLname

	# rescan puntVolatNames (suffixed variants may have been added):
	puntVolatNames = sorted(puntVolatDict.keys())

	tabText = ""
	for puntVolatName in puntVolatNames:
		puntVolat = thisFont.glyphs[puntVolatName]
		lName = puntVolatDict[puntVolatName]
		l = thisFont.glyphs[lName]
		if not puntVolat:
			print(f"❌ No glyph {puntVolatName} in ‘{thisFontFileName}’.")
			Glyphs.showMacroWindow()
		elif not all(layer.shapes for layer in puntVolat.layers if layer.isMasterLayer):
			print(f"🚫 No shapes in {puntVolatName} in ‘{thisFontFileName}’.")
			Glyphs.showMacroWindow()
		elif not l:
			print(f"❌ No glyph {lName} in ‘{thisFontFileName}’.")
			Glyphs.showMacroWindow()
		elif not all(layer.shapes for layer in l.layers if layer.isMasterLayer):
			print(f"🚫 No shapes in {lName} in ‘{thisFontFileName}’.")
			Glyphs.showMacroWindow()
		else:
			tabText += f"/{lName}/{puntVolatName}/{lName}"
			# shift punt volat into center on every master:
			for master in thisFont.masters:
				mID = master.id
				# punt volat
				puntVolatLayer = puntVolat.layers[mID]
				centerY = NSMidY(puntVolatLayer.bounds)
				lsbPunt = puntVolatLayer.lsbAtHeight_(centerY)
				rsbPunt = puntVolatLayer.rsbAtHeight_(centerY)
				# L
				lLayer = l.layers[mID]
				lsbL = lLayer.lsbAtHeight_(centerY)
				rsbL = lLayer.rsbAtHeight_(centerY)
				# calculate shift
				targetSB = int((lsbPunt+rsbPunt+lsbL+rsbL+1)*0.5) # round up 1u, avoid negative width
				move = targetSB - (rsbL+lsbPunt)
				if master.italicAngle != 0.0: # optical correction for italics
					move -= int(master.italicAngle/4)
				shift = NSAffineTransform.transform()
				shift.translateXBy_yBy_(move, 0)
				# shift punt volat
				puntVolatLayer.applyTransform(shift.transformStruct())
				# report
				print(f"✅ Shifted {puntVolatName} on master ‘{master.name}’.")
		
			# reinterpolate sidebearings for brace layers:
			for puntVolatLayer in puntVolat.layers:
				if puntVolatLayer.isSpecialLayer:
					puntVolatLayer.reinterpolateMetrics()
					print(f"✅ Reinterpolated {puntVolatName} on special layer ‘{puntVolatLayer.name}’.")
			
			if tabText:
				print("Preparing report in Edit View...")
				thisTab = thisFont.currentTab
				if not thisTab:
					thisTab = thisFont.newTab()
				thisTab.text = tabText
		
				# display line for each master:
				cutoff = []
				names = []
				for i,l in enumerate(thisTab.layers):
					if type(l) == GSControlLayer:
						cutoff.append(i)
					else:
						if not cutoff:
							names.append(l.parent.name)

				theseLayers = []
				for m in thisFont.masters:
					for gname in names:
						layer = thisFont.glyphs[gname].layers[m.id]
						theseLayers.append( layer )
					theseLayers.append( GSControlLayer.newline() )

				if theseLayers:
					# thisFont.currentTab.layers.append( theseLayers ) # BROKEN IN 1224
					# WORKAROUND:
					string = NSMutableAttributedString.alloc().init()
					for l in theseLayers:
						if l.className() == "GSLayer":
							char = chr( thisFont.characterForGlyph_(l.parent) )
							A = NSAttributedString.alloc().initWithString_attributes_(char, {"GSLayerIdAttrib": l.layerId})
						elif l.className() == "GSBackgroundLayer":
							char = chr( thisFont.characterForGlyph_(l.parent) )
							A = NSAttributedString.alloc().initWithString_attributes_(char, {"GSLayerIdAttrib": l.layerId, "GSShowBackgroundAttrib": True})
						elif l.className() == "GSControlLayer":
							char = chr( l.parent.unicodeChar() )
							A = NSAttributedString.alloc().initWithString_(char)
						else:
							raise ValueError
						string.appendAttributedString_(A)
					thisFont.currentTab.graphicView().textStorage().setText_(string)
		
