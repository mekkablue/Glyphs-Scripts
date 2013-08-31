#MenuTitle: Center Glyphs
"""Center all selected glyphs inside their respective widths."""

import GlyphsApp
Font = Glyphs.font
selectedLayers = Font.selectedLayers

for thisLayer in selectedLayers:
	
	thisLayer.setDisableUpdates()
	
	oldWidth = thisLayer.width
	thisLayer.LSB = ( thisLayer.LSB + thisLayer.RSB ) // 2
	thisLayer.width = oldWidth
	
	thisLayer.setEnableUpdates()

print "Centered:", ", ".join( [ thisLayer.parent.name for thisLayer in selectedLayers ] )

