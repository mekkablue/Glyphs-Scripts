# MenuTitle: Kern String Mixer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Intersect two sets of glyphs with each other in order to get all possible glyph combinations.
"""

import vanilla
from GlyphsApp import Glyphs, GSFeature, Message
from mekkaCore import mekkaObject

defaultTokens = (
	"$[category like 'Letter' and case in {upper,lower}]  # UPPERCASE AND LOWERCASE LETTERS",
	"$[category like 'Number' and case = minor]",
	"$[name like '*superior*' or name like '*inferior*']",
	"$[name like '*.ss??*']  # STYLISTIC SETS",
	"$[case = minor]",
	"$[case = smallCaps]",
	"$[category like 'Punctuation']",
	"$[subCategory in {'Quote','Parenthesis','Dash'}]",
	"$[category like 'Number' and case != minor]",
	"$[subCategory like 'Math']  # MATHEMATICAL OPERATORS",
	"$[category like 'Letter' and case = upper]",
	"$[category like 'Letter' and case = lower]",
	"$[category like 'Letter' and script like 'latin']",
	"$[category like 'Letter' and script like 'cyrillic']",
	"$[category like 'Letter' and script like 'greek']",
)


class KernStringMixer(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"mixString1": defaultTokens[0],
		"mixString2": defaultTokens[1],
		"reuseTab": True,
	}

	def __init__(self):
		for prefName in self.prefDict.keys():
			Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])

		# Window 'self.w':
		windowWidth = 300
		windowHeight = 180
		windowWidthResize = 800  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Kern String Mixer",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Mix glyphs for a new tab of all possible glyph combos:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		tokenHelpText = "Write a token. Click on the help button for more info."
		self.w.mixString1 = vanilla.ComboBox((inset, linePos - 1, -inset, 23), defaultTokens, sizeStyle='regular', callback=self.SavePreferences)
		self.w.mixString1.getNSComboBox().setToolTip_(tokenHelpText)
		linePos += lineHeight + 7

		self.w.mixString2 = vanilla.ComboBox((inset, linePos - 1, -inset, 23), defaultTokens, sizeStyle='regular', callback=self.SavePreferences)
		self.w.mixString2.getNSComboBox().setToolTip_(tokenHelpText)
		linePos += lineHeight + 7

		self.w.reuseTab = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Reuse current tab", value=self.pref("reuseTab"), callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Buttons at bottom:
		self.w.helpTokens = vanilla.HelpButton((inset, -20 - inset, 24, 21), callback=self.openURL)
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Mix", sizeStyle='regular', callback=self.KernStringMixerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def openURL(self, sender=None):
		URL = None
		if sender == self.w.helpTokens:
			URL = "https://www.glyphsapp.com/learn/tokens"
		if URL:
			import webbrowser
			webbrowser.open(URL)

	def expandToken(self, token, font=None):
		print("Token: %s" % token)

		# clean up token:
		if "#" in token:
			token = token[:token.find("#")]
		token = token.strip()
		if token.startswith("$[") and token.endswith("]"):
			token = token[2:-1]

		# check for font:
		if not font:
			font = Glyphs.font
			if not font:
				return ""

		evaluatedToken = GSFeature.evaluatePredicateToken_font_error_(token, font, None)
		print("Evaluation: %s\n" % evaluatedToken)
		return evaluatedToken

	def KernStringMixerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					report = "%s\n📄 %s" % (filePath.lastPathComponent(), filePath)
				else:
					report = "%s\n⚠️ The font file has not been saved yet." % thisFont.familyName
				print("Kern String Mixer Report for %s" % report)
				print()

				tabText = ""
				aa = self.expandToken(self.pref("mixString1"), font=thisFont)
				bb = self.expandToken(self.pref("mixString2"), font=thisFont)
				if not aa or not bb:
					errorMessage = ""
					if not aa:
						errorMessage = " 1"
						if not bb:
							errorMessage = "s 1 and 2"
					elif not bb:
						errorMessage = " 2"

					Message(
						title="Token Error",
						message="Token%s evaluate%s to nothing for frontmost font ‘%s’" % (
							errorMessage,
							"s" if errorMessage[0] == " " else "",
							thisFont.familyName,
						),
						OKButton=None,
					)
					return

				aa = aa.split()
				bb = bb.split()
				for a in aa:
					for b in bb:
						tabText += "/" + a
						tabText += "/" + b
					tabText += "/" + a
					tabText += "\n"

				thisTab = thisFont.currentTab
				if not thisTab or not self.pref("reuseTab"):
					thisTab = thisFont.newTab()
				thisTab.scale = 0.05
				thisTab.text = tabText
				thisTab.previewHeight = 0
				thisTab.updatePreview()

				self.w.close()  # delete if you want window to stay open

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Kern String Mixer Error: %s" % e)
			import traceback
			print(traceback.format_exc())


KernStringMixer()
