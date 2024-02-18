# MenuTitle: Set ttfautohint Options
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:  # noqa: F841
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")
__doc__ = """
Set options for existing 'TTFAutohint options' Custom Parameters.
"""

import vanilla
from Foundation import NSPoint
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


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
		ttfAutohintOptions = parameter.split(u" ")
		popList = []
		optionToBeRemoved = f"--{removeOption.strip()}"
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


def idotlessMeasure(instance):
	thisFont = instance.font
	idotless = thisFont.glyphs["idotless"]
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


def writeOptionsToInstance(optionDict, instance):
	value = dictToParameterValue(optionDict)
	try:
		if Glyphs.versionNumber >= 3:
			instanceWeightValue = instance.axes[0]  # fallback if there is no weight axis
			font = instance.font
			for axisIndex, axis in enumerate(font.axes):
				if axis.axisTag == "wght":
					instanceWeightValue = instance.axes[axisIndex]
					break
		else:
			# GLYPHS 2
			instanceWeightValue = instance.weightValue
	except Exception as e:
		instanceWeightValue = None
		print(f"⚠️ Error determining the instance weight value:\n{e}")
		import traceback
		print(traceback.format_exc())

	if instanceWeightValue is not None:
		value = value.replace("--fallback-stem-width=*", f"--fallback-stem-width={instanceWeightValue}")

	if "fallback-stem-width=idotless" in value:
		actualStemWidth = idotlessMeasure(instance)
		if actualStemWidth:
			value = value.replace("--fallback-stem-width=idotless", f"--fallback-stem-width={int(actualStemWidth)}")
		else:
			print(f"Warning: Could not measure stem width of idotless in instance ‘{instance.name}’.")
			return  # do nothing
	instance.customParameters[parameterName] = value


