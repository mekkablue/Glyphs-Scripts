#MenuTitle: Add Empty DSIG (OTVAR)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Run this after you export a Variable Font (TTF) and it will add an empty DSIG table. Necessary to pass the MyFonts onboarding of OTVAR TTFs.
"""

from fontTools import ttLib
from AppKit import NSString

def currentOTVarExportPath():
	exportPath = Glyphs.defaults["GXExportPathManual"]
	if Glyphs.versionNumber and Glyphs.versionNumber >= 3:
		useExportPath = Glyphs.defaults["GXExportUseExportPath"]
	else:
		useExportPath = Glyphs.defaults["GXPluginUseExportPath"]
	if useExportPath:
		exportPath = Glyphs.defaults["GXExportPath"]
	return exportPath

def otVarFileName(thisFont, thisInstance=None, suffix="ttf"):
	if not thisInstance is None:
		fileName = thisInstance.fileName()
		# circumvent bug in Glyphs 3.0.5
		if fileName.endswith(".otf"):
			fileName = fileName[:-4]
		if not fileName:
			fileName = thisInstance.customParameters["fileName"]
			if not fileName:
				familyName = familyNameOfInstance(thisInstance)
				fileName = ("%s-%s" % (familyName, thisInstance.name)).replace(" ", "")
		return "%s.%s" % (fileName, suffix)
	elif thisFont.customParameters["Variable Font File Name"] or thisFont.customParameters["variableFileName"]:
		fileName = thisFont.customParameters["Variable Font File Name"]
		if not fileName:
			fileName = thisFont.customParameters["variableFileName"]
		return "%s.%s" % (fileName, suffix)
	else:
		familyName = otVarFamilyName(thisFont)
		if Glyphs.versionString >= "3.0.3":
			fileName = "%sVF.%s" % (familyName, suffix)
		else:
			fileName = "%sGX.%s" % (familyName, suffix)
		return fileName.replace(" ", "")

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print("Adding DSIG for current font")

thisFont = Glyphs.font # frontmost font
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
		print(f"\n⚙️ Variable font setting {i+1}:")
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
