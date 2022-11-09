#MenuTitle: Remove Custom Parameters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes all parameters of one kind from Font Info > Font, Masters, Instances. Useful if you have many masters or instances.
"""

from GlyphsApp import *
import vanilla

class RemoveCustomParameters(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 315
		windowHeight = 130
		windowWidthResize = 500 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Remove Custom Parameters", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.RemoveCustomParameters.mainwindow" # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Remove parameter:", sizeStyle='small', selectable=True)
		self.w.parameterMenu = vanilla.PopUpButton((inset + 110, linePos, -inset - 22, 17), self.parametersOfCurrentFont(), sizeStyle='small', callback=self.SavePreferences)
		self.w.parameterMenu.getNSPopUpButton().setToolTip_("Remove this custom parameter from the designated parts of Font Info.")
		self.w.updateButton = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.updateMenu)
		self.w.updateButton.getNSButton().setToolTip_("Scans the current font for all its custom parameters and updates the menu to the left.")
		linePos += lineHeight

		self.w.removeFromText = vanilla.TextBox((inset, linePos + 3, 100, 14), "From Font Info >", sizeStyle='small', selectable=True)
		self.w.removeFromFont = vanilla.CheckBox((inset + 95 + 50 * 0, linePos, 100, 20), "Font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeFromFont.getNSButton().setToolTip_("If enabled, will remove the chosen custom parameters from File > Font Info > Font.")
		self.w.removeFromMasters = vanilla.CheckBox((inset + 95 + 50, linePos, 100, 20), "Masters", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeFromMasters.getNSButton().setToolTip_("If enabled, will remove the chosen custom parameters from File > Font Info > Masters.")
		self.w.removeFromStyles = vanilla.CheckBox(
			(inset + 95 + 120, linePos, -inset, 20), "Styles" if Glyphs.versionNumber >= 3.0 else "Instances", value=True, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.removeFromStyles.getNSButton().setToolTip_("If enabled, will remove the chosen custom parameters from File > Font Info > Styles (Instances in Glyphs 2).")
		linePos += lineHeight

		self.w.removeInText = vanilla.TextBox((inset, linePos + 3, 62, 14), "Remove in", sizeStyle='small', selectable=True)
		self.w.removeIn = vanilla.PopUpButton((inset + 62, linePos + 1, 150, 17), ("current font", "⚠️ ALL open fonts"), sizeStyle='small', callback=self.SavePreferences)
		self.w.removeIn.getNSPopUpButton().setToolTip_("Choose here in which font you want to remove the parameters. Careful with the ‘All open fonts’ choice.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Remove", sizeStyle='regular', callback=self.RemoveCustomParametersMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove Custom Parameters' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()

	def updateMenu(self, sender=None):
		currentParameters = self.parametersOfCurrentFont()
		self.w.parameterMenu.setItems(currentParameters)

	def updateUI(self, sender=None):
		menuChoice = self.w.parameterMenu.getItem()
		shouldRemoveFromFont = Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromFont"]
		shouldRemoveFromMasters = Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromMasters"]
		shouldRemoveFromStyles = Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromStyles"]
		buttonOnOff = menuChoice and (shouldRemoveFromFont or shouldRemoveFromMasters or shouldRemoveFromStyles)
		self.w.runButton.enable(buttonOnOff)

	def parametersOfCurrentFont(self, sender=None):
		theseFonts = self.currentFonts()
		if not theseFonts:
			return ()
		else:
			parameterNameList = []
			for thisFont in theseFonts:
				for parameter in thisFont.customParameters:
					parameterNameList.append(parameter.name)
				for master in thisFont.masters:
					for parameter in master.customParameters:
						parameterNameList.append(parameter.name)
				for instance in thisFont.instances:
					for parameter in instance.customParameters:
						parameterNameList.append(parameter.name)
			return set(parameterNameList)

	def currentFonts(self, sender=None):
		goThroughAllOpenFonts = Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeIn"]
		if goThroughAllOpenFonts:
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (Glyphs.font, ) # frontmost font only
		return theseFonts

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromFont"] = self.w.removeFromFont.get()
			Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromMasters"] = self.w.removeFromMasters.get()
			Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromStyles"] = self.w.removeFromStyles.get()
			Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeIn"] = self.w.removeIn.get()

			if sender == self.w.removeIn:
				self.updateMenu()

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.RemoveCustomParameters.removeFromFont", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveCustomParameters.removeFromMasters", 1)
			Glyphs.registerDefault("com.mekkablue.RemoveCustomParameters.removeFromStyles", 1)
			Glyphs.registerDefault("com.mekkablue.RemoveCustomParameters.removeIn", 0)

			# load previously written prefs:
			self.w.removeFromFont.set(Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromFont"])
			self.w.removeFromMasters.set(Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromMasters"])
			self.w.removeFromStyles.set(Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromStyles"])
			self.w.removeIn.set(Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeIn"])

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def RemoveCustomParametersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Remove Custom Parameters' could not write preferences.")

			if len(Glyphs.fonts) == 0:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				theseFonts = self.currentFonts()

				deletedParameterCount = 0
				for thisFont in theseFonts:
					print("Remove Custom Parameters Report for %s" % thisFont.familyName)
					if thisFont.filepath:
						print(thisFont.filepath)
					else:
						print("⚠️ The font file has not been saved yet.")
					print()

					parameterToBeDeleted = self.w.parameterMenu.getItem()
					removeFromFont = Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromFont"]
					removeFromMasters = Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromMasters"]
					removeFromStyles = Glyphs.defaults["com.mekkablue.RemoveCustomParameters.removeFromStyles"]

					if removeFromFont:
						for cpi in reversed(range(len(thisFont.customParameters))):
							if thisFont.customParameters[cpi].name == parameterToBeDeleted:
								del thisFont.customParameters[cpi]
								deletedParameterCount += 1
								print("🚫 Removed parameter in Font")

					if removeFromMasters:
						for master in thisFont.masters:
							for cpi in reversed(range(len(master.customParameters))):
								if master.customParameters[cpi].name == parameterToBeDeleted:
									del master.customParameters[cpi]
									deletedParameterCount += 1
									print("🚫 Removed parameter in Master %s" % master.name)

					if removeFromStyles:
						for instance in thisFont.instances:
							for cpi in reversed(range(len(instance.customParameters))):
								if instance.customParameters[cpi].name == parameterToBeDeleted:
									del instance.customParameters[cpi]
									deletedParameterCount += 1
									print("🚫 Removed parameter in Style %s" % instance.name)

				self.w.close() # delete if you want window to stay open

				# Final report:
				Glyphs.showNotification(
					"Removed Parameters in %i Font%s" % (
						len(theseFonts),
						"" if len(theseFonts) == 1 else "s",
						),
					"Deleted %i occurrence%s of ‘%s’. Details in Macro Window" % (
						deletedParameterCount,
						"" if deletedParameterCount == 1 else "s",
						parameterToBeDeleted,
						),
					)
				print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Custom Parameters Error: %s" % e)
			import traceback
			print(traceback.format_exc())

RemoveCustomParameters()
