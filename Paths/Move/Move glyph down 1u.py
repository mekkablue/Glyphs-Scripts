#MenuTitle: Move glyph down 1 unit
# -*- coding: utf-8 -*-
__doc__="""
Moves the current glyph(s) down by 1 unit.
Similar to ctrl-cmd-left/right.
Suggested shortcut: ctrl-cmd-downarrow.
"""

yDiff = -1


Font = Glyphs.font
selectedLayers = Font.selectedLayers

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

