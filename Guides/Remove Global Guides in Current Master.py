#MenuTitle: Remove Global Guides in Current Master
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Deletes all global guidelines in the current master.
"""

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
numberOfGuidelines = len( thisFontMaster.guideLines )
thisFontMaster.guideLines = []

print("Deleted %i global guides in Font %s, Master %s." % ( numberOfGuidelines, thisFont.familyName, thisFontMaster.name ))
