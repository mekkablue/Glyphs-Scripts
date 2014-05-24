#MenuTitle: Center Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Center all selected glyphs inside their respective widths.
"""

import GlyphsApp
Font = Glyphs.font
selectedLayers = Font.selectedLayers

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	oldWidth = thisLayer.width
	thisLayer.LSB = ( thisLayer.LSB + thisLayer.RSB ) // 2
	thisLayer.width = oldWidth
	thisGlyph.endUndo()

Font.enableUpdateInterface()
print "Centered: %s" % (", ".join( [ l.parent.name for l in selectedLayers ] ))

