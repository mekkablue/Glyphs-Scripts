# MenuTitle: Toggle Macro Window Separator
__doc__ = """
Toggles the separator position in the Macro Window between 80% and 20%.
"""

from mekkablue import macroDividerPosition, setMacroDivider


currentPos = macroDividerPosition()
if currentPos is not None:
	if currentPos > 0.5:
		newPos = 0.2
	else:
		newPos = 0.8
	setMacroDivider(newPos)
