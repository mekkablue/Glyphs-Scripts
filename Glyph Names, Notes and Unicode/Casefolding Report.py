# MenuTitle: Casefolding Report
__doc__ = """
Checks if uppercase and lowercase are matching. Opens a new Edit tab containing all glyphs without consistent casefolding. Writes a detailed report in Macro Window.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, macroDividerPosition, setMacroDivider


class CasefoldingReport(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"excludeMathSymbols": False,
		"allFonts": True,
		"reuseTab": True,
		"showMacroWindow": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Casefolding Report",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Report all casefolding issues:", sizeStyle="small", selectable=True)

		self.w.excludeMathSymbols = vanilla.CheckBox("auto", "Exclude math symbols (∆∏∑µ)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.excludeMathSymbols.setToolTip("If enabled, will not report math symbols like ∆, ∏, ∑ and µ, which are uppercase or lowercase only by Unicode convention.")
		self.w.allFonts = vanilla.CheckBox("auto", "Check all open fonts (otherwise frontmost only)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.setToolTip("If enabled, will check all open fonts. Otherwise, only the frontmost font.")
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.setToolTip("If enabled, will show the glyphs in the current Edit tab. Otherwise, will open a new tab.")
		self.w.showMacroWindow = vanilla.CheckBox("auto", "Open Macro Window", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.showMacroWindow.setToolTip("If enabled, will bring the Macro Window to the front to show the detailed report.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Report", callback=self.CasefoldingReportMain)
		self.w.runButton.setToolTip("Checks the casefolding and reports the glyphs with inconsistent casing in a tab and in the Macro Window.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[excludeMathSymbols]-(>=inset)-|",
				"H:|-inset-[allFonts]-(>=inset)-|",
				"H:|-inset-[reuseTab]-gap-[showMacroWindow]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-row-[excludeMathSymbols]-checkRow-[allFonts]-checkRow-[reuseTab]-inset-[runButton]-inset-|",
				{"view1": self.w.showMacroWindow, "attribute1": "centerY", "view2": self.w.reuseTab, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def CasefoldingReportMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if Glyphs.font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				allFonts = self.pref("allFonts")
				reuseTab = self.pref("reuseTab")
				showMacroWindow = self.pref("showMacroWindow")
				excludeMathSymbols = self.pref("excludeMathSymbols")

				def cleanUpName(name):
					convert = {
						"i_dotaccentcomb": "i",
						"SS": "Germandbls",
					}
					if name in convert.keys():
						name = convert[name]
					return name

				def hexCode(char):
					return f"{ord(char):04X}"

				def glyphForCharacter(char, font):
					unicodeValue = hexCode(char)
					glyph = font.localGlyphForUnicode_(unicodeValue)
					return glyph

				if allFonts:
					theseFonts = Glyphs.fonts
				else:
					theseFonts = (Glyphs.font,)
				print(f"Casefolding report for {len(theseFonts)} font{'' if len(theseFonts) == 1 else 's'}:\n")

				allFontsClear = []
				for thisFont in theseFonts:
					if thisFont.filepath:
						print(f"📄 {thisFont.filepath.lastPathComponent()}\n")
					else:
						print(f"📃 {thisFont.familyName} (⚠️ file not saved)\n")

					# collect all unicodes:
					unicodeDict = {}
					for g in thisFont.glyphs:
						if g.unicodes:
							for code in g.unicodes:
								unicodeDict[code] = g.name

								# print(unicodeDict)
					def isEncoded(code):
						if code in unicodeDict.keys():
							return True
						return False

					tabString = ""
					for g in thisFont.glyphs:
						char = g.charString()
						if g.subCategory == "Ligature":
							continue
						shouldBeSkipped = g.subCategory == "Math" and excludeMathSymbols
						if char.isupper():
							lowerCaseChar = char.lower()
							lowerCaseName = cleanUpName(Glyphs.niceGlyphName(lowerCaseChar))
							lowerCaseGlyph = thisFont.glyphs[lowerCaseName]
							if lowerCaseName:
								if not lowerCaseGlyph:
									lowerCaseCode = hexCode(lowerCaseChar)
									if not isEncoded(lowerCaseCode):
										print(f"  {'ℹ️' if shouldBeSkipped else '⚠️'} 🔠 {g.name}: 🔡 {lowerCaseName} missing {' (math symbol)' if shouldBeSkipped else ''}")
										if not shouldBeSkipped:
											tabString += f"/{g.name}"
									else:
										print(f"  ✅ 🔠 {g.name}: lowercase encoded in {unicodeDict[lowerCaseCode]}")
								elif g.export and not lowerCaseGlyph.export:
									print(f"  ⚠️ Export status: 🔠☑️ {g.name} 🔡🚫 {lowerCaseName}")
									tabString += f"/{g.name}/{lowerCaseName}"
						if char.islower():
							upperCaseChar = char.upper()
							upperCaseName = cleanUpName(Glyphs.niceGlyphName(upperCaseChar))
							upperCaseGlyph = thisFont.glyphs[upperCaseName]
							if upperCaseName:
								if not upperCaseGlyph:
									upperCaseCode = hexCode(upperCaseChar)
									if not isEncoded(upperCaseCode):
										print(f"  {'ℹ️' if shouldBeSkipped else '⚠️'} 🔡 {g.name}: 🔠 {upperCaseName} missing {' (math symbol)' if shouldBeSkipped else ''}")
										if not shouldBeSkipped:
											tabString += f"/{g.name}"
									else:
										print(f"  ✅ 🔡 {g.name}: uppercase ({upperCaseCode}) encoded in {unicodeDict[upperCaseCode]}")
								elif g.export and not upperCaseGlyph.export:
									print(f"  ⚠️ Export status: 🔡☑️ {g.name} 🔠🚫 {upperCaseName}")
									tabString += f"/{g.name}/{upperCaseName}"
					print()
					if tabString:
						allFontsClear.append(False)
						if thisFont.currentTab and reuseTab:
							thisFont.currentTab.text = tabString
						else:
							thisFont.newTab(tabString)
					else:
						allFontsClear.append(True)

				if all(allFontsClear):
					Message("No issues found. Details in Macro Window.", title='Casefolding OK', OKButton="🥂 Cheers!")
				if showMacroWindow:
					Glyphs.showMacroWindow()
					currentPos = macroDividerPosition()
					if currentPos is not None and currentPos > 0.3:
						setMacroDivider(0.2)
			print("✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Casefolding Report Error: {e}")
			import traceback
			print(traceback.format_exc())


CasefoldingReport()
