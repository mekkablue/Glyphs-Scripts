# MenuTitle: OTVAR Maker
__doc__ = """
Creates a variable font setting in Font Info > Exports.
"""

import vanilla
from AppKit import NSColor, NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from string import ascii_letters, digits
from GlyphsApp import Glyphs, GSInstance, INSTANCETYPESINGLE, INSTANCETYPEVARIABLE, Message

if Glyphs.versionNumber < 4.0:
	# Glyphs 3 only had the old name, renamed in Glyphs 4:
	from GlyphsApp import GSPropertyNameVariationsPostScriptNamePrefixKey as GSPropertyNameVariablePostScriptNamePrefixKey
else:
	from GlyphsApp import GSPropertyNameVariablePostScriptNamePrefixKey
from mekkablue import mekkaObject, reportFontName, makeWindowResizable


def shortenPSStyleName(psStyleName):
	shortDict = {
		"Bold": "Bd",
		"Book": "Bk",
		"Black": "Blk",
		"Compressed": "Cm",
		"Condensed": "Cn",
		"Compact": "Ct",
		"Display": "Ds",
		"Extended": "Ex",
		"Heavy": "Hv",
		"Inclined": "Ic",
		"Italic": "It",
		"Kursiv": "Ks",
		"Light": "Lt",
		"Medium": "Md",
		"Nord": "Nd",
		"Narrow": "Nr",
		"Oblique": "Obl",
		"Poster": "Po",
		"Regular": "Rg",
		"Slanted": "Sl",
		"Super": "Su",
		"Thin": "Th",
		"Upright": "Up",
	}
	prefixDict = {
		"Demi": "Dm",
		"Semi": "Sm",
		"Ultra": "Ult",
		"Extra": "X",
	}

	for longWord in shortDict.keys():
		abbreviation = shortDict[longWord]
		psStyleName = psStyleName.replace(longWord, abbreviation)
		psStyleName = psStyleName.replace(longWord.lower(), abbreviation)

	for longWord in prefixDict.keys():
		abbreviation = prefixDict[longWord]
		if psStyleName.endswith(longWord):
			split = -len(longWord)
			psStyleName = psStyleName[:split].replace(longWord, abbreviation) + psStyleName[split:]
		else:
			psStyleName = psStyleName.replace(longWord, abbreviation)

	return psStyleName


def psVersionOfName(name, shorten=False):
	allowedChars = ascii_letters + digits
	psName = "".join([x for x in name if x in allowedChars])
	if shorten:
		psName = shortenPSStyleName(psName)
	return psName


