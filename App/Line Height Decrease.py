# MenuTitle: Decrease Line Height
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Decrease the Edit View line height.
"""

from GlyphsApp import Glyphs, Message

Font = Glyphs.font  # frontmost font
parameterName = "EditView Line Height"

# set default height:
if not Font.customParameters[parameterName]:
	Font.customParameters[parameterName] = 1200

lineheight = Font.customParameters[parameterName]

if not lineheight < 100.0:
	lineheight *= 0.8
	lineheight = round(lineheight)
	Font.customParameters[parameterName] = lineheight
	if Font.currentTab:
		Font.currentTab.forceRedraw()
else:
	Message(title="Line Height Error", message="The line height is already below 100 units. Cannot decrease any further.", OKButton=None)
