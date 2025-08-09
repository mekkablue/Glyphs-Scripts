# MenuTitle: Fix Italic PS Names (OTVAR)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Fixes double Italic namings in name table entries in the most recent export of the current font. Run this right after a variable font export.
"""

from fontTools import ttLib
from AppKit import NSString
from otvarLib import currentOTVarExportPath, otVarFileName  # local lib
from GlyphsApp import Glyphs, INSTANCETYPEVARIABLE, Message

if Glyphs.versionNumber < 3.2:
	Message(
		title="Version Error",
		message="This script requires app version 3.2 or later. In Glyphs > Settings > Updates, activate Cutting Edge Versions, and check for updates.",
		OKButton=None,
	)
else:
	fileCount = 0

	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("Report: Fix PS Names in OTVAR Exports")

	suffixes = ["ttf"]
	for suffix in ("woff", "woff2"):
		if Glyphs.defaults[f"GXExport{suffix.upper()}"]:
			suffixes.append(suffix)
	print(f"- suffixes: {', '.join(suffixes)}")

	thisFont = Glyphs.font  # frontmost font
	currentExportPath = currentOTVarExportPath()
	print(f"- path: {currentExportPath}")

	variableFontSettings = []
	for instance in thisFont.instances:
		if instance.type == INSTANCETYPEVARIABLE:
			variableFontSettings.append(instance)

	if not variableFontSettings:
		variableFontSettings = [None]
	for variableFontExport in variableFontSettings:
		for suffix in suffixes:
			fontpath = NSString.alloc().initWithString_(currentExportPath).stringByAppendingPathComponent_(otVarFileName(thisFont, thisInstance=variableFontExport, suffix=suffix))
			print(f"\n📄 Processing: '{fontpath}'")
			otFont = ttLib.TTFont(file=fontpath)
			if not otFont:
				print("❌ No font file found. Skipping.")
				continue

			fileCount += 1

			nameTable = otFont["name"]
			anythingChanged = False
			for nameTableEntry in nameTable.names:
				nameID = nameTableEntry.nameID
				nameValue = nameTableEntry.toStr()
				oldName = nameValue
				if nameID in (4, 6, 17):
					for oldParticle in ("Regular Italic", "RegularItalic"):
						if oldParticle in nameValue:
							nameValue = nameValue.replace(oldParticle, "Italic")
				if nameID in (3, 6) or nameID > 255:
					oldName = nameValue
					if "Italic-" in nameValue and nameValue.count("Italic") > 1:
						particles = nameValue.split("-")
						for i in range(1, len(particles)):
							particles[i] = particles[i].replace("Italic", "").strip()
							if len(particles[i]) == 0:
								particles[i] = "Regular"
						nameValue = "-".join(particles)
				if nameValue != oldName:
					nameTableEntry.string = nameValue
					anythingChanged = True
					print(f"✅ Changed ID {nameID}: {oldName} → {nameValue}")
			if anythingChanged:
				otFont.save(fontpath, reorderTables=False)
				print("💾 Saved file.")
			else:
				print("🤷🏻‍♀️ No changes, file left unchanged.")

	print(f"\n✅ Done. Processed {fileCount} file{'' if fileCount == 1 else 's'}.")
