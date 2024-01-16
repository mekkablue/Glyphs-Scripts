# MenuTitle: Remove Anchors in Suffixed Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes all anchors from glyphs with one of the user-specified suffix.
"""

import vanilla
from GlyphsApp import Glyphs, Message


class RemoveAnchorsinSuffixedGlyphs(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 120
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove Anchors in Suffixed Glyphs",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName="com.mekkablue.RemoveAnchorsinSuffixedGlyphs.mainwindow"  # stores last window position and size
		)

		# UI elements:
		self.w.text_1 = vanilla.TextBox((15, 14, -15, 14), "Remove anchors from glyphs with these suffixes:", sizeStyle='small')
		self.w.suffixlist = vanilla.EditText((15, 14 + 23, -15, 20), ".sups, .sinf, superior, inferior", sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - 15, -20 - 15, -15, -15), "Remove", sizeStyle='regular', callback=self.RemoveAnchorsinSuffixedGlyphsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove Anchors in Suffixed Glyphs' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults["com.mekkablue.RemoveAnchorsinSuffixedGlyphs.suffixlist"] = self.w.suffixlist.get()
		except:
			return False

		return True

	def LoadPreferences(self):
		try:
			Glyphs.registerDefault("com.mekkablue.RemoveAnchorsinSuffixedGlyphs.suffixlist", ".sups, .sinf, superior, inferior")
			self.w.suffixlist.set(Glyphs.defaults["com.mekkablue.RemoveAnchorsinSuffixedGlyphs.suffixlist"])
		except:
			return False

		return True

	def RemoveAnchorsinSuffixedGlyphsMain(self, sender):
		try:
			if not self.SavePreferences(self):
				print("Note: 'Remove Anchors in Suffixed Glyphs' could not write preferences.")

			suffixlist = Glyphs.defaults["com.mekkablue.RemoveAnchorsinSuffixedGlyphs.suffixlist"]
			suffixes = [s.strip() for s in suffixlist.split(",")]

			thisFont = Glyphs.font  # frontmost font
			Glyphs.clearLog()  # clears macro window log
			print("Remove Anchors in Suffixed Glyphs in font: ‘%s’" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			print("Looking for glyphs with suffixes %s..." % (", ".join(suffixes)))
			print()
			cleanedGlyphsCount = 0

			for thisGlyph in thisFont.glyphs:
				glyphNeedsToBeCleaned = False
				for suffix in suffixes:
					if thisGlyph.name.endswith(suffix) or "%s." % suffix in thisGlyph.name:
						glyphNeedsToBeCleaned = True
				if glyphNeedsToBeCleaned:
					print("Removing anchors in %s" % thisGlyph.name)
					cleanedGlyphsCount += 1
					for thisLayer in thisGlyph.layers:
						print("   Layer: %s" % thisLayer.name)
						thisLayer.anchors = []

			print("\n%i glyphs cleared of their anchors.\nDone." % cleanedGlyphsCount)

			if cleanedGlyphsCount:
				msgTitle = "Removed Anchors Successfully."
			else:
				msgTitle = "No Anchors Removed."

			Message(
				title=msgTitle,
				message="Removed anchors in %i glyph%s in font ‘%s’. Detailed report in Macro Window." % (
					cleanedGlyphsCount,
					"" if cleanedGlyphsCount == 1 else "s",
					thisFont.familyName,
				),
				OKButton=None,
			)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Anchors in Suffixed Glyphs Error: %s" % e)
			import traceback
			print(traceback.format_exc())


RemoveAnchorsinSuffixedGlyphs()
