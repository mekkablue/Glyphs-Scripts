# MenuTitle: Set ttfautohint Options
__doc__ = """
Set options for existing 'TTFAutohint options' Custom Parameters.
"""

import vanilla
from AppKit import NSColor, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut, NSLayoutPriorityRequired
from GlyphsApp import Glyphs, Message, INSTANCETYPEVARIABLE
from mekkablue import mekkaObject, makeWindowResizable
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
		windowWidth = 500
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set in all ttfautohint options",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		inset = 15

		# UI elements:
		self.w.helpButton = vanilla.HelpButton("auto", callback=self.openURL)
		self.w.helpButton.setToolTip("Opens the ttfAutohint documentation for the currently selected option on freetype.org.")

		self.w.ttfAutohintOption = vanilla.PopUpButton("auto", availableOptions, callback=self.ttfAutohintOptionAction, sizeStyle='small')
		self.w.ttfAutohintOption.setToolTip("Available ttfAutohint options. Pick one from the list. Careful: also contains deprecated options. Refer to the documentation (click on the Help Button on the left), know what you are doing.")

		self.w.optionValue = vanilla.EditText("auto", "", callback=self.optionValueAction, sizeStyle='small')
		self.w.optionValue.setToolTip("Value for the currently selected option, if any. Some options can only be set or removed, some have a value.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Set", callback=self.SetTTFAutohintOptionsMain)
		self.w.runButton.setToolTip("Updates all ‘TTFAutohint options’ parameters with the current option (and value, if any) to all instances in the font.")

		self.w.delButton = vanilla.Button("auto", "Del", callback=self.RemoveOption)
		self.w.delButton.setToolTip("Removes the current option from all ‘TTFAutohint options’ parameters in all instances in the font.")

		self.w.explanation = vanilla.TextBox("auto", "Adds or sets this option in all ‘TTFAutohint options’ parameters in the current font. For fallback-stem-width, use * for entering the respective instance weight value, and idotless for measuring the width of the interpolated dotless i. The Del button removes this TTFA option from all instances.", sizeStyle='small')
		# a text block that wraps takes the width it is given, instead of demanding one long line:
		self.w.explanation.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.setDefaultButton(self.w.runButton)

		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")

		# every control hugs vertically, so the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.optionValue.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.ttfAutohintOption.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		# buttons in a row with other elements stay as wide as their titles need:
		for nsButton in (self.w.runButton.getNSButton(), self.w.delButton.getNSButton()):
			nsButton.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsButton.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[helpButton]-gap-[ttfAutohintOption(>=150)]-gap-[optionValue(>=100)]-gap-[runButton(>=50)]-gap-[delButton(>=50)]-inset-|",
				"H:|-inset-[explanation]-inset-|",
				"H:|-inset-[status]-inset-|",
				"V:|-gap-[optionValue]-row-[explanation(56)]-gap-[status]-inset-|",
				{"view1": self.w.helpButton, "attribute1": "centerY", "view2": self.w.optionValue, "attribute2": "centerY"},
				{"view1": self.w.ttfAutohintOption, "attribute1": "centerY", "view2": self.w.optionValue, "attribute2": "centerY"},
				{"view1": self.w.runButton, "attribute1": "centerY", "view2": self.w.optionValue, "attribute2": "centerY"},
				{"view1": self.w.delButton, "attribute1": "centerY", "view2": self.w.optionValue, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 12},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()
		self.editValueField()

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
		currentItem = None
		try:
			thisFont = Glyphs.font
			if not thisFont:
				self.setStatus("⚠️ No font open.")
				Message("No Font Open", "The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			optionIndex = self.prefInt("ttfAutohintOption")
			optionName = availableOptions[optionIndex]
			self.setStatus(f"🛠️ Removing {optionName} from {len(thisFont.instances)} instance(s)…")
			removedCount = 0
			for thisInstance in thisFont.instances:
				currentItem = thisInstance.name
				self.setStatus(f"🔠 {thisInstance.name}")
				if thisInstance.customParameters[parameterName]:
					removeFromAutohintOptions(thisInstance, optionName)
					removedCount += 1
					print(f"Removing {optionName} from instance '{thisInstance.name}'.")
			if removedCount:
				self.setStatus(f"✅ Removed {optionName} from {removedCount} instance(s).")
			else:
				self.setStatus("⚠️ No instances with ttfautohint options.")
		except Exception as e:
			self.setStatus(f"❌ Error at {currentItem or 'start'}. Details in Macro Window.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Set ttfautohint Options Error: {e}")
			import traceback
			print(traceback.format_exc())

	def SetTTFAutohintOptionsMain(self, sender):
		currentItem = None
		try:
			optionIndex = self.prefInt("ttfAutohintOption")
			optionName = availableOptions[optionIndex]
			enteredValue = Glyphs.defaults[f"com.mekkablue.SetTTFAutohintOptions.{optionName}"]

			if not Glyphs.orderedDocuments():
				self.setStatus("⚠️ No font open.")
				Message("No Font Open", "The script requires a font. Open a font and run the script again.", OKButton=None)
				return
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
				self.setStatus(f"🛠️ Setting {optionName} in {len(instances)} instance(s)…")
				setCount = 0
				for thisInstance in instances:
					if thisInstance.type == INSTANCETYPEVARIABLE:
						continue
					currentItem = thisInstance.name
					self.setStatus(f"🔠 {thisInstance.name}")
					if thisInstance.customParameters[parameterName] is not None:
						optionDict = ttfAutohintDict(thisInstance.customParameters[parameterName])
						optionDict[optionName] = enteredValue
						writeOptionsToInstance(optionDict, thisInstance, font=thisFont)
						setCount += 1
						print(f"Set {optionName} in instance '{thisInstance.name}'.")
					else:
						print(f"No ttfautohint parameter in instance '{thisInstance.name}'. {optionName} not set.")
				if setCount:
					self.setStatus(f"✅ Set {optionName} in {setCount} instance(s).")
				else:
					self.setStatus("⚠️ No instances with ttfautohint options.")
			else:
				self.setStatus("❌ Illegal value entered.")
				Message("Script Error", "Illegal value entered.", OKButton=None)

			# self.w.close()  # delete if you want window to stay open
		except Exception as e:
			self.setStatus(f"❌ Error at {currentItem or 'start'}. Details in Macro Window.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Set ttfautohint Options Error: {e}")
			import traceback
			print(traceback.format_exc())


SetTTFAutohintOptions()
