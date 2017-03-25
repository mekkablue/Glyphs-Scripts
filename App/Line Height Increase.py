#MenuTitle: Increase Line Height
# -*- coding: utf-8 -*-
__doc__="""
Increase the Edit View line height.
"""

Font = Glyphs.font # frontmost font
parameterName = "EditView Line Height"

# set default height:
if not Font.customParameters[parameterName]:
	Font.customParameters[parameterName] = 1200

lineheight = Font.customParameters[parameterName]

if not lineheight > Font.upm*10:
	lineheight *= 1.25
	lineheight = round(lineheight)
	Font.customParameters[parameterName] = lineheight
	if Font.currentTab:
		Font.currentTab.forceRedraw()
else:
	Message("Line Height Error", "The line height exceeds the UPM more than tenfold already. Stop it now.", OKButton=None)