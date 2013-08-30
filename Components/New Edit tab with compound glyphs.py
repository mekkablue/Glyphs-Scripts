#MenuTitle: New Edit tab with compound glyphs
# -*- coding: utf-8 -*-
# this is nativly avalilabble, could be removed
"""Opens a new Edit tab with all glyphs which contain the currently selected glyphs as a component. E.g., you have A selected, and it will give you an Edit tab with A, Adieresis, Aacute, etc. Useful for editing anchor positions."""

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
FontMaster = Doc.selectedFontMaster()
selectedLayers = Doc.selectedLayers()
Glyphs.clearLog()

editString = ""

for thisLayer in selectedLayers:
	thisGlyphName = thisLayer.parent.name
	print "Compounds with %s:" % thisGlyphName
	compoundList = [ g.name for g in Font.glyphs if thisGlyphName in [ c.componentName for c in g.layers[ FontMaster.id ].components ]]
	editString += "\n/" + thisGlyphName + "/space/" + "/".join( compoundList )

editString = editString.lstrip()

# danger, can hang Glyphs.app:
# Doc.windowController().addTabWithString_( editString )
# so instead, script reports to the Macro window:

Glyphs.showMacroWindow()
print editString
