#MenuTitle: Decompose Components in Background
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
Decomposes components in the Background.
"""

thisFont = Glyphs.font # frontmost font

def process( thisLayer ):
	if thisLayer.isKindOfClass_(GSBackgroundLayer):
		background = thisLayer
	else:
		background = thisLayer.background
	
	if not background:
		print("  Could not access background layer '%s'." % thisLayer.name)
	elif background.components:
		compCount = len(background.components)
		print("  Decomposed %i component%s in background." % (
			compCount,
			"" if compCount==1 else "s",
			))
		background.decomposeComponents()

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in thisFont.selectedLayers:
	thisGlyph = thisLayer.parent
	print("Processing", thisGlyph.name)
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
