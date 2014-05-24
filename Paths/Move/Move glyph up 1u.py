#MenuTitle: Move glyph up 1 unit
# -*- coding: utf-8 -*-
__doc__="""
Moves the current glyph(s) up by 1 unit.
Similar to ctrl-cmd-left/right.
Suggested shortcut: ctrl-cmd-uparrow.
"""

yDiff = 1

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

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print "Moving up", thisLayer.parent.name
	process( thisLayer )

Font.enableUpdateInterface()

