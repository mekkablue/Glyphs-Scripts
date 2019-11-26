from __future__ import print_function
#MenuTitle: Clean Version String
# -*- coding: utf-8 -*-
__doc__="""
Adds a clean versionString parameter, and disables ttfAutohint info in the version string.
"""

thisFont = Glyphs.font # frontmost font
thisFont.customParameters["versionString"] = "Version %d.%03d"
print("Set: versionString='Version %d.%03d' in Font Info > Font")

def removeFromAutohintOptions( thisInstance, removeOption ):
	parameter = thisInstance.customParameters[parameterName]
	if parameter:
		ttfAutohintOptions = parameter.split(u" ")
		popList = []
		optionToBeRemoved = "--%s" % removeOption.strip()
		for i, currentOption in enumerate(ttfAutohintOptions):
			if currentOption.split(u"=")[0] == optionToBeRemoved:
				popList.append(i)
		if popList:
			for j in sorted( popList )[::-1]:
				ttfAutohintOptions.pop(j)
			thisInstance.customParameters[parameterName] = " ".join(ttfAutohintOptions)
		else:
			print("-- Warning: '%s' not found." % removeOption)

def dictToParameterValue( ttfAutohintDict ):
	parameterValue = ""
	for key in ttfAutohintDict:
		parameterValue += " "
		if not ttfAutohintDict[key]:
			parameterValue += "--%s" % key.strip(" -")
		else:
			value = str(ttfAutohintDict[key]).strip()
			parameterValue += "--%s=%s" % ( key.strip(" -"), value )
	return parameterValue.strip()

def ttfAutohintDict( parameterValue ):
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
	
def writeOptionsToInstance( optionDict, instance ):
	value = dictToParameterValue(optionDict)
	instance.customParameters[parameterName] = value

parameterName = "TTFAutohint options"
optionName = "no-info"
enteredValue = ""
for thisInstance in thisFont.instances:
	if not thisInstance.customParameters[parameterName] is None:
		optionDict = ttfAutohintDict( thisInstance.customParameters[parameterName] )
		optionDict[ optionName ] = enteredValue
		writeOptionsToInstance( optionDict, thisInstance )
		print("Set: ttfAutohint %s in instance '%s'." % (
			optionName,
			thisInstance.name,
		))
	else:
		print("No TTF Autohint parameter in instance '%s'. %s not set." % (
			thisInstance.name,
			optionName,
		))
