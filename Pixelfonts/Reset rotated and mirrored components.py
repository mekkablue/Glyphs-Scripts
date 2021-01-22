#MenuTitle: Reset Rotated and Mirrored Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Looks for mirrored and rotated components and resets them to their original orientation.
"""
from Foundation import NSPoint

Font = Glyphs.font
selectedLayers = Font.selectedLayers

grid = Font.grid

for l in selectedLayers:
	thisGlyph = l.parent
	glyphName = thisGlyph.name
	
	thisGlyph.beginUndo()
	didChange = False
	for comp in l.components:
		transform = comp.transform # this is computed in Glyhs 3. When dropping support for Glyphs 2, use the position/scale/rotate API
		if transform[0] != 1.0 or transform[3] != 1.0:
			position = comp.position
			if transform[0] < 0:
				position.x -= grid
			if transform[3] < 0:
				position.y -= grid
			comp.transform = (1, 0, 0, 1, position.x, position.y)
			didChange = True
	if didChange:
		print("Fixed components in %s ..." % glyphName)

	thisGlyph.endUndo()

