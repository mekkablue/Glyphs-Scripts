# MenuTitle: Prepare Font Info
__doc__ = """
Prepare open fonts for a modern font production and git workflow.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


class PrepareFontforGit(mekkaObject):
	prefDict = {
		"preventDisplayStrings": False,
		"preventTimeStamps": False,
		"preventMacName": False,
		"fileFormat": False,
		"fileFormatVersion": 0,  # 0 = Glyphs version 3, 1 = Glyphs version 4
		"useExtensionKerning": False,
		"removeGlyphOrder": False,
		"applyToFonts": False,
		"disablesNiceNames": False,
		"disablesAutomaticAlignment": False,
	}
	parameterDict = {
		"preventDisplayStrings": ("Write DisplayStrings", 0),
		"preventTimeStamps": ("Write lastChange", 0),
		"preventMacName": ("Export Mac Name Table Entries", 0),
		"useExtensionKerning": ("Use Extension Kerning", True),
	}

	removeParameters = ("glyphOrder", )

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Prepare File",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		checkBoxNames = (
			"preventDisplayStrings",
			"preventTimeStamps",
			"preventMacName",
			"fileFormat",
			"useExtensionKerning",
			"removeGlyphOrder",
			"disablesNiceNames",
			"disablesAutomaticAlignment",
		)

		self.w.descriptionText = vanilla.TextBox("auto", "Make the font git-ready with these custom parameters:", sizeStyle="small", selectable=True)

		self.w.preventDisplayStrings = vanilla.CheckBox("auto", "Prevent storing of tab contents (Write DisplayStrings = OFF)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.preventTimeStamps = vanilla.CheckBox("auto", "Prevent storing of time stamps (Write lastChange = OFF)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.preventMacName = vanilla.CheckBox("auto", "Prevent export of Mac entries in name table", value=True, callback=self.SavePreferences, sizeStyle="small")

		fileFormatTooltip = "Sets Font Info > Other > File Format to the chosen Glyphs version."
		self.w.fileFormat = vanilla.CheckBox("auto", "Set File Format to", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.fileFormat.setToolTip(fileFormatTooltip)
		self.w.fileFormatVersion = vanilla.PopUpButton("auto", ("Glyphs version 3", "Glyphs version 4"), callback=self.SavePreferences, sizeStyle="small")
		self.w.fileFormatVersion.setToolTip(fileFormatTooltip)

		self.w.useExtensionKerning = vanilla.CheckBox("auto", "Add Use Extension Kerning parameter", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.useExtensionKerning.setToolTip("Adds the ‘Use Extension Kerning’ custom parameter, which makes the exported kern feature use the GPOS Extension lookup type. Useful for large kerning tables.")
		self.w.removeGlyphOrder = vanilla.CheckBox("auto", "Remove glyphOrder", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.disablesNiceNames = vanilla.CheckBox("auto", "Turn off Font Info > Other > Use Custom Naming", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.disablesAutomaticAlignment = vanilla.CheckBox("auto", "Turn off Font Info > Other > Disable Auto Alignment", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Apply Scope:
		self.w.applyToFontsText = vanilla.TextBox("auto", "Apply to:", sizeStyle="small", selectable=True)
		self.w.applyToFonts = vanilla.PopUpButton("auto", ("frontmost font only", "⚠️ ALL open fonts"), sizeStyle="small", callback=self.SavePreferences)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Apply", callback=self.PrepareFontforGitMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.applyToFontsText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		rules = ["H:|-inset-[descriptionText]-(>=inset)-|"]
		rules += [f"H:|-inset-[{name}]-(>=inset)-|" for name in checkBoxNames if name != "fileFormat"]
		rules += [
			"H:|-inset-[fileFormat]-gap-[fileFormatVersion]-(>=inset)-|",
			"H:|-inset-[applyToFontsText]-gap-[applyToFonts]-gap-[runButton(>=70)]-inset-|",
		]
		verticalChain = "V:|-gap-[descriptionText]"
		for name in checkBoxNames:
			verticalChain += f"-checkRow-[{name}]"
		verticalChain += "-inset-[applyToFonts]-inset-|"
		rules.append(verticalChain)
		rules += [
			{"view1": self.w.fileFormatVersion, "attribute1": "centerY", "view2": self.w.fileFormat, "attribute2": "centerY"},
			{"view1": self.w.applyToFontsText, "attribute1": "centerY", "view2": self.w.applyToFonts, "attribute2": "centerY"},
			{"view1": self.w.runButton, "attribute1": "centerY", "view2": self.w.applyToFonts, "attribute2": "centerY"},
		]
		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "checkRow": 5})

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		optionNames = [prefName for prefName in self.prefDict.keys() if prefName not in ("applyToFonts", "fileFormatVersion")]
		onOff = any([self.pref(prefName) for prefName in optionNames])
		self.w.applyToFonts.enable(onOff)
		self.w.runButton.enable(onOff)
		self.w.fileFormatVersion.enable(self.pref("fileFormat"))

	def setParameterForFont(self, font, parameterName, parameterValue=0, remove=False):
		while font.customParameters[parameterName]:
			del font.customParameters[parameterName]

		if remove:
			print("🚫 Font Info > Font > Custom Parameters > %s" % parameterName)
		else:
			font.customParameters[parameterName] = parameterValue
			print("✅ Font Info > Font > Custom Parameters > %s = %s" % (parameterName, parameterValue))

	def PrepareFontforGitMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if len(Glyphs.fonts) == 0:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				applyToFonts = self.pref("applyToFonts")

				if applyToFonts == 1:
					theseFonts = Glyphs.fonts
				else:
					theseFonts = (Glyphs.font, )

				for thisFont in theseFonts:
					print(f"🧑🏽‍💻 Prepare Font for Git: {thisFont.familyName}")
					if thisFont.filepath:
						print(f"📄 {thisFont.filepath}")
					else:
						print("⚠️ The font file has not been saved yet.")

					# set parameters:
					for optionKey in self.parameterDict.keys():
						if self.prefBool(optionKey):
							parameterName, parameterValue = self.parameterDict[optionKey]
							self.setParameterForFont(thisFont, parameterName, parameterValue)

					# remove parameters:
					for optionKey in [prefName for prefName in self.prefDict.keys() if prefName.startswith("remove") and self.pref(prefName)]:
						parameterName = optionKey[6].lower() + optionKey[7:]
						self.setParameterForFont(thisFont, parameterName, remove=True)

					# font attributes:
					for optionKey in [prefName for prefName in self.prefDict.keys() if prefName.startswith("disables") and self.pref(prefName)]:
						setattr(thisFont, optionKey, False)
						print(f"✅ Turned off {optionKey.replace('disables', '')} (See Font Info > Other)")

					# set file format:
					if self.pref("fileFormat"):
						targetVersion = 3 + self.prefInt("fileFormatVersion")
						if thisFont.formatVersion != targetVersion:
							thisFont.formatVersion = targetVersion
							print(f"✅ Font Info > Other > File Format: {targetVersion}")
						else:
							print(f"😮‍💨 Font Info > Other > File Format was already {targetVersion}")

					print()

			self.w.close()  # delete if you want window to stay open
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Prepare Font Info Error: %s" % e)
			import traceback
			print(traceback.format_exc())


PrepareFontforGit()
