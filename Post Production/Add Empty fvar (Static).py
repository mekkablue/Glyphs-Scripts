# MenuTitle: Add Empty fvar (Static)
__doc__ = """
Adds a completely empty fvar table to static font files: no axes, no instances. Useful for static fonts that have to carry an fvar table. Needs the FontTools module.
"""

from os import path
from fontTools import ttLib
from GlyphsApp import Glyphs, GetOpenFile, Message


def addEmptyFvar(fontPath):
	"""Adds an empty fvar table to the font file. Returns True if the file was saved."""
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

	fvar = ttLib.newTable("fvar")
	fvar.axes = []
	fvar.instances = []
	font["fvar"] = fvar
	font.save(fontPath, reorderTables=False)
	print("\t💾 Saved with empty fvar table.")
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
