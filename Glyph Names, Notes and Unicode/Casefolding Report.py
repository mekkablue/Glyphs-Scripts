# MenuTitle: Casefolding Report
# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

__doc__ = """
Checks if uppercase and lowercase are matching. Opens a new Edit tab containing all glyphs without consistent casefolding. Writes a detailed report in Macro Window.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


class CasefoldingReport(mekkaObject):
	prefID = "com.mekkablue.CasefoldingReport"
	prefDict = {
		# "prefName": defaultValue,
		"excludeMathSymbols": False,
		"allFonts": True,
		"reuseTab": True,
		"showMacroWindow": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 160
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Casefolding Report",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Report all casefolding issues:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.excludeMathSymbols = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Exclude math symbols (∆∏∑µ)", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Check all open fonts (otherwise frontmost only)", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.reuseTab = vanilla.CheckBox((inset + 2, linePos - 1, 120, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.showMacroWindow = vanilla.CheckBox((inset + 120, linePos - 1, -inset, 20), "Open Macro Window", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Report", sizeStyle="regular", callback=self.CasefoldingReportMain)
		self.w.setDefaultButton(self.w.runButton)

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
					if Glyphs.versionNumber < 4:
						from Foundation import NSHeight
						splitview = Glyphs.delegate().macroPanelController().consoleSplitView()
						frame = splitview.frame()
						height = NSHeight(frame)
						currentPos = splitview.positionOfDividerAtIndex_(0) / height
						if currentPos > 0.3:
							splitview.setPosition_ofDividerAtIndex_(height * 0.2, 0)
			print("✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Casefolding Report Error: {e}")
			import traceback
			print(traceback.format_exc())


CasefoldingReport()
