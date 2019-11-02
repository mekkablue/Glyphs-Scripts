#MenuTitle: TT Autoinstruct Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Automatically add Glyphs TT instructions to the selected glyphs in the selected master. (Should be the first master.) Attention: this is NOT Werner Lemberg's ttfAutohint, but the horizontal ClearType hints that the TT Instruction tool would add.
"""

from Foundation import NSClassFromString

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def setHintsToNoStem( thisLayer ):
	returnValue = False
	for thisHint in thisLayer.hints:
		if thisHint.type == 3: # TT stem
			thisHint.setStem_(-1)
			returnValue = True
	return returnValue

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

Tool = NSClassFromString("GlyphsToolTrueTypeInstructor").alloc().init()
if Tool:
	Tool.autohintLayers_(selectedLayers)
	for thisLayer in selectedLayers:
		setHintsToNoStem( thisLayer )
else:
	Message("TT Autoinstruct Error", "The TT Instructor Tool could not be accessed.", OKButton=None)

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
