# MenuTitle: Remove Custom Parameters
__doc__ = """
Removes all parameters of one kind from Font Info > Font, Masters, Instances. Useful if you have many masters or instances.
"""

import vanilla
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton, fontFileName, makeWindowResizable


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
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Remove parameter", sizeStyle='small', selectable=True)
		self.w.parameterMenu = vanilla.PopUpButton("auto", self.parametersOfCurrentFont(), sizeStyle='small', callback=self.SavePreferences)
		self.w.parameterMenu.setToolTip("Remove this custom parameter from the designated parts of Font Info.")
		self.w.updateButton = UpdateButton("auto", callback=self.updateMenu)
		self.w.updateButton.setToolTip("Scans the current font for all its custom parameters and updates the menu to the left.")

		self.w.removeFromText = vanilla.TextBox("auto", "From Font Info →", sizeStyle='small', selectable=True)
		self.w.removeFromFont = vanilla.CheckBox("auto", "Font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeFromFont.setToolTip("If enabled, will remove the chosen custom parameters from File > Font Info > Font.")
		self.w.removeFromMasters = vanilla.CheckBox("auto", "Masters", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeFromMasters.setToolTip("If enabled, will remove the chosen custom parameters from File > Font Info > Masters.")
		self.w.removeFromStyles = vanilla.CheckBox("auto", "Exports" if Glyphs.versionNumber >= 3.0 else "Instances", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeFromStyles.setToolTip("If enabled, will remove the chosen custom parameters from File > Font Info > Exports (Instances in Glyphs 2).")

		self.w.removeInText = vanilla.TextBox("auto", "Remove in", sizeStyle='small', selectable=True)
		self.w.removeIn = vanilla.PopUpButton("auto", ("current font", "⚠️ ALL open fonts"), sizeStyle='small', callback=self.SavePreferences)
		tooltipText = "Choose here in which font you want to remove the parameters. Careful with the ‘All open fonts’ choice."
		self.w.removeInText.setToolTip(tooltipText)
		self.w.removeIn.setToolTip(tooltipText)

		self.w.statusText = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)
		self.w.statusText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.removals = []  # (font, container, index, parameter, description) of the most recent removal, for Undo
		self.w.undoButton = vanilla.Button("auto", "Undo", callback=self.undoRemoval)
		self.w.undoButton.setToolTip("Puts back the parameters removed by the most recent click on Remove, at their original positions.")
		self.w.undoButton.enable(False)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove", callback=self.RemoveCustomParametersMain)
		self.w.runButton.setToolTip("Removes the chosen custom parameter from the checked parts of Font Info.")
		self.w.setDefaultButton(self.w.runButton)

		# the popups take the extra width, the update button stays snug at the right
		self.w.parameterMenu.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.removeIn.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# the update button has the same low hugging as the popup and would take half the extra width
		self.w.updateButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

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
				"H:|-inset-[descriptionText]-gap-[parameterMenu(>=100)]-gap-[updateButton(24)]-inset-|",
				"H:|-inset-[removeFromText]-gap-[removeFromFont]-checkGap-[removeFromMasters]-checkGap-[removeFromStyles]-(>=inset)-|",
				"H:|-inset-[removeInText]-gap-[removeIn(>=100)]-inset-|",
				"H:|-inset-[statusText]-(>=gap)-[undoButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[parameterMenu]-row-[removeFromFont]-row-[removeIn]-inset-[runButton]-inset-|",
				{"view1": self.w.descriptionText, "attribute1": "centerY", "view2": self.w.parameterMenu, "attribute2": "centerY"},
				{"view1": self.w.statusText, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.undoButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.parameterMenu, "attribute2": "centerY"},
				{"view1": self.w.removeFromText, "attribute1": "centerY", "view2": self.w.removeFromFont, "attribute2": "centerY"},
				{"view1": self.w.removeFromMasters, "attribute1": "centerY", "view2": self.w.removeFromFont, "attribute2": "centerY"},
				{"view1": self.w.removeFromStyles, "attribute1": "centerY", "view2": self.w.removeFromFont, "attribute2": "centerY"},
				{"view1": self.w.removeInText, "attribute1": "centerY", "view2": self.w.removeIn, "attribute2": "centerY"},
				{"view1": self.w.removeFromText, "attribute1": "width", "view2": self.w.descriptionText, "attribute2": "width"},
				{"view1": self.w.removeInText, "attribute1": "width", "view2": self.w.descriptionText, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "checkGap": 6},
		)

		makeWindowResizable(self.w, minSize=(windowWidth * 0.86, 0))  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()

	def setStatus(self, text):
		"""Sets the status line and redraws it right away."""
		self.w.statusText.set(text)
		self.w.statusText.getNSTextField().display()

	def parameterCount(self):
		"""Number of occurrences the current settings would remove."""
		parameterName = self.w.parameterMenu.getItem()
		count = 0
		for thisFont in self.currentFonts():
			containers = []
			if self.pref("removeFromFont"):
				containers.append(thisFont)
			if self.pref("removeFromMasters"):
				containers.extend(thisFont.masters)
			if self.pref("removeFromStyles"):
				containers.extend(thisFont.instances)
			for container in containers:
				count += sum(1 for parameter in container.customParameters if parameter.name == parameterName)
		return count

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
		self.w.runButton.enable(bool(buttonOnOff))
		if not Glyphs.font:
			self.setStatus("❌ No font open.")
		elif not buttonOnOff:
			self.setStatus("🤖 Ready.")
		else:
			count = self.parameterCount()
			self.setStatus(f"🔮 Will remove {count} parameter{'' if count == 1 else 's'}.")

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

	def undoRemoval(self, sender=None):
		try:
			Glyphs.clearLog()
			print("Remove Custom Parameters: Undo\n")
			restoredCount = 0
			parameterName = None
			# reverse order of removal, so that every parameter goes back to its original index
			for thisFont, container, index, parameter, description in reversed(self.removals):
				if thisFont not in Glyphs.fonts:
					print(f"\t⚠️ Skipped {description}: font was closed")
					continue
				container.customParameters.insert(index, parameter)
				restoredCount += 1
				parameterName = parameter.name
				print(f"\t↩️ Restored ‘{parameter.name}’ in {description}")
			self.removals = []
			self.w.undoButton.enable(False)
			self.updateMenu()
			if parameterName:
				self.w.parameterMenu.setItem(parameterName)
			self.updateUI()
			self.setStatus(f"✅ Restored {restoredCount} parameter{'' if restoredCount == 1 else 's'}. Details in Macro Window.")
			print("\n✅ Done")
		except Exception as e:
			Glyphs.showMacroWindow()
			print(f"Remove Custom Parameters Undo Error: {e}")
			import traceback
			print(traceback.format_exc())

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

				parameterToBeDeleted = self.w.parameterMenu.getItem()
				removeFromFont = self.pref("removeFromFont")
				removeFromMasters = self.pref("removeFromMasters")
				removeFromStyles = self.pref("removeFromStyles")

				print("Remove Custom Parameters Report")
				print(f"Parameter: ‘{parameterToBeDeleted}’\n")

				removals = []
				for thisFont in theseFonts:
					print(f"📄 {fontFileName(thisFont, fullPath=True)}")

					containers = []
					if removeFromFont:
						containers.append((thisFont, "Font"))
					if removeFromMasters:
						containers.extend((master, f"Master {master.name}") for master in thisFont.masters)
					if removeFromStyles:
						containers.extend((instance, f"Export {instance.name}") for instance in thisFont.instances)

					for container, description in containers:
						for cpi in reversed(range(len(container.customParameters))):
							parameter = container.customParameters[cpi]
							if parameter.name == parameterToBeDeleted:
								del container.customParameters[cpi]
								removals.append((thisFont, container, cpi, parameter, description))
								print(f"\t🚫 Removed ‘{parameterToBeDeleted}’ in {description}")
					print()

				deletedParameterCount = len(removals)
				if deletedParameterCount:
					self.removals = removals
				self.w.undoButton.enable(bool(self.removals))

				# the removed parameter is gone from the menu, so refresh it, then report in the status line:
				self.updateMenu()
				self.setStatus(f"✅ Removed {deletedParameterCount} parameter{'' if deletedParameterCount == 1 else 's'}. Details in Macro Window.")

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
				print("✅ Done")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Custom Parameters Error: %s" % e)
			import traceback
			print(traceback.format_exc())


RemoveCustomParameters()
