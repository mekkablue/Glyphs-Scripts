#MenuTitle: Set blueFuzz to zero for master instances
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds blueFuzz custom parameter with value 0 for instances that are the same as a master.
"""

thisFont = Glyphs.font # frontmost font
axesValuesOfAllMasters = [m.axes for m in thisFont.masters]
Glyphs.clearLog() # clears log in Macro window

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisInstance in [i for i in thisFont.instances if i.type==INSTANCETYPESINGLE]:
		if thisInstance.axes in axesValuesOfAllMasters:
			thisInstance.customParameters["blueFuzz"] = 0
			print(f"ℹ️ {thisInstance.name}: blueFuzz 0")
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Set blueFuzz to zero for master instances\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
