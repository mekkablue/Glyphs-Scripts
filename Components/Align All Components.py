#MenuTitle: Align All Components
# -*- coding: utf-8 -*-
__doc__="""
Fakes auto-alignment in glyphs that cannot be auto-aligned.
"""



thisFont = Glyphs.font # frontmost font
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisLayer ):
	advance = 0.0
	thisFontMasterID = thisLayer.associatedFontMaster().id
	for thisComponent in thisLayer.components:
		thisComponent.position = NSPoint( advance, 0.0 )
		advance += thisComponent.component.layers[thisFontMasterID].width
	thisLayer.width = advance

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Aligning components in:", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
