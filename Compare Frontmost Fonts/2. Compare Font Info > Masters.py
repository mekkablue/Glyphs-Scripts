#MenuTitle: Compare Font Info > Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Detailed report of Font Info > Masters for the two frontmost fontsand outputs a report in the Macro Window.
"""

from compare import *

thisFont = Glyphs.fonts[0] # frontmost font
otherFont = Glyphs.fonts[1] # second font
thisFileName = thisFont.filepath.pathComponents()[-1]
otherFileName = otherFont.filepath.pathComponents()[-1]

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print("Comparing Font Info > Masters for:".upper())
print()
print("1. %s (family: %s)" % (thisFileName, thisFont.familyName))
print("   %s" % thisFont.filepath)
print("2. %s (family: %s)" % (otherFileName, otherFont.familyName))
print("   %s" % otherFont.filepath)
print() 

for thisMaster, otherMaster in zip(thisFont.masters, otherFont.masters):
	print() 
	print() 
	print("   COMPARING MASTERS:")
	print("   A. %s" % thisMaster.name)
	print("   B. %s" % otherMaster.name)
	print()
	
	keyValueDict= {
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
		len(thisMaster.alignmentZones), len(otherMaster.alignmentZones),
		thisMaster.name, otherMaster.name,
		)
	compareCount(
		"Vertical Stems", 
		len(thisMaster.verticalStems), len(otherMaster.verticalStems),
		thisMaster.name, otherMaster.name,
		)
	compareCount(
		"Horizontal Stems", 
		len(thisMaster.horizontalStems), len(otherMaster.horizontalStems),
		thisMaster.name, otherMaster.name,
		)
		
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
	for thisParameterName in [p.name for p in thisMaster.customParameters]:
		thisParameter = thisMaster.customParameters[thisParameterName]
		otherParameter = otherMaster.customParameters[thisParameterName]
		if otherParameter:
			if thisParameter == otherParameter:
				parameterContent = cleanUpAndShortenParameterContent(thisParameter)
				print(u"💚 Parameter %s: same value (%s). OK." % (thisParameterName, parameterContent))
			else:
				thisContent = cleanUpAndShortenParameterContent(thisParameter)
				otherContent = cleanUpAndShortenParameterContent(otherParameter)
				print(u"⚠️ Parameter %s: different values." % thisParameterName)
				print(u"    A. %s in %s" % (thisContent, thisMaster.name))
				print(u"    B. %s in %s" % (otherContent, otherMaster.name))
				
				