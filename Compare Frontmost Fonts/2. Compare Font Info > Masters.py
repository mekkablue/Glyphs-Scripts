# MenuTitle: Compare Font Info > Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Detailed report of Font Info > Masters for the two frontmost fontsand outputs a report in the Macro Window.
"""

from compare import compareCount, compareLists, cleanUpAndShortenParameterContent
from GlyphsApp import Glyphs

thisFont = Glyphs.fonts[0]  # frontmost font
otherFont = Glyphs.fonts[1]  # second font
if thisFont.filepath:
	thisFileName = thisFont.filepath.lastPathComponent()
else:
	thisFileName = None
if otherFont.filepath:
	otherFileName = otherFont.filepath.lastPathComponent()
else:
	otherFileName = None

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print("Comparing Font Info > Masters for:".upper())
print()
print("1. %s (family: %s)" % (thisFileName, thisFont.familyName))
print("   ~/%s" % thisFont.filepath.relativePathFromBaseDirPath_("~"))
print("2. %s (family: %s)" % (otherFileName, otherFont.familyName))
print("   ~/%s" % otherFont.filepath.relativePathFromBaseDirPath_("~"))
print()

for thisMaster, otherMaster in zip(thisFont.masters, otherFont.masters):
	print()
	print()
	print("   COMPARING MASTERS:")
	print("   A. %s" % thisMaster.name)
	print("   B. %s" % otherMaster.name)
	print()

	keyValueDict = {
		"Ascender": (thisMaster.ascender, otherMaster.ascender),
		"Cap Height": (thisMaster.capHeight, otherMaster.capHeight),
		"x-Height": (thisMaster.xHeight, otherMaster.xHeight),
		"Descender": (thisMaster.descender, otherMaster.descender),
		"Italic Angle": (thisMaster.italicAngle, otherMaster.italicAngle),
	}
	for key in keyValueDict:
		thisValue, otherValue = keyValueDict[key]
		if thisValue == otherValue:
			print("✅ %s value is the same: %i" % (key, thisValue))
		else:
			print("⚠️ Different %s values:" % key)
			print("   A. %.1f in %s" % (thisValue, thisMaster.name))
			print("   B. %.1f in %s" % (otherValue, otherMaster.name))

	# count zones, stems:
	compareCount(
		"Zones",
		len(thisMaster.alignmentZones),
		len(otherMaster.alignmentZones),
		thisMaster.name,
		otherMaster.name,
	)
	try:
		if Glyphs.versionNumber >= 3:
			# GLYPHS 3 code:
			compareCount(
				"Vertical Stems",
				len([stem for i, stem in enumerate(thisMaster.stems) if not thisFont.stems[i].horizontal]),
				len([stem for i, stem in enumerate(otherMaster.stems) if not otherFont.stems[i].horizontal]),
				thisMaster.name,
				otherMaster.name,
			)
			compareCount(
				"Horizontal Stems",
				len([stem for i, stem in enumerate(thisMaster.stems) if thisFont.stems[i].horizontal]),
				len([stem for i, stem in enumerate(otherMaster.stems) if otherFont.stems[i].horizontal]),
				thisMaster.name,
				otherMaster.name,
			)
		else:
			# GLYPHS 2 code:
			compareCount(
				"Vertical Stems",
				len(thisMaster.verticalStems),  # type: ignore
				len(otherMaster.verticalStems),  # type: ignore
				thisMaster.name,
				otherMaster.name,
			)
			compareCount(
				"Horizontal Stems",
				len(thisMaster.horizontalStems),  # type: ignore
				len(otherMaster.horizontalStems),  # type: ignore
				thisMaster.name,
				otherMaster.name,
			)
	except Exception as e:  # noqa: F841
		import traceback
		print(traceback.format_exc())

	# comparing parameters:
	theseParameters = [p.name for p in thisMaster.customParameters]
	otherParameters = [p.name for p in otherMaster.customParameters]
	thisSet, otherSet = compareLists(theseParameters, otherParameters)
	if thisSet or otherSet:
		if otherSet:
			print("❌ Parameters not in (A) %s:" % thisMaster.name)
			print("   %s" % ("\n   ".join(otherSet)))
		if thisSet:
			print("❌ Parameters not in (B) %s:" % otherMaster.name)
			print("   %s" % ("\n   ".join(thisSet)))
	else:
		print("✅ Same structure of parameters in both masters.")

	# detailed comparison:
	for thisParameter in thisMaster.customParameters:
		otherParameter = None
		for currParameter in otherMaster.customParameters:
			if currParameter.parameterIdentifier() == thisParameter.parameterIdentifier():
				otherParameter = currParameter
				break
		if otherParameter:
			if thisParameter.name == otherParameter.name and thisParameter.value == otherParameter.value:
				parameterContent = cleanUpAndShortenParameterContent(thisParameter)
				print("💚 Parameter %s: same value (%s). OK." % (thisParameter.name, parameterContent))
			else:
				thisContent = cleanUpAndShortenParameterContent(thisParameter)
				otherContent = cleanUpAndShortenParameterContent(otherParameter)
				print("⚠️ Parameter %s: different values." % thisParameter.name)
				print("    A. %s in %s (%s)" % (thisContent, thisMaster.name, repr(thisParameter)))
				print("    B. %s in %s (%s)" % (otherContent, otherMaster.name, repr(otherParameter)))
