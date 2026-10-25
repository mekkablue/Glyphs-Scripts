# MenuTitle: Add Empty DSIG (OTVAR)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Run this after you export a Variable Font (TTF) and it will add an empty DSIG table. Necessary to pass the MyFonts onboarding of OTVAR TTFs.
"""

from os import path
from fontTools import ttLib
from otvarLib import currentOTVarExportPath, otVarFileName
from GlyphsApp import Glyphs, GetOpenFile, INSTANCETYPEVARIABLE, Message


def addEmptyDSIG(fontpath):
	print(f"📄 {fontpath}")
	if not path.isfile(fontpath):
		print("⚠️ File not found, skipping.")
		return
	font = ttLib.TTFont(file=fontpath)
	dsig = ttLib.ttFont.newTable("DSIG")
	dsig.ulVersion = 1
	dsig.usFlag = 0
	dsig.usNumSigs = 0
	dsig.signatureRecords = []
	font["DSIG"] = dsig
	font.save(fontpath, reorderTables=False)
	print("💾 Saved file.")


def exportFolderOfInstance(thisFont, instance):
	# same lookup as in Variable Font Test HTML: instance parameter first, then font-wide
	for owner in (instance, thisFont):
		parameter = owner.customParameterActiveForKey_("Export Folder")
		if parameter:
			return parameter.value
	return None


if Glyphs.versionNumber < 3.2:
	Message(
		title="Version Error",
		message="This script requires app version 3.2 or later.",
		OKButton=None,
	)
else:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("Adding DSIG for current font")

	thisFont = Glyphs.font  # frontmost font
	currentExportPath = currentOTVarExportPath()
	print(f"🖥️ Export path: {currentExportPath}")

	variableFontSettings = []
	for instance in thisFont.instances:
		if instance.type == INSTANCETYPEVARIABLE:
			variableFontSettings.append(instance)

	fontPaths = []
	if currentExportPath and variableFontSettings:
		for variableFontExport in variableFontSettings:
			exportFolder = exportFolderOfInstance(thisFont, variableFontExport)
			folderPath = path.join(currentExportPath, exportFolder) if exportFolder else currentExportPath
			fontPaths.append(path.join(folderPath, otVarFileName(thisFont, thisInstance=variableFontExport)))
	elif not currentExportPath:
		print("⚠️ Could not determine most recent VF export.")
		chosenPaths = GetOpenFile(
			message="Could not determine most recent VF export. Please choose the variable font.",
			allowsMultipleSelection=True,
			filetypes=["otf", "ttf", "woff", "woff2"],
		)
		if chosenPaths:
			fontPaths = list(chosenPaths) if isinstance(chosenPaths, (list, tuple)) else [chosenPaths]
		else:
			print("⚠️ No file chosen.")
	else:
		print("⚠️ No VF Settings found in Font Info > Exports.")

	if fontPaths:
		for i, fontPath in enumerate(fontPaths):
			print(f"\n⚙️ Variable font {i + 1}:")
			addEmptyDSIG(fontPath)
		print("\n✅ Done.")
