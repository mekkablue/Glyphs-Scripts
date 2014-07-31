#MenuTitle: Delete global guidelines
# -*- coding: utf-8 -*-
__doc__="""
Deletes all global guidelines in the current master.
"""

import GlyphsApp


thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
numberOfGuidelines = len( thisFontMaster.guideLines )

print "Deleting %i global guidelines in Font %s, Master %s." % ( numberOfGuidelines, thisFont.familyName, thisFontMaster.name )

for guidelineNumber in range(numberOfGuidelines)[::-1]:
	del thisFontMaster.guideLines[guidelineNumber]