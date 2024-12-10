# MenuTitle: Clean Version String
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__ = """
Adds a clean versionString parameter, and disables ttfAutohint info in the version string. Hold down OPTION and SHIFT for all masters
"""

from AppKit import NSEvent, NSEventModifierFlagOption, NSEventModifierFlagShift
from GlyphsApp import Glyphs


# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()


def removeFromAutohintOptions(thisInstance, removeOption):
	parameter = thisInstance.customParameters[parameterName]
	if parameter:
		ttfAutohintOptions = parameter.split(u" ")
		popList = []
		optionToBeRemoved = "--%s" % removeOption.strip()
		for i, currentOption in enumerate(ttfAutohintOptions):
			if currentOption.split(u"=")[0] == optionToBeRemoved:
				popList.append(i)
		if popList:
			for j in sorted(popList)[::-1]:
				ttfAutohintOptions.pop(j)
			thisInstance.customParameters[parameterName] = " ".join(ttfAutohintOptions)
		else:
			print(f"-- Warning: '{removeOption}' not found.")


def dictToParameterValue(ttfAutohintDict):
	parameterValue = ""
	for key in ttfAutohintDict:
		parameterValue += " "
		if not ttfAutohintDict[key]:
			parameterValue += "--%s" % key.strip(" -")
		else:
			value = str(ttfAutohintDict[key]).strip()
			parameterValue += "--%s=%s" % (key.strip(" -"), value)
	return parameterValue.strip()


def ttfAutohintDict(parameterValue):
	"""Returns a dict for a TTFAutohint parameter value."""
	ttfAutohintDict = {}
	for ttfAutohintOption in parameterValue.split("--"):
		if "=" in ttfAutohintOption:
			[key, value] = ttfAutohintOption.split("=")
			value = value.strip()
		else:
			key = ttfAutohintOption
			value = None
		if key:
			ttfAutohintDict[key.strip(" -")] = value
	return ttfAutohintDict


def writeOptionsToInstance(optionDict, instance, parameterName):
	value = dictToParameterValue(optionDict)
	instance.customParameters[parameterName] = value


def cleanVersionStringProperty(thisFont):
	# version string property
	propKey = "versionString"
	propValue = "Version %d.%03d"
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		thisFont.setProperty_value_languageTag_(propKey, propValue, None)
	else:
		# GLYPHS 2
		thisFont.customParameters[propKey] = propValue
	print(f"Set: {propKey}='{propValue}' in Font Info > Font")


def cleanTtfautohintSetting(thisFont):
	# ttfautohint parameter
	parameterName = "TTFAutohint options"
	optionName = "no-info"
	enteredValue = ""
	for thisInstance in thisFont.instances:
		if thisInstance.customParameters[parameterName] is not None:
			optionDict = ttfAutohintDict(thisInstance.customParameters[parameterName])
			optionDict[optionName] = enteredValue
			writeOptionsToInstance(optionDict, thisInstance, parameterName)
			print("Set: ttfAutohint %s in instance '%s'." % (
				optionName,
				thisInstance.name,
			))
		else:
			print("No TTF Autohint parameter in instance '%s'. %s not set." % (
				thisInstance.name,
				optionName,
			))


keysPressed = NSEvent.modifierFlags()
optionKeyPressed = keysPressed & NSEventModifierFlagOption == NSEventModifierFlagOption
shiftKeyPressed = keysPressed & NSEventModifierFlagShift == NSEventModifierFlagShift

allFonts = optionKeyPressed and shiftKeyPressed
if allFonts:
	theseFonts = Glyphs.fonts
else:
	theseFonts = (Glyphs.font, )

for thisFont in theseFonts:
	print(f"🧼 Clean Version String for: {thisFont.familyName} (📄 {thisFont.filepath.lastPathComponent()})\n")
	cleanVersionStringProperty(thisFont)
	cleanTtfautohintSetting(thisFont)
	print()

print("✅ Done.")
