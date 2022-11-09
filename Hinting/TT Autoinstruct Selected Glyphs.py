#MenuTitle: TT Autoinstruct Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Automatically add Glyphs TT instructions to the selected glyphs in the selected master. (Should be the first master.) Attention: this is NOT Werner Lemberg's ttfAutohint, but the horizontal ClearType hints that the TT Instruction tool would add.
"""

from GlyphsApp import TTANCHOR, TTSTEM, TTALIGN, TTINTERPOLATE, TTDIAGONAL, TTDELTA
from Foundation import NSClassFromString
Glyphs.registerDefault("com.mekkablue.ttAutoinstructSelectedGlyphs.alwaysUseNoStem", 1)
shouldSetStemsToNoStem = Glyphs.defaults["com.mekkablue.ttAutoinstructSelectedGlyphs.alwaysUseNoStem"]

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def setHintsToNoStem(thisLayer):
	returnValue = False
	count = 0
	for thisHint in thisLayer.hints:
		if thisHint.type == TTSTEM: # TT stem
			count += 1
			thisHint.setStem_(-1)
			returnValue = True
	if count:
		print("   %i TT Stem Hint%s set to ‘No Stem’." % (
			count,
			"" if count == 1 else "s",
			))
	return returnValue

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print("TT Autoinstruct: %s" % thisFont.familyName)
thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	Tool = NSClassFromString("GlyphsToolTrueTypeInstructor").alloc().init()
	if Tool:
		Tool.autohintLayers_(selectedLayers)
		for thisLayer in selectedLayers:
			hintCount = len([h for h in thisLayer.hints if h.type in (TTANCHOR, TTSTEM, TTALIGN, TTINTERPOLATE, TTDIAGONAL, TTDELTA)])
			print("\n🔠 %s\n   Layer ‘%s’ has %i TT instruction%s." % (
				thisLayer.parent.name,
				thisLayer.name,
				hintCount,
				"" if hintCount == 1 else "s",
				))
			if shouldSetStemsToNoStem:
				setHintsToNoStem(thisLayer)
	else:
		Message("TT Autoinstruct Error", "The TT Instructor Tool could not be accessed.", OKButton=None)

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e

finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View

# Floating notification:
Glyphs.showNotification(
	"TT-Autoinstructed %s" % (thisFont.familyName),
	"Processed %i glyph%s, details in Macro Window." % (
		len(selectedLayers),
		"" if len(selectedLayers) == 0 else "s",
		),
	)
print("\nProcessed %i glyph%s." % (
	len(selectedLayers),
	"" if len(selectedLayers) == 0 else "s",
	))
