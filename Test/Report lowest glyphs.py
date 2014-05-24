#MenuTitle: Report lowest glyphs
# -*- coding: utf-8 -*-
__doc__="""
Reports a list of glyph names to the Macro Window in the order of the lowest bounding boxes. Restricts itself to the selected glyphs.
"""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers

Glyphs.clearLog()
Glyphs.showMacroWindow()
print "%s (master: %s)" % (Font.familyName, Font.selectedFontMaster.name)
print "Lowest selected glyphs:"

sortedNameHeightPairs = sorted([ [l.parent.name,  l.bounds.origin.y] for l in selectedLayers], key=lambda x: x[1])
for thisLayerPair in sortedNameHeightPairs:
	print "- %s: %.1f" % ( thisLayerPair[0], thisLayerPair[1] )
