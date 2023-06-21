#MenuTitle: Fix Italic PS Names (OTVAR)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Fixes double Italic namings in name table entries in the most recent export of the current font. Run this right after a variable font export.
"""

from fontTools import ttLib
from AppKit import NSString
from otvarLib import *

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
	print("Report: Fix PS Names in OTVAR Exports")

	suffixes = ["ttf"]
	for suffix in ("woff", "woff2"):
		if Glyphs.defaults[f"GXExport{suffix.upper()}"]:
			suffixes.append(suffix)
	print(f"- suffixes: {', '.join(suffixes)}")

	thisFont = Glyphs.font # frontmost font
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
			print(f"\n- processing: '{fontpath}'")
			otFont = ttLib.TTFont(file=fontpath)
			# print("CHECK1 font", otFont) # DEBUG
			nameTable = otFont["name"]
			# print("CHECK2 name", nameTable) # DEBUG
			anythingChanged = False
			for nameTableEntry in nameTable.names:
				nameID = nameTableEntry.nameID
				# print("CHECK3 nameID", nameID) # DEBUG
				if nameID in (3, 6) or nameID > 255:
					nameValue = nameTableEntry.toStr()
					# print("CHECK4 nameID", nameID, nameValue) # DEBUG
					oldName = nameValue
					if "Italic-" in nameValue and nameValue.count("Italic")>1:
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
				print("- 💾 saved file")
			else:
				print("- 🤷🏻‍♀️ no changes, file left unchanged")