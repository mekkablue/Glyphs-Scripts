#MenuTitle: Set Variable Style Names
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds Style Names for variable fonts to instances in Font Info > Exports, and makes an informed guess as for their value. Useful if you split your static family in subfamilies (e.g. by optical size or by width), and as a result, you end up with repeating style names (e.g. multiple Mediums).
"""

thisFont = Glyphs.font # frontmost font
thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	thisFont = Glyphs.font
	for thisInstance in thisFont.instances:
		if thisInstance.type == INSTANCETYPEVARIABLE:
			continue
		part1 = thisInstance.preferredFamily.replace(thisFont.familyName, "").strip()
		part2 = thisInstance.name.strip()
		if part1 and part2 == "Regular":
			thisInstance.variableStyleName = part1
		else:
			thisInstance.variableStyleName = f"{part1} {part2}".strip()
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Set Variable Style Names\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
