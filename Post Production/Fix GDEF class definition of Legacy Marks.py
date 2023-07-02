#MenuTitle: Fix GDEF class definition of Legacy Marks
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Fix GDEF definition of spacing, non-combining marks for all .ttf, .otf, .woff, .woff2 in your current export folders. Will switch to class 1 (‘base glyph’, single character, spacing glyph) if necessary.
"""

import fontTools
from fontTools import ttLib
from AppKit import NSString
from otvarLib import *
import os

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
		"uni02BB"
	)
	
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("Report: Fix GDEF definition of Legacy Marks")

	currentExportPaths = [currentOTVarExportPath()]
	currentExportPaths.append(currentStaticExportPath())
	print(f"- OTVAR path: {currentExportPaths[0]}")
	print(f"- Static path: {currentExportPaths[1]}")
	print()

	suffixes = ("otf", "ttf", "woff", "woff2")
	fontpaths = []
	for exportPath in currentExportPaths:
		for file in os.listdir(exportPath):
			for suffix in suffixes:
				if file.endswith(f".{suffix}"):
					fontpath = os.path.join(exportPath, file)
					fontpaths.append(fontpath)
	
	for fontpath in fontpaths:
		print(f"📄 Processing: {fontpath}")
		try:
			font = ttLib.TTFont(fontpath)
		except Exception as e:
			import traceback
			print(traceback.format_exc())
			print()
			continue
		
		if not "GDEF" in font.keys():
			print(f"⚠️ No GDEF table found, skipping file.\n")
			continue
			
		gdef = font["GDEF"].table
		madeChanges = False

		if not hasattr(gdef, "MarkGlyphSetsDef") or not gdef.MarkGlyphSetsDef:
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
		
print("✅ Done.")
