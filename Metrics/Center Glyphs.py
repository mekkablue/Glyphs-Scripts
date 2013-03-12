#MenuTitle: Center Glyphs
"""Center all selected glyphs inside their respective widths."""

import GlyphsApp
selectedLayers = Glyphs.currentDocument.selectedLayers()

for thisLayer in selectedLayers:

	Font.disableUpdateInterface()
	
	oldWidth = thisLayer.width
	thisLayer.LSB = ( thisLayer.LSB + thisLayer.RSB ) // 2
	thisLayer.width = oldWidth
	
	Font.enableUpdateInterface()

print "Centered:", ", ".join( [ thisLayer.parent.name for thisLayer in selectedLayers ] )

