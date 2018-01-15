#MenuTitle: New Tab with Selected Glyph Combinations
# -*- coding: utf-8 -*-
__doc__="""
Opens a new tab with all possible combinations of currently selected glyphs.
"""


from PyObjCTools.AppHelper import callAfter

Doc = Glyphs.currentDocument
Font = Glyphs.font
selectedLayers = Font.selectedLayers

namesOfSelectedGlyphs = [ "/%s" % l.parent.name for l in selectedLayers if hasattr(l.parent, 'name')]
editString = ""

for leftGlyphName in namesOfSelectedGlyphs:
	for rightGlyphName in namesOfSelectedGlyphs:
		editString += ( leftGlyphName + rightGlyphName )
	editString += ( leftGlyphName + "\n" )

# in case last line fails, the text is in the macro window:
Glyphs.clearLog() # clears macro window log
print editString

# opens new Edit tab:
callAfter( Doc.windowController().addTabWithString_, editString )
