from AppKit import NSPoint
from GlyphsApp import Glyphs

parameterName = "TTFAutohint options"

valuelessOptions = (
	"adjust-subglyphs",
	"composites",
	"dehint",
	"detailed-info",
	"ignore-restrictions",
	"no-info",
	"symbol",
	"ttfa-table",
	"windows-compatibility",
)

availableOptionsDict = {
	"adjust-subglyphs": "adjust-subglyphs",
	"composites": "hint-composites",
	"default-script": "default-script",
	"dehint": "dehint",
	"detailed-info": "ttfautohint-info",
	"fallback-script": "fallback-script",
	"fallback-stem-width": "fallback-stem-width",
	"hinting-limit": "hinting-limit",
	"hinting-range-max": "hint-set-range-minimum-hint-set-range-maximum",
	"hinting-range-min": "hint-set-range-minimum-hint-set-range-maximum",
	"ignore-restrictions": "miscellaneous",
	"increase-x-height": "x-height-increase-limit",
	"no-info": "ttfautohint-info",
	"stem-width-mode": "stem-width-and-positioning-mode",
	"strong-stem-width": "stem-width-and-positioning-mode",
	"symbol": "symbol-font",
	"ttfa-table": "add-ttfa-info-table",
	"windows-compatibility": "windows-compatibility",
	"x-height-snapping-exceptions": "x-height-snapping-exceptions",
	"reference": "blue-zone-reference-font",
}

availableOptions = sorted(availableOptionsDict.keys())


def removeFromAutohintOptions(thisInstance, removeOption):
	parameter = thisInstance.customParameters[parameterName]
	if parameter:
		ttfAutohintOptions = parameter.split(" ")
		popList = []
		optionToBeRemoved = f"--{removeOption.strip()}"
		for i, currentOption in enumerate(ttfAutohintOptions):
			if currentOption.split("=")[0] == optionToBeRemoved:
				popList.append(i)
		if popList:
			for j in sorted(popList)[::-1]:
				ttfAutohintOptions.pop(j)
			thisInstance.customParameters[parameterName] = " ".join(ttfAutohintOptions)


def dictToParameterValue(ttfAutohintDict):
	parameterValue = ""
	for key in ttfAutohintDict:
		parameterValue += " "
		if not ttfAutohintDict[key]:
			parameterValue += f"--{key.strip(' -')}"
		else:
			value = str(ttfAutohintDict[key]).strip()
			parameterValue += f"--{key.strip(' -')}={value}"
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


def glyphInterpolation(thisGlyph, thisInstance):
	try:
		interpolatedFont = thisInstance.pyobjc_instanceMethods.interpolatedFont()
		interGlyph = interpolatedFont.glyphForName_(thisGlyph.name)
		if Glyphs.versionNumber >= 3:
			# GLYPHS 3
			interpolatedLayer = interGlyph.layer0()
		else:
			# GLYPHS 2
			interpolatedLayer = interGlyph.layerForKey_(interpolatedFont.fontMasterID())

		thisFont = thisGlyph.parent
		if not thisInstance.customParameters["Grid Spacing"] and not (thisFont.gridMain() / thisFont.gridSubDivision):
			interpolatedLayer.roundCoordinates()
		if len(interpolatedLayer.paths) != 0:
			return interpolatedLayer
		else:
			return None
	except Exception as e:  # noqa: F841
		import traceback
		print(traceback.format_exc())
		return None


def idotlessMeasure(instance, font=None):
	if font is None:
		font = instance.font
	idotless = font.glyphs["idotless"]
	idotlessLayer = glyphInterpolation(idotless, instance)
	if idotlessLayer:
		measureHeight = idotlessLayer.bounds.size.height * 0.5
		measureStartX = idotlessLayer.bounds.origin.x - 10
		measureEndX = measureStartX + idotlessLayer.bounds.size.width + 20
		measureStart = NSPoint(measureStartX, measureHeight)
		measureEnd = NSPoint(measureEndX, measureHeight)
		intersections = idotlessLayer.intersectionsBetweenPoints(measureStart, measureEnd, components=True)
		if not len(intersections) > 2:
			return None
		else:
			firstIntersection = intersections[1]
			lastIntersection = intersections[-2]
			idotlessWidth = lastIntersection.x - firstIntersection.x
			return idotlessWidth
	else:
		return None


def writeOptionsToInstance(optionDict, instance, font=None):
	value = dictToParameterValue(optionDict)
	try:
		if Glyphs.versionNumber >= 3:
			instanceWeightValue = tuple(instance.axes)[0]  # fallback if there is no weight axis
			if font is None:
				font = instance.font
			for axisIndex, axis in enumerate(font.axes):
				if axis.axisTag == "wght":
					instanceWeightValue = tuple(instance.axes)[axisIndex]
					break
		else:
			# GLYPHS 2
			instanceWeightValue = instance.weightValue
	except Exception as e:
		instanceWeightValue = None
		print(f"⚠️ Error determining the instance weight value:\n{e}")
		import traceback
		print("🫣 instance:", instance)
		print("🫣 font:", font)
		print(traceback.format_exc())

	if instanceWeightValue is not None:
		value = value.replace("--fallback-stem-width=*", f"--fallback-stem-width={instanceWeightValue}")

	if "fallback-stem-width=idotless" in value:
		actualStemWidth = idotlessMeasure(instance, font)
		if actualStemWidth:
			value = value.replace("--fallback-stem-width=idotless", f"--fallback-stem-width={int(actualStemWidth)}")
		else:
			print(f"Warning: Could not measure stem width of idotless in instance ‘{instance.name}’.")
			return  # do nothing
	instance.customParameters[parameterName] = value
