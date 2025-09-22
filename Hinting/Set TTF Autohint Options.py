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
from GlyphsApp import Glyphs, Message, INSTANCETYPEVARIABLE
from mekkablue import mekkaObject
from ttfautohintoptions import parameterName, valuelessOptions, availableOptionsDict, availableOptions, removeFromAutohintOptions, dictToParameterValue, ttfAutohintDict, glyphInterpolation, idotlessMeasure, writeOptionsToInstance


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
