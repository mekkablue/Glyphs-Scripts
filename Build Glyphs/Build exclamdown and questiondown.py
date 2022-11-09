#MenuTitle: Build exclamdown and questiondown
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Builds inverted Spanish punctuation ¡¿ for mixed and upper case.
"""

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

thisFont = Glyphs.font # frontmost font
Glyphs.clearLog() # clears log in Macro window

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	exclam = thisFont.glyphs["exclam"]
	question = thisFont.glyphs["question"]

	for invertedName in invertedGlyphNames:
		# determine original glyph for component:
		uprightName = invertedName[:invertedName.find("down")]
		if "." in invertedName:
			invertedParticles = invertedName.split(".")
			# adds suffix if necessary:
			if not "case" in invertedParticles[1:]:
				uprightName = ".".join([uprightName] + invertedParticles[1:])

		# if upright exists, build inverted mark:
		uprightGlyph = thisFont.glyphs[uprightName]
		if not uprightGlyph:
			print("🚫 Not in font: %s. No %s built." % (uprightName, invertedName))
		else:
			invertedGlyph = thisFont.glyphs[invertedName]
			if not invertedGlyph:
				print("⚙️ Creating glyph %s (did not exist)" % invertedName)
				invertedGlyph = GSGlyph(invertedName)
				thisFont.glyphs.append(invertedGlyph)

			for thisMaster in thisFont.masters:
				print("Ⓜ️ %s" % thisMaster.name)
				mID = thisMaster.id

				print("   Backing up %s in background..." % invertedName)
				invertedLayer = invertedGlyph.layers[mID]
				invertedLayer.swapForegroundWithBackground()
				invertedLayer.background.decomposeComponents()
				invertedLayer.shapes = None

				print("   Adding component %s..." % uprightName)
				invertedComponent = GSComponent(uprightName)
				invertedLayer.shapes.append(invertedComponent)
				# flip:
				print("   Flipping component %s..." % uprightName)
				t = list(invertedComponent.transform)
				t[0] = -1
				t[3] = -1
				t = tuple(t)
				invertedComponent.applyTransform(t)
				invertedComponent.setDisableAlignment_(False)
				invertedLayer.updateMetrics()

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Build exclamdown and questiondown\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
