#MenuTitle: Move glyph down 1 unit
"""
Moves the current glyph(s) down by 1 unit.
Similar to ctrl-cmd-left/right.
Suggested shortcut: ctrl-cmd-downarrow.
"""

yDiff = -1

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
	print "Moving down", thisLayer.parent.name
	process( thisLayer )

Font.enableUpdateInterface()

