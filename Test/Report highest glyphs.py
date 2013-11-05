#MenuTitle: Report highest glyphs
# -*- coding: utf-8 -*-
"""Reports a list of glyph names to the Macro Window in the order of the highest bounding boxes. Restricts itself to the selected glyphs."""

import GlyphsApp

Font = Glyphs.font
selectedLayers = Font.selectedLayers

Glyphs.clearLog()
Glyphs.showMacroWindow()
print "%s (master: %s)" % (Font.familyName, Font.selectedFontMaster.name)
print "Highest selected glyphs:"

sortedNameHeightPairs = sorted([[l.parent.name,  l.bounds.origin.y + l.bounds.size.height] for l in selectedLayers], key=lambda x: -x[1])
for thisLayerPair in sortedNameHeightPairs:
	print "- %s: %.1f" % ( thisLayerPair[0], thisLayerPair[1] )
