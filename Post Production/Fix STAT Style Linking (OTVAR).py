# MenuTitle: Fix STAT Style Linking (OTVAR)
__doc__ = """
Run this right after a variable font export. In STAT, turns the Format 1 axis values of wght=400 and ital=0 (or, if there is no ital axis, slnt=0) into Format 3 (style linking), makes them elidable (Flags=2), and sets the linked values wght=700, ital=1, slnt=most negative value of the axis.
"""

from os import path
from fontTools import ttLib
from otvarLib import currentOTVarExportPath, otVarFileName
from fixStyleLinking import fixStyleLinking
from GlyphsApp import Glyphs, INSTANCETYPEVARIABLE, Message


def exportFolderOfInstance(thisFont, instance):
	# same lookup as in Add Empty DSIG (OTVAR): instance parameter first, then font-wide
	for owner in (instance, thisFont):
		parameter = owner.customParameterActiveForKey_("Export Folder")
		if parameter:
			return parameter.value
	return None


if Glyphs.versionNumber < 3.2:
	Message(
		title="Version Error",
		message="This script requires app version 3.2 or later. In Glyphs > Settings > Updates, activate Cutting Edge Versions, and check for updates.",
		OKButton=None,
	)
elif not Glyphs.font:
	Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
elif not currentOTVarExportPath():
	Message(title="No Export Path", message="Could not determine the folder of the most recent variable font export.", OKButton=None)
else:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("Report: Fix STAT Style Linking")

	suffixes = ["ttf"]
	for suffix in ("woff", "woff2"):
		if Glyphs.defaults[f"GXExport{suffix.upper()}"]:
			suffixes.append(suffix)
	print(f"- suffixes: {', '.join(suffixes)}")

	thisFont = Glyphs.font  # frontmost font
	currentExportPath = currentOTVarExportPath()
	print(f"- path: {currentExportPath}")

	variableFontSettings = [instance for instance in thisFont.instances if instance.type == INSTANCETYPEVARIABLE]
	if not variableFontSettings:
		variableFontSettings = [None]

	changedCount = 0
	fileCount = 0
	for variableFontExport in variableFontSettings:
		exportFolder = exportFolderOfInstance(thisFont, variableFontExport) if variableFontExport else None
		folderPath = path.join(currentExportPath, exportFolder) if exportFolder else currentExportPath
		for suffix in suffixes:
			fontPath = path.join(folderPath, otVarFileName(thisFont, thisInstance=variableFontExport, suffix=suffix))
			print(f"\n📄 {fontPath}")
			if not path.isfile(fontPath):
				print("❌ No font file found. Skipping.")
				continue
			fileCount += 1
			font = ttLib.TTFont(fontPath)
			if fixStyleLinking(font):
				font.save(fontPath, reorderTables=False)
				changedCount += 1
				print("💾 Saved.")
			else:
				print("🤷🏻‍♀️ No changes made. File left unchanged.")

	print(f"\n✅ Done. Changed {changedCount} of {fileCount} files.")
	Glyphs.showNotification("Fix STAT Style Linking", f"Changed {changedCount} of {fileCount} files. Details in Macro Window.")
