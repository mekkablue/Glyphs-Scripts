#MenuTitle: Find and Replace in Font Info
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds and replaces names in Font Info > Font and Instances.
"""

import vanilla

class FindAndReplaceInFontInfo(object):
	totalCount = 0

	def __init__(self):
		# Window 'self.w':
		windowWidth = 290
		windowHeight = 200
		windowWidthResize = 100 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Find and Replace in Font Info", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.FindAndReplaceInFontInfo.mainwindow" # stores last window position and size
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
		self.w.includeInactiveInstances = vanilla.CheckBox(
			(inset + 120, linePos, -inset, 20), "Also inactive instances", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		linePos += lineHeight

		self.w.includeCustomParameters = vanilla.CheckBox((inset, linePos, -inset, 20), "Include Custom Parameters", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Replace", sizeStyle='regular', callback=self.FindAndReplaceInFontInfoMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Find and Replace in Font Info' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.w.searchFor.get())
		self.w.includeInactiveInstances.enable(self.w.includeInstances.get())

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.includeInstances"] = self.w.includeInstances.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.allFonts"] = self.w.allFonts.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.completeWordsOnly"] = self.w.completeWordsOnly.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.searchFor"] = self.w.searchFor.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.replaceWith"] = self.w.replaceWith.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.includeCustomParameters"] = self.w.includeCustomParameters.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.includeInactiveInstances"] = self.w.includeInactiveInstances.get()

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.FindAndReplaceInFontInfo.includeInstances", 0)
			Glyphs.registerDefault("com.mekkablue.FindAndReplaceInFontInfo.allFonts", 0)
			Glyphs.registerDefault("com.mekkablue.FindAndReplaceInFontInfo.completeWordsOnly", 0)
			Glyphs.registerDefault("com.mekkablue.FindAndReplaceInFontInfo.searchFor", "BETA")
			Glyphs.registerDefault("com.mekkablue.FindAndReplaceInFontInfo.replaceWith", "RC1")
			Glyphs.registerDefault("com.mekkablue.FindAndReplaceInFontInfo.includeCustomParameters", 1)
			Glyphs.registerDefault("com.mekkablue.FindAndReplaceInFontInfo.includeInactiveInstances", 0)

			# load previously written prefs:
			self.w.includeInstances.set(Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.includeInstances"])
			self.w.allFonts.set(Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.allFonts"])
			self.w.completeWordsOnly.set(Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.completeWordsOnly"])
			self.w.searchFor.set(Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.searchFor"])
			self.w.replaceWith.set(Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.replaceWith"])
			self.w.includeCustomParameters.set(Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.includeCustomParameters"])
			self.w.includeInactiveInstances.set(Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.includeInactiveInstances"])

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

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
			print("✅ %s: ‘%s’ → ‘%s’" % (reportString, name, newName))
			self.totalCount += 1
		else:
			print("🤷🏻‍♀️ %s: ‘%s’ unchanged" % (reportString, name))

		return newName

	def FindAndReplaceInFontInfoMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Find and Replace in Font Info' could not write preferences.")

			if not Glyphs.fonts:
				Message(title="No Font Open", message="The script requires at least one font. Open a font and run the script again.", OKButton=None)
			else:
				self.totalCount = 0

				searchFor = Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.searchFor"]
				replaceWith = Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.replaceWith"]
				completeWordsOnly = Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.completeWordsOnly"]
				allFonts = Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.allFonts"]
				includeCustomParameters = Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.includeCustomParameters"]
				includeInstances = Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.includeInstances"]
				includeInactiveInstances = Glyphs.defaults["com.mekkablue.FindAndReplaceInFontInfo.includeInactiveInstances"]

				if allFonts:
					fonts = Glyphs.fonts
				else:
					fonts = (Glyphs.font, )
				print("Find and Replace in Font Info:")

				for thisFont in fonts:
					if thisFont.filepath:
						print("\n🔠 %s (family: %s)" % (thisFont.filepath.lastPathComponent(), thisFont.familyName))
						print("📂 ~/%s" % thisFont.filepath.relativePathFromBaseDirPath_("~"))
					else:
						print("\n🔠 %s" % thisFont.familyName)
						print("⚠️ The font file has not been saved yet.")

					# TODO: directly iterate properties
					for prop in thisFont.properties:
						if hasAttr(prop, "values"):
							pass

					if thisFont.familyName: # could be None
						thisFont.familyName = self.replaceInName(thisFont.familyName, searchFor, replaceWith, completeWordsOnly, "Font > Family Name")
					if thisFont.designer: # could be None
						thisFont.designer = self.replaceInName(thisFont.designer, searchFor, replaceWith, completeWordsOnly, "Font > Designer")
					if thisFont.manufacturer: # could be None
						thisFont.manufacturer = self.replaceInName(thisFont.manufacturer, searchFor, replaceWith, completeWordsOnly, "Font > Manufacturer")
					if thisFont.copyright: # could be None
						thisFont.copyright = self.replaceInName(thisFont.copyright, searchFor, replaceWith, completeWordsOnly, "Font > Copyright")

					if includeCustomParameters:
						for customParameter in thisFont.customParameters:
							if Glyphs.versionNumber >= 3:
								# GLYPHS 3
								parameterIsAString = type(customParameter.value) in (objc.pyobjc_unicode, str)
							else:
								# GLYPHS 2
								parameterIsAString = type(customParameter.value) in (objc.pyobjc_unicode, str, unicode)

							if parameterIsAString:
								reportString = "Font > Custom Parameters > %s" % customParameter.name
								customParameter.value = self.replaceInName(customParameter.value, searchFor, replaceWith, completeWordsOnly, reportString)

					if includeInstances:
						for thisInstance in thisFont.instances:
							if thisInstance.active or includeInactiveInstances:
								# style name:
								thisInstance.name = self.replaceInName(
									thisInstance.name, searchFor, replaceWith, completeWordsOnly, "Instances > %s > Style Name" % thisInstance.name
									)

								# general properties:
								if Glyphs.versionNumber >= 3:
									# GLYPHS 3
									for fontInfo in thisInstance.properties:
										if type(fontInfo) == GSFontInfoValueLocalized:
											for valueSet in fontInfo.values:
												valueSet.value = self.replaceInName(
													valueSet.value, searchFor, replaceWith, completeWordsOnly, "Instances > %s > General > %s" % (thisInstance.name, fontInfo.key)
													)

								# parameters:
								if includeCustomParameters:
									for customParameter in thisInstance.customParameters:
										if Glyphs.versionNumber >= 3:
											# GLYPHS 3
											parameterIsAString = type(customParameter.value) in (objc.pyobjc_unicode, str)
										else:
											# GLYPHS 2
											parameterIsAString = type(customParameter.value) in (objc.pyobjc_unicode, str, unicode)

										if parameterIsAString:
											reportString = "Instances > %s > Custom Parameters > %s" % (thisInstance.name, customParameter.name)
											customParameter.value = self.replaceInName(customParameter.value, searchFor, replaceWith, completeWordsOnly, reportString)

			# Final report:
			Glyphs.showNotification(
				"%i Font%s: %i Change%s" % (
					len(fonts),
					"" if len(fonts) == 1 else "s",
					self.totalCount,
					"" if self.totalCount == 1 else "s",
					),
				"Find and Replace in Font Info is finished. Details in Macro Window",
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Find and Replace in Font Info Error: %s" % e)
			import traceback
			print(traceback.format_exc())

FindAndReplaceInFontInfo()
