#MenuTitle: Reset Alternate Glyph Widths
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Sets the width of selected .ss01 (or any other extension) widths in the font to the width of their base glyphs. E.g. A.ss01 will have the same width as A.
"""

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers

def resetWidth( thisLayer, thisName ):
	if thisLayer is None: 
		print("> couldn't get layer of <%s> " % thisName)
		return
	baseGlyphName = thisName[:thisName.find(".")]
	baseGlyph = Font.glyphs[ baseGlyphName ]
	if baseGlyph is None: 
		print("> couldn't find a base glyph for <%s> " % thisName)
		return
	baseLayer = baseGlyph.layers[ FontMaster.id ]
	baseWidth = baseLayer.width
	thisLayer.width = baseWidth
	return baseWidth

Font.disableUpdateInterface()
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		thisGlyphName = thisGlyph.name
		if "." in thisGlyphName:
			if Glyphs.versionNumber >= 3:
				# Glyphs 3 code
				# thisLayer.glyph().beginUndo() # undo grouping causes crashes
			else:
				# Glyphs 2 code
				# thisLayer.beginUndo() # undo grouping causes crashes
			try:
				print("Resetting width of %s to %.0f." % ( thisGlyphName, resetWidth( thisLayer, thisGlyphName ) ))
			except:
				print("> ERROR, couldn't reset <%s>" % (thisGlyphName))
			if Glyphs.versionNumber >= 3:
				# Glyphs 3 code
				# thisLayer.glyph().endUndo() # undo grouping causes crashes
			else:
				# Glyphs 2 code
				# thisLayer.endUndo() # undo grouping causes crashes
			
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
	
finally:
	Font.enableUpdateInterface() # re-enables UI updates in Font View

