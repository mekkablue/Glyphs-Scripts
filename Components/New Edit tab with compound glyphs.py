#MenuTitle: New Edit tab with compound glyphs
# -*- coding: utf-8 -*-
__doc__="""
Opens a new Edit tab with all glyphs which contain the currently selected glyphs as a component. E.g., you have A selected, and it will give you an Edit tab with A, Adieresis, Aacute, etc. Useful for editing anchor positions.
"""

import GlyphsApp

Doc = Glyphs.currentDocument
Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers

editString = ""

for thisLayer in selectedLayers:
	thisGlyphName = thisLayer.parent.name
	print "Compounds with %s:" % thisGlyphName
	compoundList = [ g.name for g in Font.glyphs if thisGlyphName in [ c.componentName for c in g.layers[ FontMaster.id ].components ]]
	editString += "\n/" + thisGlyphName + "/space/" + "/".join( compoundList )

editString = editString.lstrip()

Doc.windowController().performSelectorOnMainThread_withObject_waitUntilDone_( "addTabWithString:", editString, True )
