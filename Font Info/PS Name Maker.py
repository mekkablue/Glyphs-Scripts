# MenuTitle: PS Name Maker
__doc__ = """
Creates postscriptFontName entries (Name ID 6) for all instances with options to shorten them.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from string import ascii_letters, digits
from GlyphsApp import Glyphs, GSDocument, GSProjectDocument, INSTANCETYPESINGLE, Message
from mekkablue import mekkaObject


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


def removePSNameFromInstance(i, key="postscriptFontName"):
	for cpIndex in range(len(i.customParameters) - 1, -1, -1):
		cp = i.customParameters[cpIndex]
		if cp.name == "Name Table Entry" and cp.value.split(";")[0].split()[:1] == ["6"]:
			del i.customParameters[cpIndex]

	while i.propertyForName_(key):
		i.removeObjectFromProperties_(i.propertyForName_(key))


def familyNameForInstance(instance):
	if isinstance(instance.font, GSProjectDocument):
		return instance.font.font().familyName
	else:
		return instance.font.familyName


def addPSNameToInstance(i, shorten=False, asCustomParameter=True):
	allowedChars = ascii_letters + digits
	familyName = i.familyName
	if not familyName:
		familyName = familyNameForInstance(i)
	psFamilyName = "".join([x for x in familyName if x in allowedChars])
	psStyleName = "".join([x for x in i.name if x in allowedChars])
	if shorten:
		psStyleName = shortenPSStyleName(psStyleName)
	psFontName = f"{psFamilyName}-{psStyleName}"

	removePSNameFromInstance(i)

	if asCustomParameter:
		i.customParameters["Name Table Entry"] = f"6; {psFontName}"
	else:
		i.fontName = psFontName

	print(f"✅ {familyName} {i.name}: {psFontName}")


class PSNameMaker(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"addAsNameEntryParameter": 1,
		"shortenStyleNames": 1,
		"allFonts": 0,
		"includeInactiveInstances": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"PS Name Maker",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Recalculates and resets PS Names in instances:", sizeStyle="small", selectable=True)

		self.w.addAsNameEntryParameter = vanilla.CheckBox("auto", "Add as custom parameter (OTVAR safe)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.addAsNameEntryParameter.setToolTip("If enabled, will add the PS name as a ‘Name Table Entry’ custom parameter, which also survives variable font export. Otherwise, will set the font name (PostScript name) of the instance.")

		self.w.shortenStyleNames = vanilla.CheckBox("auto", "Shorten style names (Tech Note #5088)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.shortenStyleNames.setToolTip("If enabled, will abbreviate style names in the PS names according to Adobe’s Font Tech Note #5088.")
		self.w.helpButton = vanilla.HelpButton("auto", callback=self.openURL)
		self.w.helpButton.setToolTip("Opens Adobe’s Font Tech Note #5088 on font names in your web browser.")

		self.w.allFonts = vanilla.CheckBox("auto", "Apply to ⚠️ ALL open documents", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.setToolTip("If enabled, will process all open documents. Otherwise, only the frontmost one.")

		self.w.includeInactiveInstances = vanilla.CheckBox("auto", "Include inactive instances", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeInactiveInstances.setToolTip("If enabled, will also process instances that are deactivated. Otherwise, only the active ones.")

		self.w.removeButton = vanilla.Button("auto", "Remove", callback=self.PSNameMakerMain)
		self.w.removeButton.setToolTip("Removes the PS names from the instances instead of adding them.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Add", callback=self.PSNameMakerMain)
		self.w.runButton.setToolTip("Calculates and adds PS names to the instances.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[addAsNameEntryParameter]-(>=inset)-|",
				"H:|-inset-[shortenStyleNames]-gap-[helpButton]-(>=inset)-|",
				"H:|-inset-[allFonts]-(>=inset)-|",
				"H:|-inset-[includeInactiveInstances]-(>=inset)-|",
				"H:|-inset-[removeButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[addAsNameEntryParameter]-stackRow-[shortenStyleNames]-stackRow-[allFonts]-stackRow-[includeInactiveInstances]-inset-[runButton]-inset-|",
				"V:[removeButton]-inset-|",
				{"view1": self.w.helpButton, "attribute1": "centerY", "view2": self.w.shortenStyleNames, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "headlineGap": 10, "stackRow": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def openURL(self, sender=None):
		from webbrowser import open as openURL
		url = "https://github.com/adobe-type-tools/font-tech-notes/blob/main/pdfs/5088.FontNames.pdf"
		openURL(url)

	def PSNameMakerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			includeInactiveInstances = self.pref("includeInactiveInstances")
			shortenStyleNames = self.pref("shortenStyleNames")
			remove = sender == self.w.removeButton
			addAsNameEntryParameter = self.pref("addAsNameEntryParameter")

			theseDocs = Glyphs.orderedDocuments()
			if not theseDocs:
				Message(title="No Font Open", message="The script requires a font or project document. Open a font and run the script again.", OKButton=None)
			else:
				if not self.pref("allFonts"):
					theseDocs = (theseDocs[0], )

				for thisDoc in theseDocs:
					if isinstance(thisDoc, GSProjectDocument):
						thisFont = thisDoc.font()
						instances = thisDoc.instances
						filePath = thisDoc.fileURL()
					elif isinstance(thisDoc, GSDocument):
						thisFont = thisDoc.font
						instances = thisFont.instances
						filePath = thisFont.filepath
					else:
						continue

					if filePath:
						reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
					else:
						reportName = f"{thisFont.familyName} (unsaved)"
					print(f"PS Name Maker Report for {reportName}")
					print()
					for thisInstance in instances:
						if thisInstance.type == INSTANCETYPESINGLE:
							if includeInactiveInstances or thisInstance.active:
								if remove:
									removePSNameFromInstance(thisInstance)
									print(f"⌦ ‘{thisInstance.name}’ cleared of PS Names.")
								else:
									addPSNameToInstance(thisInstance, shorten=shortenStyleNames, asCustomParameter=addAsNameEntryParameter)
							else:
								print(f"⏭️ ‘{thisInstance.name}’ is inactive: skipping.")
					print()

			print("Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"PS Name Maker Error: {e}")
			import traceback
			print(traceback.format_exc())


PSNameMaker()
