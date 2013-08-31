#MenuTitle: Move glyph up 10 units
"""
Moves the current glyph(s) up by 10 units.
Similar to shift-ctrl-cmd-left/right.
Suggested shortcut: shift-ctrl-cmd-uparrow.
"""

yDiff = 10

import GlyphsApp
Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			thisNode.y += yDiff
	
	for thisComp in thisLayer.components:
		newPosition = NSPoint( thisComp.position.x, thisComp.position.y + yDiff  )
		thisComp.position = newPosition

for thisLayer in selectedLayers:
	print "Moving up (x10)", thisLayer.parent.name
	thisLayer.setDisableUpdates()
	process( thisLayer )
	thisLayer.setEnableUpdates()
