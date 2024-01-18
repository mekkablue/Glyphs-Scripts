# MenuTitle: Pangram Helper
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Helps you write pangrams by displaying which letters are still missing.
"""

import vanilla
from AppKit import NSStringPboardType, NSPasteboard
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject

fullAlphabets = (
	"abcdefghijklmnopqrstuvwxyz",
	"abcdefghijklmnñopqrstuvwxyz",
	"αβγδεζηθικλμνξοπρςστυφχψω",
	"абвгдеёжзийклмнопрстуфхчцшщьыъэюя",
)


class PangramHelper(mekkaObject):
	prefDict = {
		"alphabetChoice": 0,
		"pangram": "The quick brown fox jumps over the lazy dog.",
	}
	title = "Pangram Helper"
	alphabet = fullAlphabets[0]

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 180
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 500  # user can resize height by this value
		self.w = vanilla.Window(
			(windowWidth, windowHeight),  # default window size
			self.title,  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.alphabetChoice = vanilla.PopUpButton((inset, linePos, -inset, 17), fullAlphabets, sizeStyle='small', callback=self.updateMissingLetters)
		linePos += lineHeight

		self.w.missingLetters = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Missing: %s" % self.alphabet.upper(), sizeStyle='small')
		linePos += lineHeight

		self.w.pangram = vanilla.TextEditor((1, linePos, -1, -45), "The quick brown fox jumps over the lazy dog.", checksSpelling=True, callback=self.updateMissingLetters)

		# Run Button:
		self.w.copyButton = vanilla.Button((-170, -20 - inset, -110, -inset), "Copy", sizeStyle='regular', callback=self.PangramHelperMain)
		self.w.tabButton = vanilla.Button((-100, -20 - inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.PangramHelperMain)
		self.w.setDefaultButton(self.w.tabButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.updateMissingLetters()
		self.w.open()
		self.w.pangram.selectAll()
		self.w.makeKey()

	def decompose(self, glyph):
		unicodeValue = "%04X" % ord(glyph)
		info = Glyphs.glyphInfoForUnicode(unicodeValue)
		if info.components:
			listOfCharacters = [c.unicharString() for c in info.components if c.category == "Letter"]
			return listOfCharacters
		return []

	def updateMissingLetters(self, sender=None):
		self.SavePreferences()

		self.alphabet = fullAlphabets[self.pref("alphabetChoice")]

		if Glyphs.versionNumber >= 3:
			# Glyphs 3 code
			currentTextEntry = self.pref("pangram").lower()
		else:
			# Glyphs 2 code
			currentTextEntry = unicode(self.pref("pangram").lower())  # noqa F821

		containedBaseLetters = ""
		for thisLetter in currentTextEntry:
			if ord(thisLetter) > 191:
				components = self.decompose(thisLetter)
				containedBaseLetters += "".join(components)

		currentTextEntry += containedBaseLetters
		missingLetters = ""
		for thisLetter in self.alphabet:
			if thisLetter not in currentTextEntry:
				missingLetters += thisLetter.upper()
		self.w.missingLetters.set("Missing: %s" % missingLetters)

	def PangramHelperMain(self, sender):
		try:
			myText = self.pref("pangram")

			if myText:
				if sender == self.w.copyButton:
					myClipboard = NSPasteboard.generalPasteboard()
					myClipboard.declareTypes_owner_([NSStringPboardType], None)
					myClipboard.setString_forType_(myText, NSStringPboardType)
				elif sender == self.w.tabButton:
					Glyphs.font.newTab(myText)
					self.w.close()  # delete if you want window to stay open
			else:
				Message("%s Error", "The entered text is empty." % self.title, OKButton=None)

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("%s Error: %s" % (self.title, e))


PangramHelper()
