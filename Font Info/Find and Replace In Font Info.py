# MenuTitle: Find and Replace in Font Info
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:  # noqa: F841
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__ = """
Finds and replaces names in Font Info > Font and Instances.
"""

import vanilla
import objc
from GlyphsApp import Glyphs, GSFontInfoValueLocalized, Message
from mekkablue import mekkaObject


class FindAndReplaceInFontInfo(mekkaObject):
	totalCount = 0
	prefDict = {
		# "prefName": defaultValue,
		"includeInstances": 0,
		"allFonts": 0,
		"completeWordsOnly": 0,
		"searchFor": "BETA",
		"replaceWith": "RC1",
		"includeCustomParameters": 1,
		"includeInactiveInstances": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 290
		windowHeight = 200
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Find and Replace in Font Info",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.searchForText = vanilla.TextBox((inset, linePos + 2, 80, 14), "Search for:", sizeStyle='small', selectable=True)
		self.w.searchFor = vanilla.EditText((inset + 80, linePos - 1, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.replaceWithText = vanilla.TextBox((inset, linePos + 2, 80, 14), "Replace with:", sizeStyle='small', selectable=True)
		self.w.replaceWith = vanilla.EditText((inset + 80, linePos - 1, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.completeWordsOnly = vanilla.CheckBox((inset, linePos, -inset, 20), "Complete words only", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos, -inset, 20), "⚠️ Include all open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.includeInstances = vanilla.CheckBox((inset, linePos, 120, 20), "Include instances", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeInactiveInstances = vanilla.CheckBox((inset + 120, linePos, -inset, 20), "Also inactive instances", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.includeCustomParameters = vanilla.CheckBox((inset, linePos, -inset, 20), "Include Custom Parameters", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Replace", sizeStyle='regular', callback=self.FindAndReplaceInFontInfoMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.w.searchFor.get())
		self.w.includeInactiveInstances.enable(self.w.includeInstances.get())

	def replaceInName(self, name, searchFor, replaceWith, completeWordsOnly=False, reportString="", avoidExcessiveWhiteSpace=True):
		newName = name.strip()
		if completeWordsOnly:
			particles = newName.split(" ")
			for i in range(len(particles)):
				if particles[i] == searchFor:
					particles[i] = replaceWith
			newName = " ".join(particles)
		else:
			newName = name.replace(searchFor, replaceWith).strip()

		if avoidExcessiveWhiteSpace:
			# remove leading and trailing white space:
			newName = newName.strip()
			# remove multiple spaces:
			while "  " in newName:
				newName = newName.replace("  ", " ")

		if newName != name:
			print(f"✅ {reportString}: ‘{name}’ → ‘{newName}’")
			self.totalCount += 1
		else:
			print(f"🤷🏻‍♀️ {reportString}: ‘{name}’ unchanged")

		return newName

	def FindAndReplaceInFontInfoMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if not Glyphs.fonts:
				Message(title="No Font Open", message="The script requires at least one font. Open a font and run the script again.", OKButton=None)
			else:
				self.totalCount = 0

				searchFor = self.pref("searchFor")
				replaceWith = self.pref("replaceWith")
				completeWordsOnly = self.pref("completeWordsOnly")
				allFonts = self.pref("allFonts")
				includeCustomParameters = self.pref("includeCustomParameters")
				includeInstances = self.pref("includeInstances")
				includeInactiveInstances = self.pref("includeInactiveInstances")

				if allFonts:
					fonts = Glyphs.fonts
				else:
					fonts = (Glyphs.font, )
				print("Find and Replace in Font Info:")

				for thisFont in fonts:
					if thisFont.filepath:
						print(f"\n🔠 {thisFont.filepath.lastPathComponent()} (family: {thisFont.familyName})")
						print(f"📂 ~/{thisFont.filepath.relativePathFromBaseDirPath_('~')}")
					else:
						print(f"\n🔠 {thisFont.familyName}")
						print("⚠️ The font file has not been saved yet.")

					# TODO: directly iterate properties
					# for prop in thisFont.properties:
					# 	if hasattr(prop, "values"):
					# 		pass

					if thisFont.familyName:  # could be None
						thisFont.familyName = self.replaceInName(thisFont.familyName, searchFor, replaceWith, completeWordsOnly, "Font > Family Name")
					if thisFont.designer:  # could be None
						thisFont.designer = self.replaceInName(thisFont.designer, searchFor, replaceWith, completeWordsOnly, "Font > Designer")
					if thisFont.manufacturer:  # could be None
						thisFont.manufacturer = self.replaceInName(thisFont.manufacturer, searchFor, replaceWith, completeWordsOnly, "Font > Manufacturer")
					if thisFont.copyright:  # could be None
						thisFont.copyright = self.replaceInName(thisFont.copyright, searchFor, replaceWith, completeWordsOnly, "Font > Copyright")

					if includeCustomParameters:
						for customParameter in thisFont.customParameters:
							parameterIsAString = isinstance(customParameter.value, (objc.pyobjc_unicode, str))

							if parameterIsAString:
								reportString = f"Font > Custom Parameters > {customParameter.name}"
								customParameter.value = self.replaceInName(customParameter.value, searchFor, replaceWith, completeWordsOnly, reportString)

					if includeInstances:
						for thisInstance in thisFont.instances:
							if Glyphs.buildNumber > 3198:
								instanceIsExporting = thisInstance.exports
							else:
								instanceIsExporting = thisInstance.active
							if instanceIsExporting or includeInactiveInstances:
								# style name:
								thisInstance.name = self.replaceInName(
									thisInstance.name, searchFor, replaceWith, completeWordsOnly, f"Instances > {thisInstance.name} > Style Name"
								)

								# general properties:
								if Glyphs.versionNumber >= 3:
									# GLYPHS 3
									for fontInfo in thisInstance.properties:
										if isinstance(fontInfo, GSFontInfoValueLocalized):
											for valueSet in fontInfo.values:
												valueSet.value = self.replaceInName(
													valueSet.value, searchFor, replaceWith, completeWordsOnly, f"Instances > {thisInstance.name} > General > {fontInfo.key}"
												)

								# parameters:
								if includeCustomParameters:
									for customParameter in thisInstance.customParameters:
										parameterIsAString = isinstance(customParameter.value, (objc.pyobjc_unicode, str))

										if parameterIsAString:
											reportString = f"Instances > {thisInstance.name} > Custom Parameters > {customParameter.name}"
											customParameter.value = self.replaceInName(customParameter.value, searchFor, replaceWith, completeWordsOnly, reportString)

			# Final report:
			Message(
				title="%i Font%s: %i Change%s" % (
					len(fonts),
					"" if len(fonts) == 1 else "s",
					self.totalCount,
					"" if self.totalCount == 1 else "s",
				),
				message="Find and Replace in Font Info is finished. Details in Macro Window",
				OKButton="Cool"
			)
			print("\nDone.")

		except Exception as e:  # noqa: F841
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Find and Replace in Font Info Error: {e}")
			import traceback
			print(traceback.format_exc())


FindAndReplaceInFontInfo()
