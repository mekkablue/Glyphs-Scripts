from __future__ import print_function
#MenuTitle: New Tab with Orphaned Components
# -*- coding: utf-8 -*-
__doc__="""
Opens a new tab in the current font window containing all glyphs (of the current master) that have components that point to non-existent glyphs, i.e., no base glyphs.
"""

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
thisFontMasterID = thisFontMaster.id
orphanedGlyphNames = []

def thisGlyphHasOrphanedComponents( thisGlyph ):
	returnValue = False
	currentLayers = [l for l in thisGlyph.layers if l.associatedMasterId == thisFontMasterID ]
	for thisLayer in currentLayers:
		theseComponents = thisLayer.components
		if theseComponents:
			for thisComponent in theseComponents:
				if thisComponent.component is None:
					returnValue = True
	return returnValue

for thisGlyph in thisFont.glyphs:
	if thisGlyphHasOrphanedComponents( thisGlyph ):
		orphanedGlyphNames.append( thisGlyph.name )

if orphanedGlyphNames:
	Glyphs.clearLog()
	print("Found these glyphs with orphaned components:\n%s" % ", ".join(orphanedGlyphNames))
	tabString = "/%s" % "/".join(orphanedGlyphNames)
	thisFont.newTab( tabString )
else:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("No orphaned components found in this font master.")
