# MenuTitle: Build exclamdown and questiondown
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Builds inverted Spanish punctuation ¡¿ for mixed and upper case. Hold down COMMAND and SHIFT for all open fonts.
"""

from AppKit import NSEvent, NSEventModifierFlagShift, NSEventModifierFlagCommand
from GlyphsApp import Glyphs, GSGlyph, GSComponent

invertedGlyphNames = (
	"exclamdown",
	"questiondown",
	"exclamdown.case",
	"questiondown.case",
	"exclamdown.c2sc",
	"questiondown.c2sc",
	"exclamdown.c2pc",
	"questiondown.c2pc",
	"exclamdown.sc",
	"questiondown.sc",
	"exclamdown.pc",
	"questiondown.pc",
)


keysPressed = NSEvent.modifierFlags()
shiftKeyPressed = keysPressed & NSEventModifierFlagShift == NSEventModifierFlagShift
commandKeyPressed = keysPressed & NSEventModifierFlagCommand == NSEventModifierFlagCommand

verbose = False

Glyphs.clearLog()  # clears log in Macro window
print("Building Spanish inverted punctuation:\n")

if commandKeyPressed and shiftKeyPressed:
	theseFonts = Glyphs.fonts
else:
	theseFonts = [Glyphs.font, ]

for thisFont in theseFonts:
	if thisFont.filepath:
		print(f"📄 {thisFont.filepath.lastPathComponent().stringByDeletingLastDotSuffix()}")
	else:
		print(f"⚠️ unsaved document: {thisFont.familyName}")
	print()

	thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
	try:
		exclam = thisFont.glyphs["exclam"]
		question = thisFont.glyphs["question"]
		tabText = ""

		for invertedName in invertedGlyphNames:
			# determine original glyph for component:
			uprightName = invertedName[:invertedName.find("down")]
			if "." in invertedName:
				invertedParticles = invertedName.split(".")
				# adds suffix if necessary:
				if "case" not in invertedParticles[1:]:
					uprightName = ".".join([uprightName] + invertedParticles[1:])

			# if upright exists, build inverted mark:
			uprightGlyph = thisFont.glyphs[uprightName]
			if not uprightGlyph:
				if verbose:
					print(f"   🚫 {invertedName} not built, missing {uprightName} in font.")
			else:
				tabText += f"/{invertedName}"
				invertedGlyph = thisFont.glyphs[invertedName]
				if not invertedGlyph:
					print(f"   ⚙️ Creating glyph {invertedName} (did not exist)")
					invertedGlyph = GSGlyph(invertedName)
					thisFont.glyphs.append(invertedGlyph)

				for thisMaster in thisFont.masters:
					print(f"Ⓜ️ {thisMaster.name}")
					mID = thisMaster.id

					print(f"   Backing up {invertedName} in background...")
					invertedLayer = invertedGlyph.layers[mID]
					invertedLayer.swapForegroundWithBackground()
					invertedLayer.background.decomposeComponents()
					invertedLayer.shapes = None

					print(f"   Adding component {uprightName}...")
					invertedComponent = GSComponent(uprightName)
					invertedLayer.shapes.append(invertedComponent)
					# flip:
					print(f"   Flipping component {uprightName}...")
					t = list(invertedComponent.transform)
					t[0] = -1
					t[3] = -1
					t[5] = thisMaster.topHeightForLayer_(invertedLayer)
					t = tuple(t)
					invertedComponent.applyTransform(t)
					invertedComponent.automaticAlignment = True
					invertedLayer.updateMetrics()

		if tabText:
			thisFont.newTab(tabText)
	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ Error in script: Build exclamdown and questiondown\n")
		import traceback
		print(traceback.format_exc())
		print()
		raise e
	finally:
		thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
		print()
