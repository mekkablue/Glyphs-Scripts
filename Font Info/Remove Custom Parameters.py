# MenuTitle: Remove Custom Parameters
__doc__ = """
Removes all parameters of one kind from Font Info > Font, Masters, Instances. Useful if you have many masters or instances.
"""

import vanilla
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton, fontFileName


class RemoveCustomParameters(mekkaObject):
	prefDict = {
		"removeFromFont": 0,
		"removeFromMasters": 1,
		"removeFromStyles": 1,
		"removeIn": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 380
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove Custom Parameters",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Remove parameter:", sizeStyle='small', selectable=True)
		self.w.parameterMenu = vanilla.PopUpButton("auto", self.parametersOfCurrentFont(), sizeStyle='small', callback=self.SavePreferences)
		self.w.parameterMenu.setToolTip("Remove this custom parameter from the designated parts of Font Info.")
		self.w.updateButton = UpdateButton("auto", callback=self.updateMenu)
		self.w.updateButton.setToolTip("Scans the current font for all its custom parameters and updates the menu to the left.")

		self.w.removeFromText = vanilla.TextBox("auto", "From Font Info >", sizeStyle='small', selectable=True)
		self.w.removeFromFont = vanilla.CheckBox("auto", "Font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeFromFont.setToolTip("If enabled, will remove the chosen custom parameters from File > Font Info > Font.")
		self.w.removeFromMasters = vanilla.CheckBox("auto", "Masters", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeFromMasters.setToolTip("If enabled, will remove the chosen custom parameters from File > Font Info > Masters.")
		self.w.removeFromStyles = vanilla.CheckBox("auto", "Styles" if Glyphs.versionNumber >= 3.0 else "Instances", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeFromStyles.setToolTip("If enabled, will remove the chosen custom parameters from File > Font Info > Styles (Instances in Glyphs 2).")

		self.w.removeInText = vanilla.TextBox("auto", "Remove in", sizeStyle='small', selectable=True)
		self.w.removeIn = vanilla.PopUpButton("auto", ("current font", "⚠️ ALL open fonts"), sizeStyle='small', callback=self.SavePreferences)
		tooltipText = "Choose here in which font you want to remove the parameters. Careful with the ‘All open fonts’ choice."
		self.w.removeInText.setToolTip(tooltipText)
		self.w.removeIn.setToolTip(tooltipText)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove", callback=self.RemoveCustomParametersMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned, hug their text and share one width:
		labelNames = ("descriptionText", "removeFromText", "removeInText")
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-gap-[parameterMenu(>=150)]-gap-[updateButton]-inset-|",
				"H:|-inset-[removeFromText]-gap-[removeFromFont]-gap-[removeFromMasters]-gap-[removeFromStyles]-(>=inset)-|",
				"H:|-inset-[removeInText]-gap-[removeIn(>=150)]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[parameterMenu]-row-[removeFromFont]-row-[removeIn]-inset-[runButton]-inset-|",
				{"view1": self.w.descriptionText, "attribute1": "centerY", "view2": self.w.parameterMenu, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.parameterMenu, "attribute2": "centerY"},
				{"view1": self.w.removeFromText, "attribute1": "centerY", "view2": self.w.removeFromFont, "attribute2": "centerY"},
				{"view1": self.w.removeFromMasters, "attribute1": "centerY", "view2": self.w.removeFromFont, "attribute2": "centerY"},
				{"view1": self.w.removeFromStyles, "attribute1": "centerY", "view2": self.w.removeFromFont, "attribute2": "centerY"},
				{"view1": self.w.removeInText, "attribute1": "centerY", "view2": self.w.removeIn, "attribute2": "centerY"},
				{"view1": self.w.removeFromText, "attribute1": "width", "view2": self.w.descriptionText, "attribute2": "width"},
				{"view1": self.w.removeInText, "attribute1": "width", "view2": self.w.descriptionText, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()

	def updateMenu(self, sender=None):
		currentParameters = self.parametersOfCurrentFont()
		self.w.parameterMenu.setItems(currentParameters)
		self.updateUI()

	def updateUI(self, sender=None):
		menuChoice = self.w.parameterMenu.getItem()
		shouldRemoveFromFont = self.pref("removeFromFont")
		shouldRemoveFromMasters = self.pref("removeFromMasters")
		shouldRemoveFromStyles = self.pref("removeFromStyles")
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
			return sorted(set(parameterNameList))

	def currentFonts(self, sender=None):
		goThroughAllOpenFonts = self.pref("removeIn")
		if goThroughAllOpenFonts:
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (Glyphs.font, ) if Glyphs.font else ()  # frontmost font only
		return theseFonts

	def RemoveCustomParametersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if len(Glyphs.fonts) == 0:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				theseFonts = self.currentFonts()

				deletedParameterCount = 0
				for thisFont in theseFonts:
					print("Remove Custom Parameters Report for %s" % thisFont.familyName)
					print(fontFileName(thisFont, fullPath=True))
					print()

					parameterToBeDeleted = self.w.parameterMenu.getItem()
					removeFromFont = self.pref("removeFromFont")
					removeFromMasters = self.pref("removeFromMasters")
					removeFromStyles = self.pref("removeFromStyles")

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

				self.w.close()  # delete if you want window to stay open

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
