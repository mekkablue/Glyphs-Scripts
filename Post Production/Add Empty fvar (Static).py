# MenuTitle: Add Empty fvar (Static)
__doc__ = """
Adds an fvar table to static font files, with wght, wdth and ital axes that are pinned to the values of the font (min = default = max), and a single named instance. Weight and width come from the OS/2 table, italic from its italic bit. Useful for static fonts that have to behave like variable fonts in software that expects an fvar table. Needs the FontTools module.
"""

from os import path
from fontTools import ttLib
from fontTools.fontBuilder import FontBuilder
from GlyphsApp import Glyphs, GetOpenFile, Message

# OS/2 usWidthClass → wdth axis value (percent of normal)
WIDTH_CLASS_TO_PERCENT = {1: 50.0, 2: 62.5, 3: 75.0, 4: 87.5, 5: 100.0, 6: 112.5, 7: 125.0, 8: 150.0, 9: 200.0}


def addEmptyFvar(fontPath):
	"""Adds the pinned fvar table to the font file. Returns True if the file was saved."""
	print(f"📄 {fontPath}")
	if not path.isfile(fontPath):
		print("\t⚠️ File not found, skipping.")
		return False

	font = ttLib.TTFont(fontPath)
	if "fvar" in font:
		print("\t⚠️ Font already has an fvar table, skipping.")
		return False
	if "gvar" in font or "CFF2" in font:
		print("\t⚠️ Font has a gvar or CFF2 table, hence is not static. Skipping.")
		return False
	if "OS/2" not in font or "name" not in font:
		print("\t⚠️ Font has no OS/2 or name table, skipping.")
		return False

	nameTable = font["name"]
	styleName = nameTable.getDebugName(17) or nameTable.getDebugName(2)
	postScriptName = nameTable.getDebugName(6)
	if not styleName or not postScriptName:
		print("\t❌ Font has no style name (name ID 17 or 2) or no PostScript name (name ID 6), skipping.")
		return False

	os2 = font["OS/2"]
	axisValues = {
		"wght": float(os2.usWeightClass),
		"wdth": WIDTH_CLASS_TO_PERCENT.get(os2.usWidthClass, 100.0),
		"ital": 1.0 if os2.fsSelection & 1 else 0.0,
	}
	axes = (
		("wght", axisValues["wght"], axisValues["wght"], axisValues["wght"], "Weight"),
		("wdth", axisValues["wdth"], axisValues["wdth"], axisValues["wdth"], "Width"),
		("ital", axisValues["ital"], axisValues["ital"], axisValues["ital"], "Italic"),
	)
	instance = {"location": axisValues, "stylename": styleName, "postscriptfontname": postScriptName}
	FontBuilder(font=font).setupFvar(axes, instances=[instance])
	font.save(fontPath, reorderTables=False)
	print(f"\t💾 Saved with wght={axisValues['wght']:g}, wdth={axisValues['wdth']:g}, ital={axisValues['ital']:g}, instance ‘{styleName}’.")
	return True


if Glyphs.versionNumber < 3.2:
	Message(
		title="Version Error",
		message="This script requires app version 3.2 or later.",
		OKButton=None,
	)
else:
	Glyphs.clearLog()
	print("Report for Add Empty fvar (Static)\n")
	chosenPaths = GetOpenFile(
		message="Choose the static font files that need an fvar table.",
		allowsMultipleSelection=True,
		filetypes=["ttf", "otf", "woff", "woff2"],
	)
	if not chosenPaths:
		print("⚠️ No file chosen.")
	else:
		fontPaths = list(chosenPaths) if isinstance(chosenPaths, (list, tuple)) else [chosenPaths]
		savedCount = 0
		for i, fontPath in enumerate(fontPaths):
			print(f"⚙️ Font {i + 1} of {len(fontPaths)}:")
			if addEmptyFvar(fontPath):
				savedCount += 1
		print(f"\n✅ Done. Added fvar to {savedCount} of {len(fontPaths)} files.")
		Glyphs.showNotification("Add Empty fvar (Static)", f"Added fvar to {savedCount} of {len(fontPaths)} files. Details in Macro Window.")
