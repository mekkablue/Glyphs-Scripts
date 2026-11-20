# MenuTitle: Decrease Line Height
__doc__ = """
Decrease the Edit View line height.
"""

from GlyphsApp import Glyphs, Message

Font = Glyphs.font  # frontmost font
parameterName = "EditView Line Height"

if Font:
	# set default height:
	if not Font.customParameters[parameterName]:
		Font.customParameters[parameterName] = 1200

	lineheight = Font.customParameters[parameterName]

	if not lineheight < 100.0:
		lineheight *= 0.8
		lineheight = round(lineheight)
		Font.customParameters[parameterName] = lineheight
		if Font.currentTab:
			if Glyphs.versionNumber >= 4.0:
				Font.currentTab.redraw()
			else:
				Font.currentTab.forceRedraw()
			Font.currentTab.reflow()
	else:
		Message(title="Line Height Error", message="The line height is already below 100 units. Cannot decrease any further.", OKButton=None)
