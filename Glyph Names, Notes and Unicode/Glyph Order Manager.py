# MenuTitle: Glyph Order Manager
__doc__ = """
UI for managing glyphOrder parameters.
"""

import codecs
import vanilla
from mekkablue import mekkaObject, getLegibleFont, reportFontName, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut


def saveFileInLocation(content="", filePath="~/Desktop/test.txt"):
	with codecs.open(filePath, "w", "utf-8-sig") as thisFile:
		print("💾 Writing:", thisFile.name)
		thisFile.write(content)
		thisFile.close()
	return True


def readFileFromLocation(filePath="~/Desktop/test.txt"):
	content = ""
	with codecs.open(filePath, "r", "utf-8-sig") as thisFile:
		print("💾 Reading:", thisFile.name)
		content = thisFile.read()
		thisFile.close()
	return content


class GlyphOrderManager(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"glyphOrderText": "",
		"scope": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 380
		windowHeight = 260
		# the window stays resizable, because the user needs to enlarge the text editor
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Glyph Order Manager",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Content of glyphOrder parameter:", sizeStyle="small", selectable=True)

		self.w.glyphOrderText = vanilla.TextEditor("auto", text="", callback=self.SavePreferences, checksSpelling=False)
		self.w.glyphOrderText.getNSScrollView().setHasVerticalScroller_(1)
		self.w.glyphOrderText.getNSScrollView().setHasHorizontalScroller_(1)
		self.w.glyphOrderText.getNSScrollView().setRulersVisible_(0)

		legibleFont = getLegibleFont()

		textView = self.w.glyphOrderText.getNSTextView()
		textView.setFont_(legibleFont)
		textView.setUsesFindBar_(True)
		textView.setToolTip_("Extract, edit, and reapply glyphOrder text to custom parameters.")
		textView.setHorizontallyResizable_(1)
		textView.setVerticallyResizable_(1)
		textView.setAutomaticDataDetectionEnabled_(1)
		textView.setAutomaticLinkDetectionEnabled_(1)
		textView.setDisplaysLinkToolTips_(1)
		textSize = textView.minSize()
		textSize.width = 1000
		textView.setMinSize_(textSize)

		scopeOptions = (
			"frontmost font only",
			"⚠️ all open fonts",
		)
		self.w.scopeText = vanilla.TextBox("auto", "Apply to:", selectable=True)
		self.w.scope = vanilla.PopUpButton("auto", scopeOptions, callback=self.SavePreferences)

		# Run Button:
		self.w.extractButton = vanilla.Button("auto", "Extract", callback=self.extractFromFrontmostFont)
		self.w.cleanButton = vanilla.Button("auto", "Clean", callback=self.cleanForScope)
		self.w.addMissingButton = vanilla.Button("auto", "Add Missing", callback=self.addMissingForScope)

		self.w.runButton = vanilla.Button("auto", "Apply", callback=self.GlyphOrderManagerMain)
		self.w.setDefaultButton(self.w.runButton)

		# everything hugs vertically, except for the text editor, which takes the leftover height:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		self.w.glyphOrderText.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)
		self.w.scopeText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-0-[glyphOrderText]-0-|",
				"H:|-inset-[scopeText]-gap-[scope]-inset-|",
				"H:|-inset-[extractButton(>=70)]-gap-[cleanButton(>=70)]-gap-[addMissingButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-gap-[glyphOrderText(>=100)]-gap-[scope]-inset-[runButton]-inset-|",
				"V:[extractButton]-inset-|",
				"V:[cleanButton]-inset-|",
				"V:[addMissingButton]-inset-|",
				{"view1": self.w.scopeText, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8},
		)

		makeWindowResizable(self.w, vertical=True)  # resizable, limits in content sizes

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def requestedFonts(self):
		scope = self.prefInt("scope")
		if not Glyphs.fonts or not Glyphs.font:
			return None
		if scope == 0:
			return (Glyphs.font, )
		elif scope == 1:  # all fonts
			return Glyphs.fonts
		return None

	def extractFromFrontmostFont(self, sender=None):
		font = Glyphs.font
		if not font:
			return
		glyphOrder = font.customParameters["glyphOrder"]
		if glyphOrder:
			Glyphs.defaults[self.domain("glyphOrderText")] = "\n".join(glyphOrder)
			self.LoadPreferences()
		else:
			Message(
				title="No glyphOrder",
				message=f"The frontmost font, {font.familyName}, has no glyphOrder parameter.",
				OKButton=None,
			)

	def cleanForScope(self, sender=None):
		fonts = self.requestedFonts()
		if fonts:
			currentText = self.pref("glyphOrderText")
			currentGlyphs = currentText.strip().splitlines()
			relevantGlyphs = []
			for currentGlyph in currentGlyphs:
				if any([f.glyphs[currentGlyph] is not None for f in fonts]):
					relevantGlyphs.append(currentGlyph)
			Glyphs.defaults[self.domain("glyphOrderText")] = "\n".join(relevantGlyphs)
			self.LoadPreferences()

	def addMissingForScope(self, sender=None):
		fonts = self.requestedFonts()
		if fonts:
			currentText = self.pref("glyphOrderText")
			glyphs = currentText.strip().splitlines()
			for font in fonts:
				for g in font.glyphs:
					if g.name not in glyphs:
						glyphs.append(g.name)
			Glyphs.defaults[self.domain("glyphOrderText")] = "\n".join(glyphs)
			self.LoadPreferences()

	def GlyphOrderManagerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			glyphOrderText = self.pref("glyphOrderText")
			glyphOrder = list([n.strip() for n in glyphOrderText.splitlines() if n.strip()])

			fonts = self.requestedFonts()  # frontmost font
			if fonts is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				for thisFont in fonts:
					reportName = reportFontName(thisFont)
					print(f"🔢 Setting glyphOrder for {reportName}")
					print()
					thisFont.disableUpdateInterface()
					thisFont.customParameters["glyphOrder"] = glyphOrder
					thisFont.enableUpdateInterface()

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Glyph Order Manager Error: {e}")
			import traceback
			print(traceback.format_exc())


GlyphOrderManager()
