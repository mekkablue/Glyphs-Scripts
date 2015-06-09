#MenuTitle: New Tab with Unaligned Compounds for Every Master
# -*- coding: utf-8 -*-
__doc__="""
Opens a new tab with glyphs that have unaligned components. Inserts a new paragraph for a every master. Useful for finding misaligned accents.
"""

import GlyphsApp

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs			
tabString = ""

for thisFontMaster in thisFont.masters:
	tabString += "\n\n%s:\n" % thisFontMaster.name
	for thisGlyph in thisFont.glyphs:
		thisLayer = thisGlyph.layers[thisFontMaster.id]
		if len( thisLayer.components ) > 0 and len( thisLayer.paths ) == 0:
			everythingAligned = True
			for thisComponent in thisLayer.components:
				if thisComponent.disableAlignment:
					everythingAligned = False
			if not everythingAligned:
				tabString += "/%s" % thisGlyph.name
				
# opens new Edit tab:
from PyObjCTools.AppHelper import callAfter
callAfter( Glyphs.currentDocument.windowController().addTabWithString_, tabString[2:-1] )

