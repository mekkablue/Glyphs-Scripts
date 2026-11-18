# MenuTitle: Kern String Mixer
__doc__ = """
Intersect two sets of glyphs with each other in order to get all possible glyph combinations.
"""

import vanilla
from mekkablue import mekkaObject, reportFontName
from GlyphsApp import Glyphs, GSFeature, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
	NSWindowStyleMaskResizable,
)
from Foundation import NSSize

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
		# Window 'self.w':
		windowWidth = 420
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Kern String Mixer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Mix glyphs for a new tab of all possible glyph combos:", sizeStyle='small', selectable=True)

		tokenHelpText = "Write a token. Click on the help button for more info."
		self.w.mixString1 = vanilla.ComboBox("auto", defaultTokens, callback=self.SavePreferences)
		self.w.mixString1.setToolTip(tokenHelpText)

		self.w.mixString2 = vanilla.ComboBox("auto", defaultTokens, callback=self.SavePreferences)
		self.w.mixString2.setToolTip(tokenHelpText)

		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')

		# Buttons at bottom:
		self.w.helpTokens = vanilla.HelpButton("auto", callback=self.openURL)
		self.w.runButton = vanilla.Button("auto", "Mix", callback=self.KernStringMixerMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the combo boxes take the window width, however long their tokens are:
		for comboBox in (self.w.mixString1, self.w.mixString2):
			comboBox.getNSComboBox().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[mixString1]-inset-|",
				"H:|-inset-[mixString2]-inset-|",
				"H:|-inset-[reuseTab]-(>=inset)-|",
				"H:|-inset-[helpTokens]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[mixString1]-row-[mixString2]-gap-[reuseTab]-inset-[runButton]-inset-|",
				{"view1": self.w.helpTokens, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# make the window horizontally resizable, but keep the height that Auto Layout determined.
		# (Content sizes set directly on the NSWindow, so the title bar is not counted twice.)
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()  # make sure the content has its final size before we read it
		contentSize = nsWindow.contentView().frame().size
		nsWindow.setContentMinSize_(NSSize(contentSize.width, contentSize.height))
		nsWindow.setContentMaxSize_(NSSize(contentSize.width + 1000, contentSize.height))

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

		if hasattr(GSFeature, "evaluatePredicateToken_font_contextLabel_error_"):
			evaluatedToken = GSFeature.evaluatePredicateToken_font_contextLabel_error_(token, font, "", None)
		else:
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
				report = reportFontName(thisFont)
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
