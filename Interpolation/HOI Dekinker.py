# MenuTitle: HOI Dekinker
__doc__ = """
Goes through each axis and finds kinks of green (smooth) curve nodes halfway between neighboring key layers (masters and brace layers) along that axis. For every kink larger than the threshold, it adds an HOI intermediate point in the lower layer of the span. For two adjacent smooth nodes between two offcurves (offcurve-smooth-smooth-offcurve), both nodes are projected onto the line through the two offcurves. Nodes that already have HOI attributes are skipped and assumed to be fine. Processes the selected glyphs, or the whole font if no glyph is selected. Reports in the Macro Window, selects the nodes with HOI attributes in the affected glyphs and opens a tab with them. Requires Glyphs 4 or later. Sets Font Info → Document → File format version to the major version of Glyphs if it is lower.
"""

from GlyphsApp import Glyphs, Message
from mekkablue.hoi import dekinkGlyph, selectHOINodes

THRESHOLD = 0.92  # in units
minimumVersion = 4  # HOI exists since Glyphs 4, and since file format version 4
verbose = False  # if True, also report glyphs without changes


if Glyphs.versionNumber < minimumVersion:
	Message(title="HOI Dekinker", message=f"This script requires Glyphs {minimumVersion} or later.", OKButton=None)
else:
	font = Glyphs.font
	if not font:
		Message(title="HOI Dekinker", message="No font open.", OKButton=None)
	else:
		Glyphs.clearLog()
		Glyphs.showMacroWindow()
		print("Report for HOI Dekinker\n")
		print(f"Font: {font.familyName}")
		print(f"Axes: {', '.join(axis.axisTag for axis in font.axes)}")
		print(f"Threshold: {THRESHOLD}u")
		appVersion = int(Glyphs.versionNumber)
		if font.formatVersion < appVersion:
			print(f"☑️ Font Info → Document → File format version was {font.formatVersion}, setting it to {appVersion} for HOI.")
			font.formatVersion = appVersion
		print()
		glyphs = []
		for layer in font.selectedLayers:
			if layer.parent not in glyphs:
				glyphs.append(layer.parent)
		wholeFont = not glyphs
		if wholeFont:
			glyphs = list(font.glyphs)
			print(f"No glyphs selected, processing all {len(glyphs)} glyphs in the font.\n")
		total, skippedSpans, changedGlyphNames = 0, 0, []
		stats = {"spans": 0, "nodesWithHOI": 0}
		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				count, skipped = dekinkGlyph(glyph, font.axes, stats, threshold=THRESHOLD)
				total += count
				skippedSpans += skipped
				if count:
					changedGlyphNames.append(glyph.name)
				elif verbose:
					print(f"\t☑️ {glyph.name}: no kinks above threshold")
		finally:
			font.enableUpdateInterface()
		print(f"\nSummary: added {total} intermediate point{'s' if total != 1 else ''} in {len(changedGlyphNames)} of {len(glyphs)} glyph{'s' if len(glyphs) != 1 else ''}.")
		if changedGlyphNames:
			print(f"Changed glyphs: {', '.join(changedGlyphNames)}")
		if skippedSpans:
			print(f"⚠️ Skipped {skippedSpans} incompatible span{'s' if skippedSpans != 1 else ''}.")
		if changedGlyphNames:
			selectHOINodes(font, changedGlyphNames)
			font.newTab("/" + "/".join(changedGlyphNames))
		if total:
			Glyphs.showNotification("HOI Dekinker", f"Added {total} HOI intermediate points. Details in Macro Window.")
		else:
			if wholeFont:
				scope = f"In all {len(glyphs)} glyphs in font ‘{font.familyName}’"
			else:
				scope = f"In the {len(glyphs)} selected glyph{'s' if len(glyphs) != 1 else ''} of {len(font.glyphs)} total glyphs in font ‘{font.familyName}’"
			if not stats["spans"]:
				message = f"{scope}, no pair of neighboring key layers (masters or brace layers) was found along any axis, so there was nothing to check."
			else:
				message = f"{scope}, there were no kinks larger than the threshold {THRESHOLD}u."
				if stats["nodesWithHOI"]:
					message += f"\n\n{stats['nodesWithHOI']} smooth node{'s' if stats['nodesWithHOI'] != 1 else ''} already had HOI attributes and were skipped."
				if skippedSpans:
					message += f"\n\n{skippedSpans} span{'s' if skippedSpans != 1 else ''} with incompatible layers {'were' if skippedSpans != 1 else 'was'} skipped. Details in Macro Window."
			Message(title="HOI Dekinker", message=message, OKButton=None)
