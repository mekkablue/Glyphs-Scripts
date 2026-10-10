# MenuTitle: HOI Cleaner
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes all HOI (higher-order interpolation) attributes from all nodes in all layers of the frontmost font, reports in the Macro Window and opens a tab with the affected glyphs. Requires Glyphs 4.
"""

from GlyphsApp import Glyphs, Message

if Glyphs.versionNumber < 4:
	Message(title="HOI Cleaner", message="This script requires Glyphs 4 or later.", OKButton=None)
else:
	font = Glyphs.font
	if not font:
		Message(title="HOI Cleaner", message="No font open.", OKButton=None)
	else:
		Glyphs.clearLog()
		Glyphs.showMacroWindow()
		print("Report for HOI Cleaner\n")
		print(f"Font: {font.familyName}\n")
		totalNodes, glyphNames = 0, []
		font.disableUpdateInterface()
		try:
			for glyph in font.glyphs:
				glyphCount = 0
				for layer in glyph.layers:
					for path in layer.paths:
						for node in path.nodes:
							if node.attributes["hoi"]:
								del node.attributes["hoi"]
								glyphCount += 1
				if glyphCount:
					totalNodes += glyphCount
					glyphNames.append(glyph.name)
					print(f"\t✅ {glyph.name}: removed HOI from {glyphCount} node{'s' if glyphCount != 1 else ''}")
		finally:
			font.enableUpdateInterface()
		if not totalNodes:
			print("☑️ No HOI attributes found.")
		print(f"\nSummary: removed HOI from {totalNodes} node{'s' if totalNodes != 1 else ''} in {len(glyphNames)} glyph{'s' if len(glyphNames) != 1 else ''}.")
		if glyphNames:
			font.newTab("/" + "/".join(glyphNames))
		Glyphs.showNotification("HOI Cleaner", f"Removed HOI from {totalNodes} nodes. Details in Macro Window.")
