#MenuTitle: Compare Font Info > Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Detailed report of Font Info > Masters for the two frontmost fontsand outputs a report in the Macro Window.
"""

from compare import *
thisFont = Glyphs.fonts[0] # frontmost font
otherFont = Glyphs.fonts[1] # second font
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
			print(u"✅ %s value is the same: %i" % (key, thisValue))
		else:
			print(u"⚠️ Different %s values:" % key)
			print(u"   A. %.1f in %s" % (thisValue, thisMaster.name))
			print(u"   B. %.1f in %s" % (otherValue, otherMaster.name))

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
				len([stem for stem in thisMaster.stems if not stem.horizontal]),
				len([stem for stem in otherMaster.stems if not stem.horizontal]),
				thisMaster.name,
				otherMaster.name,
				)
			compareCount(
				"Horizontal Stems",
				len([stem for stem in thisMaster.stems if stem.horizontal]),
				len([stem for stem in otherMaster.stems if stem.horizontal]),
				thisMaster.name,
				otherMaster.name,
				)
		else:
			# GLYPHS 2 code:
			compareCount(
				"Vertical Stems",
				len(thisMaster.verticalStems),
				len(otherMaster.verticalStems),
				thisMaster.name,
				otherMaster.name,
				)
			compareCount(
				"Horizontal Stems",
				len(thisMaster.horizontalStems),
				len(otherMaster.horizontalStems),
				thisMaster.name,
				otherMaster.name,
				)
	except Exception as e:
		import traceback
		print(traceback.format_exc())

	# comparing parameters:
	theseParameters = [p.name for p in thisMaster.customParameters]
	otherParameters = [p.name for p in otherMaster.customParameters]
	thisSet, otherSet = compareLists(theseParameters, otherParameters)
	if thisSet or otherSet:
		if otherSet:
			print(u"❌ Parameters not in (A) %s:" % thisMaster.name)
			print("   %s" % ("\n   ".join(otherSet)))
		if thisSet:
			print(u"❌ Parameters not in (B) %s:" % otherMaster.name)
			print("   %s" % ("\n   ".join(thisSet)))
	else:
		print(u"✅ Same structure of parameters in both masters.")

	# detailed comparison:
	for thisParameter in thisMaster.customParameters:
		otherParameter = None
		for currParameter in otherMaster.customParameters:
			if currParameter.parameterIdentifier() == thisParameter.parameterIdentifier():
				otherParameter = currParameter
				break
		if otherParameter:
			if thisParameter == otherParameter:
				parameterContent = cleanUpAndShortenParameterContent(thisParameter)
				print(u"💚 Parameter %s: same value (%s). OK." % (thisParameter.name, parameterContent))
			else:
				thisContent = cleanUpAndShortenParameterContent(thisParameter)
				otherContent = cleanUpAndShortenParameterContent(otherParameter)
				print(u"⚠️ Parameter %s: different values." % thisParameter.name)
				print(u"    A. %s in %s" % (thisContent, thisMaster.name))
				print(u"    B. %s in %s" % (otherContent, otherMaster.name))
