#MenuTitle: Center Glyphs
"""Center all selected glyphs inside their respective widths."""

import GlyphsApp
Font = Glyphs.font
selectedLayers = Font.selectedLayers

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisLayer.beginUndo()
	oldWidth = thisLayer.width
	thisLayer.LSB = ( thisLayer.LSB + thisLayer.RSB ) // 2
	thisLayer.width = oldWidth
	thisLayer.endUndo()

Font.enableUpdateInterface()
print "Centered: %s" % (", ".join( [ l.parent.name for l in selectedLayers ] ))

