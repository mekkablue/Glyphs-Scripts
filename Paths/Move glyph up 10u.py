#MenuTitle: Move glyph up 10 units
"""
Moves the current glyph(s) up by 10 units.
Similar to shift-ctrl-cmd-left/right.
Suggested shortcut: shift-ctrl-cmd-uparrow.
"""

yDiff = 10

import GlyphsApp
Doc  = Glyphs.currentDocument
selectedLayers = Doc.selectedLayers()

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			thisNode.y += yDiff
	
	for thisComp in thisLayer.components:
		newPosition = NSPoint( thisComp.position.x, thisComp.position.y + yDiff  )
		thisComp.position = newPosition

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print "Moving up (x10)", thisLayer.parent.name
	process( thisLayer )

Font.enableUpdateInterface()

