# MenuTitle: Glyph Order Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
UI for managing glyphOrder parameters.
"""

import vanilla
import codecs
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, getLegibleFont


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
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 1000  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Glyph Order Manager",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Content of glyphOrder parameter:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.glyphOrderText = vanilla.TextEditor((1, linePos, -1, -inset * 5), text="", callback=self.SavePreferences, checksSpelling=False)
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
		self.w.scopeText = vanilla.TextBox((inset, -48 - inset - 2, 65, 18), "Apply to:", selectable=True)
		self.w.scope = vanilla.PopUpButton((inset + 65, -48 - inset, -inset, 17), scopeOptions, callback=self.SavePreferences)
		linePos += lineHeight

		# Run Button:
		self.w.extractButton = vanilla.Button((inset, -20 - inset, 70, -inset), "Extract", callback=self.extractFromFrontmostFont)
		self.w.cleanButton = vanilla.Button((inset + 80, -20 - inset, 70, -inset), "Clean", callback=self.cleanForScope)
		self.w.addMissingButton = vanilla.Button((inset + 160, -20 - inset, 100, -inset), "Add Missing", callback=self.addMissingForScope)

		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Apply", callback=self.GlyphOrderManagerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def requestedFonts(self):
		scope = self.prefInt("scope")
		if scope == 0 and Glyphs.fonts:
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
					filePath = thisFont.filepath
					if filePath:
						reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
					else:
						reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
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
