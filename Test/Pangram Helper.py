#MenuTitle: Pangram Helper
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Helps you write pangrams by displaying which letters are still missing.
"""

import vanilla
from AppKit import NSStringPboardType, NSPasteboard
fullAlphabets = (
	"abcdefghijklmnopqrstuvwxyz",
	"abcdefghijklmnñopqrstuvwxyz",
	"αβγδεζηθικλμνξοπρςστυφχψω",
	"абвгдеёжзийклмнопрстуфхчцшщьыъэюя",
	)

class PangramHelper(object):
	prefDomain = "com.mekkablue.PangramHelper"
	title = "Pangram Helper"
	alphabet = fullAlphabets[0]

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 180
		windowWidthResize = 500 # user can resize width by this value
		windowHeightResize = 500 # user can resize height by this value
		self.w = vanilla.Window(
			(windowWidth, windowHeight), # default window size
			self.title, # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName=self.domain("mainwindow") # stores last window position and size
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
		if not self.LoadPreferences():
			print("Note: '%s' could not load preferences. Will resort to defaults" % self.title)

		# Open window and focus on it:
		self.updateMissingLetters()
		self.w.open()
		self.w.pangram.selectAll()
		self.w.makeKey()

	def domain(self, key):
		return "%s.%s" % (self.prefDomain, key)

	def preference(self, key):
		domain = self.domain(key)
		return Glyphs.defaults[domain]

	def SavePreferences(self, sender=None):
		try:
			Glyphs.defaults[self.domain("alphabetChoice")] = self.w.alphabetChoice.get()
			Glyphs.defaults[self.domain("pangram")] = self.w.pangram.get()
		except:
			return False
		return True

	def LoadPreferences(self, sender=None):
		try:
			Glyphs.registerDefault(self.domain("alphabetChoice"), 0)
			Glyphs.registerDefault(self.domain("pangram"), "The quick brown fox jumps over the lazy dog.")

			self.w.alphabetChoice.set(self.preference("alphabetChoice"))
			self.w.pangram.set(self.preference("pangram"))
		except:
			return False
		return True

	def decompose(self, glyph):
		unicodeValue = "%04X" % ord(glyph)
		info = Glyphs.glyphInfoForUnicode(unicodeValue)
		if info.components:
			listOfCharacters = [c.unicharString() for c in info.components if c.category == "Letter"]
			return listOfCharacters
		return []

	def updateMissingLetters(self, sender=None):
		if not self.SavePreferences():
			print("Note: '%s' could not save its preferences." % self.title)

		self.alphabet = fullAlphabets[self.preference("alphabetChoice")]

		if Glyphs.versionNumber >= 3:
			# Glyphs 3 code
			currentTextEntry = self.preference("pangram").lower()
		else:
			# Glyphs 2 code
			currentTextEntry = unicode(self.preference("pangram").lower())

		containedBaseLetters = ""
		for thisLetter in currentTextEntry:
			if ord(thisLetter) > 191:
				components = self.decompose(thisLetter)
				containedBaseLetters += "".join(components)

		currentTextEntry += containedBaseLetters
		missingLetters = ""
		for thisLetter in self.alphabet:
			if not thisLetter in currentTextEntry:
				missingLetters += thisLetter.upper()
		self.w.missingLetters.set("Missing: %s" % missingLetters)

	def PangramHelperMain(self, sender):
		try:
			myText = self.preference("pangram")

			if myText:
				if sender == self.w.copyButton:
					myClipboard = NSPasteboard.generalPasteboard()
					myClipboard.declareTypes_owner_([NSStringPboardType], None)
					myClipboard.setString_forType_(myText, NSStringPboardType)
				elif sender == self.w.tabButton:
					Glyphs.font.newTab(myText)
					self.w.close() # delete if you want window to stay open
			else:
				Message("%s Error", "The entered text is empty." % self.title, OKButton=None)

			if not self.SavePreferences(self):
				print("Note: '%s' could not write preferences." % self.title)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("%s Error: %s" % (self.title, e))

PangramHelper()
