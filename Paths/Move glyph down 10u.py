#MenuTitle: Move glyph down 10 units
"""
Moves the current glyph(s) down by 10 units.
Similar to shift-ctrl-cmd-left/right.
Suggested shortcut: shift-ctrl-cmd-downarrow.
"""

yDiff = -10

import GlyphsApp
Doc  = Glyphs.currentDocument
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
	thisLayer.setDisableUpdates()
	print "Moving down (x10)", thisLayer.parent.name
	process( thisLayer )
	thisLayer.setEnableUpdates()
