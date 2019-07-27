#MenuTitle: Compare Font Info > Font
# -*- coding: utf-8 -*-
__doc__="""
Detailed report of Font Info > Masters for the two frontmost fontsand outputs a report in the Macro Window.
"""

import GlyphsApp
from compare import *

thisFont = Glyphs.fonts[0] # frontmost font
otherFont = Glyphs.fonts[1] # second font
thisFileName = thisFont.filepath.pathComponents()[-1]
otherFileName = otherFont.filepath.pathComponents()[-1]

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print "Comparing Font Info > Font for:".upper()
print
print "1. %s (family: %s)" % (thisFileName, thisFont.familyName)
print "   %s" % thisFont.filepath
print "2. %s (family: %s)" % (otherFileName, otherFont.familyName)
print "   %s" % otherFont.filepath
print 

keyValueDict= {
	"Family Name": (thisFont.familyName, otherFont.familyName),
	"Designer": (thisFont.designer, otherFont.designer),
	"Designer URL": (thisFont.designerURL, otherFont.designerURL),
	"Manufacturer": (thisFont.manufacturer, otherFont.manufacturer),
	"Manufacturer URL": (thisFont.manufacturerURL, otherFont.manufacturerURL),
	"Copyright": (thisFont.copyright, otherFont.copyright),
	"Version Major": (thisFont.versionMajor, otherFont.versionMajor),
	"Version Minor": (thisFont.versionMinor, otherFont.versionMinor),
	"Units per Em": (thisFont.upm, otherFont.upm),
	"Date": (str(thisFont.date), str(otherFont.date)),
}
for key in keyValueDict:
	thisValue, otherValue = keyValueDict[key]
	if thisValue == otherValue:
		print u"✅ %s value is the same: %s" % (key, thisValue)
	else:
		print u"⚠️ Different %s values:" % key
		print u"   A. '%s' in %s" % (thisValue, thisFileName)
		print u"   B. '%s' in %s" % (otherValue, otherFileName)

# count parameters:
compareCount(
	"Custom Parameters",
	len(thisFont.customParameters), len(otherFont.customParameters),
	thisFileName, otherFileName,
)
	
# comparing parameters:
theseParameters = [p.name for p in thisFont.customParameters]
otherParameters = [p.name for p in otherFont.customParameters]
thisSet, otherSet = compareLists(theseParameters, otherParameters)
if thisSet or otherSet:
	if otherSet:
		print u"❌ Parameters not in (A) %s:" % thisFileName
		print "   %s" % ("\n   ".join(otherSet))
	if thisSet:
		print u"❌ Parameters not in (B) %s:" % otherFileName
		print "   %s" % ("\n   ".join(thisSet))
else:
	print u"✅ Same structure of parameters in both masters."

# detailed comparison:
for thisParameterName in [p.name for p in thisFont.customParameters]:
	thisParameter = thisFont.customParameters[thisParameterName]
	otherParameter = otherFont.customParameters[thisParameterName]
	if otherParameter:
		if thisParameter == otherParameter:
			parameterContent = cleanUpAndShortenParameterContent(thisParameter)
			print u"💚 Parameter %s: same value (%s). OK." % (thisParameterName, parameterContent)
		else:
			thisContent = cleanUpAndShortenParameterContent(thisParameter)
			otherContent = cleanUpAndShortenParameterContent(otherParameter)
			print u"⚠️ Parameter %s: different values." % thisParameterName
			print u"    A. %s in %s" % (thisContent, thisFileName)
			print u"    B. %s in %s" % (otherContent, otherFileName)
			
			