class SetTTFAutohintOptions(mekkaObject):
	prefDict = {
		# ttfautohint options:
		"adjust-subglyphs": "",
		"composites": "",
		"default-script": "latn",
		"dehint": "",
		"detailed-info": "",
		"fallback-script": "latn",
		"fallback-stem-width": "*",
		"hinting-limit": "48",
		"hinting-range-max": "36",
		"hinting-range-min": "",
		"ignore-restrictions": "",
		"increase-x-height": "",
		"no-info": "",
		"strong-stem-width": "gG",
		"stem-width-mode": "qss",
		"symbol": "",
		"ttfa-table": "",
		"windows-compatibility": "",
		"x-height-snapping-exceptions": "",
		"reference": "",

		# script specific:
		"optionValue": "",
		"ttfAutohintOption": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 470
		windowHeight = 110
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set in all ttfautohint options",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		linePos, inset, lineHeight = 12, 15, 38

		# UI elements:
		self.w.helpButton = vanilla.HelpButton((inset - 3, linePos, 21, 20), callback=self.openURL)
		self.w.helpButton.getNSButton().setToolTip_("Opens the ttfAutohint documentation for the currently selected option on freetype.org.")

		self.w.ttfAutohintOption = vanilla.PopUpButton((inset + 23, linePos + 1, 175, 17), availableOptions, callback=self.ttfAutohintOptionAction, sizeStyle='small')
		self.w.ttfAutohintOption.getNSPopUpButton().setToolTip_("Available ttfAutohint options. Pick one from the list. Careful: also contains deprecated options. Refer to the documentation (click on the Help Button on the left), know what you are doing.")

		self.w.optionValue = vanilla.EditText((inset + 205, linePos, -67 - 50, 20), "", callback=self.optionValueAction, sizeStyle='small')
		self.w.optionValue.getNSTextField().setToolTip_("Value for the currently selected option, if any. Some options can only be set or removed, some have a value.")

		# Run Button:
		self.w.runButton = vanilla.Button((-60 - 50, linePos - 2, -inset - 50, 22), "Set", callback=self.SetTTFAutohintOptionsMain)
		self.w.runButton.getNSButton().setToolTip_("Updates all ‘TTFAutohint options’ parameters with the current option (and value, if any) to all instances in the font.")

		self.w.delButton = vanilla.Button((-60, linePos - 2, -inset, 22), "Del", callback=self.RemoveOption)
		self.w.delButton.getNSButton().setToolTip_("Removes the current option from all ‘TTFAutohint options’ parameters in all instances in the font.")

		linePos += lineHeight
		self.w.explanation = vanilla.TextBox((inset, 40, -inset, -5), "Adds or sets this option in all ‘TTFAutohint options’ parameters in the current font. For fallback-stem-width, use * for entering the respective instance weight value, and idotless for measuring the width of the interpolated dotless i. The Del button removes this TTFA option from all instances.", sizeStyle='small')

		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()
		self.editValueField()
		# enable or disable the edit box
		# self.editValueField()


		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()


	def LoadPreferences(self):
		try:
			self.w.ttfAutohintOption.set(self.pref("ttfAutohintOption"))
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
		except:
			import traceback
			print(traceback.format_exc())
			print(f"⚠️ ‘{self.__class__.__name__}’ could not load preferences. Will resort to defaults.")


	def openURL(self, sender):
		URL = None
		if sender == self.w.helpButton:
			URL = "https://www.freetype.org/ttfautohint/doc/ttfautohint.html"
			currentlySelectedOption = self.w.ttfAutohintOption.getItem()
			if currentlySelectedOption in availableOptionsDict.keys():
				urlExtension = availableOptionsDict[currentlySelectedOption]
				if urlExtension:
					URL = f"{URL}#{urlExtension}"
		if URL:
			import webbrowser
			webbrowser.open(URL)

	def editValueField(self):
		optionName = self.currentOptionName()
		if optionName in valuelessOptions:
			self.w.optionValue.enable(onOff=False)
			self.w.optionValue.set("")
		else:
			self.w.optionValue.enable(onOff=True)
			ttfAutohintOption = self.domain(optionName)
			self.w.optionValue.set(Glyphs.defaults[ttfAutohintOption])

	def currentOptionName(self):
		optionIndex = self.pref("ttfAutohintOption")
		if optionIndex is None:
			optionIndex = 0
			self.setPref("ttfAutohintOption", 0)
		optionName = availableOptions[int(optionIndex)]
		return optionName

	def ttfAutohintOptionAction(self, sender):
		self.setPref("ttfAutohintOption", self.w.ttfAutohintOption.get())
		# picked an option from the pop-up, populate value field:
		self.editValueField()

	def optionValueAction(self, sender):
		self.setPref("optionValue", self.w.optionValue.get())
		# store entered value in prefs:
		ttfAutohintOption = self.domain(self.currentOptionName())  # f"com.mekkablue.SetTTFAutohintOptions.{self.currentOptionName()}"
		Glyphs.defaults[ttfAutohintOption] = self.w.optionValue.get()

	def RemoveOption(self, sender):
		try:
			optionIndex = self.prefInt("ttfAutohintOption")
			optionName = availableOptions[optionIndex]
			for thisInstance in Glyphs.font.instances:
				if thisInstance.customParameters[parameterName]:
					removeFromAutohintOptions(thisInstance, optionName)
					print(f"Removing {optionName} from instance '{thisInstance.name}'.")
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Set ttfautohint Options Error: {e}")
			import traceback
			print(traceback.format_exc())

	def SetTTFAutohintOptionsMain(self, sender):
		try:
			optionIndex = self.prefInt("ttfAutohintOption")
			optionName = availableOptions[optionIndex]
			enteredValue = Glyphs.defaults[f"com.mekkablue.SetTTFAutohintOptions.{optionName}"]

			firstDoc = Glyphs.orderedDocuments()[0]
			if firstDoc.fileType() != "com.glyphsapp.glyphsproject":
				thisFont = firstDoc.font
				if Glyphs.versionNumber >= 3:
					instances = thisFont.instances
				else:
					instances = thisFont.instances()  # GLYPHS 2
			else:  # frontmost = project file
				thisFont = firstDoc.font()
				if Glyphs.versionNumber >= 3:
					instances = firstDoc.instances
				else:
					instances = firstDoc.instances()  # GLYPHS 2

			if enteredValue != "" or optionName in valuelessOptions:
				for thisInstance in instances:
					if thisInstance.type == INSTANCETYPEVARIABLE:
						continue
					if thisInstance.customParameters[parameterName] is not None:
						optionDict = ttfAutohintDict(thisInstance.customParameters[parameterName])
						optionDict[optionName] = enteredValue
						writeOptionsToInstance(optionDict, thisInstance)
						print(f"Set {optionName} in instance '{thisInstance.name}'.")
					else:
						print(f"No ttfautohint parameter in instance '{thisInstance.name}'. {optionName} not set.")
			else:
				Message("Script Error", "Illegal value entered.", OKButton=None)

			# self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Set ttfautohint Options Error: {e}")
			import traceback
			print(traceback.format_exc())


SetTTFAutohintOptions()
