# MenuTitle: HOI Cleaner
__doc__ = """
Removes all HOI (higher-order interpolation) attributes from all nodes in all layers of the selected glyphs (the parents of the selected layers) in the frontmost font, or of all glyphs if no glyph is selected. Reports in the Macro Window and opens a tab with the affected glyphs. Requires Glyphs 4 or later and a font with Font Info → Document → File format version 4 or later.
"""

from GlyphsApp import Glyphs, Message

minimumVersion = 4  # HOI exists since Glyphs 4, and since file format version 4

if Glyphs.versionNumber < minimumVersion:
	Message(title="HOI Cleaner", message=f"This script requires Glyphs {minimumVersion} or later.", OKButton=None)
else:
	font = Glyphs.font
	if not font:
		Message(title="HOI Cleaner", message="No font open.", OKButton=None)
	elif font.formatVersion < minimumVersion:
		Message(
			title="HOI Cleaner",
			message=f"The file format version of ‘{font.familyName}’ is {font.formatVersion}, which cannot contain HOI attributes (they need version {minimumVersion} or later). Nothing to clean. "
			"The file format version is set in Font Info → Document → File format version.",
			OKButton=None,
		)
	else:
		Glyphs.clearLog()
		Glyphs.showMacroWindow()
		print("Report for HOI Cleaner\n")
		print(f"Font: {font.familyName}\n")
		glyphs = []
		for selectedLayer in font.selectedLayers:
			glyph = selectedLayer.parent
			if glyph is not None and glyph not in glyphs:
				glyphs.append(glyph)
		if glyphs:
			print(f"Cleaning {len(glyphs)} selected glyph{'s' if len(glyphs) != 1 else ''} only.\n")
		else:
			glyphs = font.glyphs
			print("No glyph selection, cleaning all glyphs.\n")
		totalNodes, scannedNodes, glyphNames = 0, 0, []
		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				glyphCount = 0
				for layer in glyph.layers:
					for path in layer.paths:
						for node in path.nodes:
							scannedNodes += 1
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
		else:
			if not len(glyphs):
				reason = "The font has no glyphs."
			elif not scannedNodes:
				reason = f"None of the {len(glyphs)} glyphs has any nodes in any layer."
			else:
				reason = f"None of the {scannedNodes} nodes in the {len(glyphs)} glyphs has HOI attributes."
			Message(title="HOI Cleaner", message=f"Nothing was removed in font ‘{font.familyName}’. {reason}", OKButton=None)
