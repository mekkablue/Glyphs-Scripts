#MenuTitle: Glyph Shaker
"""Goes through all selected glyphs and slaps each of their nodes around a bit."""

import random
random.seed()

selectedLayers = Glyphs.font.selectedLayers

for thisLayer in selectedLayers:
    for thisPath in thisLayer.paths:
        for thisNode in thisPath.nodes:
            thisNode.x += random.randint( -50, 50 )