class OTVARMaker(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"suffix": "VF",
		"psSuffix": "Roman",
		"allFonts": True,
		"deletePrevious": True,
		"addFileName": False,
	}

	suffixSuggestions = (
		"VF",
		"Variable",
		"Var",
		"VAR",
		"OTVAR",
	)

	psSuffixSuggestions = (
		"Roman",
		"Upright",
		"Normal",
		"Regular",
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 360
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"OTVAR Maker",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Add Variable Font Setting in Font Info > Exports:", sizeStyle="small", selectable=True)

		self.w.suffixText = vanilla.TextBox("auto", "Family name suffix", sizeStyle="small", selectable=True)
		self.w.suffix = vanilla.ComboBox("auto", self.suffixSuggestions, sizeStyle="small", callback=self.SavePreferences)
		tooltip = "This is the extension that will be added to your OTVAR family name in order to differentiate it from the static family name."
		self.w.suffixText.setToolTip(tooltip)
		self.w.suffix.setToolTip(tooltip)

		self.w.psSuffixText = vanilla.TextBox("auto", "Non-italic PS extension", sizeStyle="small", selectable=True)
		self.w.psSuffix = vanilla.ComboBox("auto", self.psSuffixSuggestions, sizeStyle="small", callback=self.SavePreferences)
		tooltip = "Only applies to fonts that are entirely non-italic. The Variations PostScript Name Prefix (nameID 25) should have an extension like Roman or Regular to differentiate it clearly from a pure Italic. Important for setups where uprights and italics are in different files. Also has an effect on the file name if you use that option (see below)."
		self.w.psSuffixText.setToolTip(tooltip)
		self.w.psSuffix.setToolTip(tooltip)

		self.w.addFileName = vanilla.CheckBox("auto", "Add fileName parameter", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.addFileName.setToolTip("Adds a custom parameter for overriding the default file name of the font file.")

		self.w.deletePrevious = vanilla.CheckBox("auto", "⚠️ Remove previous variable font settings", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.deletePrevious.setToolTip("Deletes all variable font settings that you may already have in your file(s).")

		self.w.allFonts = vanilla.CheckBox("auto", "Apply to ⚠️ ALL open fonts", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.setToolTip("Adds Variable Font Settings to all fonts currently open in Glyphs.")

		# Status line and Run Button:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.runButton = vanilla.Button("auto", "Add", callback=self.OTVARMakerMain)
		self.w.runButton.setToolTip("Adds a variable font setting to Font Info > Exports of the chosen fonts.")
		self.w.setDefaultButton(self.w.runButton)

		# the status line takes the leftover width, the button stays as wide as its title needs:
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned, hug their text and share one width:
		for labelName in ("suffixText", "psSuffixText"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[suffixText]-gap-[suffix]-inset-|",
				"H:|-inset-[psSuffixText]-gap-[psSuffix]-inset-|",
				"H:|-inset-[addFileName]-(>=inset)-|",
				"H:|-inset-[deletePrevious]-(>=inset)-|",
				"H:|-inset-[allFonts]-(>=inset)-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[suffix]-row-[psSuffix]-sectionGap-[addFileName]-checkRow-[deletePrevious]-checkRow-[allFonts]-inset-[runButton]-inset-|",
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.suffixText, "attribute1": "centerY", "view2": self.w.suffix, "attribute2": "centerY"},
				{"view1": self.w.psSuffixText, "attribute1": "centerY", "view2": self.w.psSuffix, "attribute2": "centerY"},
				{"view1": self.w.psSuffixText, "attribute1": "width", "view2": self.w.suffixText, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "headlineGap": 10, "sectionGap": 12, "checkRow": 5},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		enable = bool(self.pref("suffix").strip())
		self.w.runButton.enable(enable)

	def OTVARMakerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			suffix = self.pref("suffix")
			psSuffix = self.pref("psSuffix")
			allFonts = self.pref("allFonts")
			deletePrevious = self.pref("deletePrevious")
			addFileName = self.pref("addFileName")

			if Glyphs.font is None:
				self.setStatus("⚠️ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			self.setStatus(f"🛠️ Processing {len(theseFonts)} font(s)…")
			thisFont = None
			for thisFont in theseFonts:
				reportName = reportFontName(thisFont)
				self.setStatus(f"🔠 {reportName}")
				print(f"OTVAR Maker Report for {reportName}")
				print()

				if len(thisFont.masters) == 1:
					print("⚠️ Font only has one master, are you sure?")
					# continue

				if deletePrevious:
					for i in range(len(thisFont.instances) - 1, -1, -1):
						existingInstance = thisFont.instances[i]
						if existingInstance.type == INSTANCETYPEVARIABLE:
							print(f"🚫 Removing existing VF setting ‘{existingInstance.name}’...")
							del thisFont.instances[i]

				# this does not work (yet):
				# otvarInstance = GSInstance()
				# otvarInstance.type = INSTANCETYPEVARIABLE
				# so we have to do it like this:
				otvarInstance = GSInstance.alloc().initWithType_(INSTANCETYPEVARIABLE)
				otvarInstance.font = thisFont
				otvarInstance.familyName = f"{thisFont.familyName.strip()} {suffix.strip()}".strip()

				# Regular vs. Italic
				allMastersHaveAnAngle = all([m.italicAngle != 0.0 for m in thisFont.masters])
				singleInstanceNames = [i.name for i in thisFont.instances if i.type == INSTANCETYPESINGLE]
				# all() of an empty list is True, so a font without instances must not count as italic:
				allInstancesAreCalledItalic = bool(singleInstanceNames) and all(["Italic" in name for name in singleInstanceNames])
				isItalic = allMastersHaveAnAngle or allInstancesAreCalledItalic
				if isItalic:
					otvarInstance.name = "Italic"
				else:
					otvarInstance.name = "Regular"

				# name ID 25
				psFamilyName = psVersionOfName(otvarInstance.familyName)
				extension = "Italic" if isItalic else psSuffix.strip().replace(" ", "")
				if not psFamilyName.endswith(extension):
					psFamilyName += extension
				otvarInstance.setProperty_value_languageTag_(GSPropertyNameVariablePostScriptNamePrefixKey, psFamilyName, None)

				# file name
				if addFileName:
					fileName = otvarInstance.familyName
					if not fileName.endswith(extension):
						fileName = f"{fileName} {extension}"
					if fileName:
						otvarInstance.customParameters["fileName"] = fileName

				# add VFS to instances:
				print(f"✅ Adding Variable Font Setting ‘{otvarInstance.familyName} {otvarInstance.name}’")
				thisFont.instances.insert(0, otvarInstance)
				thisFont.parent.windowController().showFontInfoWindowWithTabSelected_(2)

			self.setStatus(f"✅ Added variable font settings to {len(theseFonts)} font(s).")
			print("\nDone.")

		except Exception as e:
			self.setStatus(f"❌ Error at {reportFontName(thisFont) if thisFont else 'start'}. Details in Macro Window.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"OTVAR Maker Error: {e}")
			import traceback
			print(traceback.format_exc())


OTVARMaker()
