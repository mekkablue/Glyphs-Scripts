# MenuTitle: Remove Global Guides in Current Master
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Deletes all global guidelines in the current master.
"""
from mekkablue import clearGuides, guidesOf
from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font
thisFontMaster = thisFont.selectedFontMaster  # active master
numberOfGuidelines = len(guidesOf(thisFontMaster))
clearGuides(thisFontMaster)

print("Deleted %i global guides in Font %s, Master %s." % (numberOfGuidelines, thisFont.familyName, thisFontMaster.name))
