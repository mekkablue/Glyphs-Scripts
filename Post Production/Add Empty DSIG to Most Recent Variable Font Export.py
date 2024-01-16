# MenuTitle: Add Empty DSIG (OTVAR)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Run this after you export a Variable Font (TTF) and it will add an empty DSIG table. Necessary to pass the MyFonts onboarding of OTVAR TTFs.
"""

from fontTools import ttLib
from AppKit import NSString
from otvarLib import currentOTVarExportPath, otVarFileName
from GlyphsApp import Glyphs, INSTANCETYPEVARIABLE, Message


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

	if not variableFontSettings:
		print("⚠️ No VF Settings found in Font Info > Exports.")
	else:
		for i, variableFontExport in enumerate(variableFontSettings):
			print(f"\n⚙️ Variable font setting {i + 1}:")
			fontpath = NSString.alloc().initWithString_(currentExportPath).stringByAppendingPathComponent_(otVarFileName(thisFont, thisInstance=variableFontExport))
			print(f"📄 {fontpath}")
			font = ttLib.TTFont(file=fontpath)
			dsig = ttLib.ttFont.newTable("DSIG")
			dsig.ulVersion = 1
			dsig.usFlag = 0
			dsig.usNumSigs = 0
			dsig.signatureRecords = []
			font["DSIG"] = dsig
			font.save(fontpath, reorderTables=False)
			print("💾 Saved file.")
		print("\n✅ Done.")
