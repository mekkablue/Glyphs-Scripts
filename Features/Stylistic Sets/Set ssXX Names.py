#MenuTitle: Set ssXX Names
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Prefills names for ssXX features with ‘Alternate’ or another chosen text, plus the name of the first substituted glyph, e.g., ‘Alternate a’.
"""

import vanilla

class SetSSXXNames(object):
	defaultName = u"Alternate"

	def __init__(self):
		# Window 'self.w':
		windowWidth = 270
		windowHeight = 145
		windowWidthResize = 200 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Set ssXX Names", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.SetSSXXNames.mainwindow" # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 12, 22
		self.w.descriptionText = vanilla.TextBox(
			(inset, linePos + 2, -inset, 30), u"Prefill human-readable names for Stylistic Set features ss01-ss20 with a default phrase:", sizeStyle='small', selectable=True
			)
		linePos += int(lineHeight * 1.8)

		self.w.alternateText = vanilla.TextBox((inset, linePos + 2, 85, 14), u"Default Name:", sizeStyle='small', selectable=True)
		self.w.alternate = vanilla.EditText((inset + 85, linePos - 1, -inset - 25, 19), self.defaultName, callback=self.SavePreferences, sizeStyle='small')
		self.w.alternate.getNSTextField().setToolTip_(
			u"The script will look for the first substituted glyph in every ssXX, e.g., ‘a’, and construct a Stylistic Set name with this Default Name plus the name of the first substituted glyph, e.g., ‘Alternate a’."
			)
		self.w.alternateUpdateButton = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), u"↺", sizeStyle='small', callback=self.SavePreferences)
		self.w.alternateUpdateButton.getNSButton().setToolTip_(u"Will reset default name to ‘%s’." % self.defaultName)
		linePos += lineHeight

		self.w.overwrite = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Overwrite existing names", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.overwrite.getNSButton(
		).setToolTip_(u"If set, will skip ssXX features that already have a ‘Name:’ entry in their feature notes. If unset, will reset all ssXX names.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Fill Names", sizeStyle='regular', callback=self.SetSSXXNamesMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Set ssXX Names' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SavePreferences(self, sender=None):
		try:
			# reset name field:
			if sender == self.w.alternateUpdateButton:
				self.w.alternate.set(self.defaultName)

			# save prefs:
			Glyphs.defaults["com.mekkablue.SetSSXXNames.alternate"] = self.w.alternate.get()
			Glyphs.defaults["com.mekkablue.SetSSXXNames.overwrite"] = self.w.overwrite.get()
		except:
			return False

		return True

	def LoadPreferences(self, sender=None):
		try:
			Glyphs.registerDefault("com.mekkablue.SetSSXXNames.alternate", self.defaultName)
			Glyphs.registerDefault("com.mekkablue.SetSSXXNames.overwrite", 0)
			self.w.alternate.set(Glyphs.defaults["com.mekkablue.SetSSXXNames.alternate"])
			self.w.overwrite.set(Glyphs.defaults["com.mekkablue.SetSSXXNames.overwrite"])
		except:
			return False

		return True

	def SetSSXXNamesMain(self, sender=None):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print("Note: 'Set ssXX Names' could not write preferences.")

			thisFont = Glyphs.font # frontmost font

			# query user settings:
			alternate = Glyphs.defaults["com.mekkablue.SetSSXXNames.alternate"]
			overwrite = Glyphs.defaults["com.mekkablue.SetSSXXNames.overwrite"]

			print("Set ssXX Names Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()

			ssXXtags = ["ss%02i" % (i + 1) for i in range(20)]

			for thisFeature in Font.features:
				if thisFeature.name in ssXXtags:
					if overwrite or not (thisFeature.notes and thisFeature.notes.startswith("Name:")):
						codeLines = [l.strip() for l in thisFeature.code.strip().split(";") if " by " in l]
						if codeLines:
							replacedLetter = codeLines[0].split("by")[0].replace("sub", "").strip()
							if replacedLetter:
								thisFeature.notes = "Name: %s %s" % (alternate, replacedLetter)

			self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set ssXX Names Error: %s" % e)
			import traceback
			print(traceback.format_exc())

SetSSXXNames()
