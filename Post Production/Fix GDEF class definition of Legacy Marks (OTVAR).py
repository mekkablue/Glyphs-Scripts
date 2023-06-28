#MenuTitle: Fix GDEF class definition of Legacy Marks (OTVAR)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Fix GDEF definition of spacing, non-combining marks for your most recent OTVAR export(s), will switch to class 1 (‘base glyph’, single character, spacing glyph) if necessary.
"""

import fontTools
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
	legacyMarks = (
		"dieresis",
		"dotaccent",
		"grave",
		"acute",
		"hungarumlaut",
		"circumflex",
		"caron",
		"breve",
		"ring",
		"tilde",
		"macron",
		"cedilla",
		"ogonek",
		"gigi"
	)
	
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("Report: Fix GDEF definition of Legacy Marks")

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
			font = ttLib.TTFont(fontpath)
			print(f"Processing: {fontpath}...")

			gdef = font["GDEF"].table
			madeChanges = False

			if not gdef.MarkGlyphSetsDef:
				print("⚠️ No MarkGlyphSetsDef found in GDEF table.")
			else:
				print("Scanning MarkGlyphSetsDef...")
				for coverage in gdef.MarkGlyphSetsDef.Coverage:
					for i in range(len(coverage.glyphs)-1,-1,-1):
						glyph = coverage.glyphs[i]
						if glyph in legacyMarks:
							coverage.glyphs.pop(i)
							print(f"\t🚫 Removed {glyph} from GDEF.MarkGlyphSetsDef")
							madeChanges = True
						elif not (glyph.startswith("uni03") or "comb" in glyph):
							print(f"\t❓ {glyph}")
						# else:
						# 	print(f"\t✅ {glyph}")

			if not gdef.GlyphClassDef:
				print("⚠️ No GlyphClassDef found in GDEF table.")
			else:
				print("Scanning GlyphClassDef...")
				for legacyMark in legacyMarks:
					if legacyMark in gdef.GlyphClassDef.classDefs:
						classType = gdef.GlyphClassDef.classDefs[legacyMark]
						if classType != 1:
							gdef.GlyphClassDef.classDefs[legacyMark] = 1
							print(f"\t👨🏻‍🔧 Switched {legacyMark} from class {classType} to 1")
							madeChanges = True
			
			if not madeChanges:
				print("🤷🏻‍♀️ No changes, file left untouched.")
			else:
				font.save(fontpath, reorderTables=False)
				print("💾 Saved file.")
			print()
