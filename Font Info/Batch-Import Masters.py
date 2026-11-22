# MenuTitle: Batch-Import Masters
__doc__ = """
Import many masters at once with the Import Master parameter.
"""

import vanilla
from mekkablue import mekkaObject, UpdateButton, makeWindowResizable
from GlyphsApp import Glyphs, GSCustomParameter, Message
from AppKit import NSNotificationCenter, NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut


def menuForFonts(fonts):
	menu = []
	for i, font in enumerate(fonts):
		if font.filepath:
			path = font.filepath.lastPathComponent()
			menu.append(f"{i + 1}. {font.familyName} ({path})")
	if menu:
		return menu
	else:
		return ("⚠️ Save the fonts, then press Update.", )


def masterNameParticlesForFont(font, separators=".,-:/"):
	allParticles = []
	for m in font.masters:
		particles = m.name.split()
		for sep in separators:
			newParticles = []
			for particle in particles:
				newParticles.extend(particle.split(sep))
			particles = newParticles
		allParticles.extend(particles)
	return set(allParticles)


def cleanParametersFromFont(font, cpName="Import Master"):
	while font.customParameters[cpName]:
		font.removeObjectFromCustomParametersForKey_(cpName)


def importMastersFromFontToFont(importedFont, targetFont, searchFor="", useRelativePath=False):
	importedPath = importedFont.filepath
	importedRelativePath = importedPath.relativePathFromBaseDirPath_(targetFont.filepath.stringByDeletingLastPathComponent())
	for importedMaster in importedFont.masters:
		if searchFor and searchFor not in importedMaster.name:
			continue
		cpName = "Import Master"
		cpValue = {
			"Master": importedMaster.name,
			"Path": importedRelativePath if useRelativePath else importedPath,
		}
		cp = GSCustomParameter(cpName, cpValue)
		targetFont.customParameters.append(cp)
		print(f"✅ Added master: {importedMaster.name}")


class BatchImportMasters(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"sourceFont": 0,
		"targetFont": 0,
		"searchFor": "",
		"useRelativePath": True,
		"resetParameters": True,
		"suppressMessage": False,
	}

	currentFonts = Glyphs.fonts

	def __init__(self):
		# Window 'self.w':
		windowWidth = 520
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Batch-Import Masters",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		self.w.descriptionText = vanilla.TextBox("auto", "Batch-add ‘Import Master’ parameters to target font:", sizeStyle="small", selectable=True)

		self.w.targetFontText = vanilla.TextBox("auto", "Target font:", sizeStyle="small", selectable=True)
		self.w.targetFont = vanilla.PopUpButton("auto", (), sizeStyle="small", callback=self.SavePreferences)
		self.w.updateButton = UpdateButton("auto", callback=self.updateUI)
		self.w.updateButton.setToolTip("Will update all the menus and buttons of this window. Click here if you opened or closed a font since you invoked the script, or after you changed the source font.")
		tooltip = "The font that receives the Import Master parameters."
		self.w.targetFont.setToolTip(tooltip)
		self.w.targetFontText.setToolTip(tooltip)

		self.w.sourceFontText = vanilla.TextBox("auto", "Source font:", sizeStyle="small", selectable=True)
		self.w.sourceFont = vanilla.PopUpButton("auto", (), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font the custom parameters refer to."
		self.w.sourceFont.setToolTip(tooltip)
		self.w.sourceFontText.setToolTip(tooltip)

		self.w.searchForText = vanilla.TextBox("auto", "Source master name must contain:", sizeStyle="small", selectable=True)
		self.w.searchFor = vanilla.ComboBox("auto", (sorted(masterNameParticlesForFont(self.currentFonts[0])) if self.currentFonts else ()), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "If set, will only import masters that contain this name particle. Leave empty to import all masters of the source font."
		self.w.searchFor.setToolTip(tooltip)
		self.w.searchForText.setToolTip(tooltip)

		self.w.useRelativePath = vanilla.CheckBox("auto", "Use relative font path in parameter values", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.useRelativePath.setToolTip("If set, will add a relative path rather than an absolute path. Better for git repos.")

		self.w.resetParameters = vanilla.CheckBox("auto", "Delete all existing Import Master parameters in target font", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.resetParameters.setToolTip("If set, will first clean out all existing ‘Import Master’ parameters, so the font will only have the ‘Import Master’ parameters you add.")

		self.w.suppressMessage = vanilla.CheckBox("auto", "Suppress confirmation dialog", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.suppressMessage.setToolTip("After you add the masters, there is a success dialog confirming the import. If it gets on your nerves, check this checkbox.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Import", callback=self.BatchImportMastersMain)
		self.w.runButton.setToolTip("Adds an Import Master parameter to the target font for every matching master of the source font.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and share the width of the widest one, so the fields line up:
		labelNames = ("targetFontText", "sourceFontText", "searchForText")
		widestLabel = "searchForText"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# long font names must not widen the window:
		for popup in (self.w.targetFont, self.w.sourceFont):
			popup.getNSPopUpButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[targetFontText]-gap-[targetFont(>=100)]-gap-[updateButton]-inset-|",
				"H:|-inset-[sourceFontText]-gap-[sourceFont(>=100)]-inset-|",
				"H:|-inset-[searchForText]-gap-[searchFor(>=100)]-inset-|",
				"H:|-inset-[useRelativePath]-(>=inset)-|",
				"H:|-inset-[resetParameters]-(>=inset)-|",
				"H:|-inset-[suppressMessage]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[targetFont]-row-[sourceFont]-row-[searchFor]-headlineGap-[useRelativePath]-checkRow-[resetParameters]-checkRow-[suppressMessage]-inset-[runButton]-inset-|",
				{"view1": self.w.targetFontText, "attribute1": "centerY", "view2": self.w.targetFont, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.targetFont, "attribute2": "centerY"},
				{"view1": self.w.sourceFontText, "attribute1": "centerY", "view2": self.w.sourceFont, "attribute2": "centerY"},
				{"view1": self.w.searchForText, "attribute1": "centerY", "view2": self.w.searchFor, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": 15, "gap": 8, "row": 6, "checkRow": 5, "headlineGap": 10},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings (also fills the menus, see updateUI):
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.currentFonts = [f for f in Glyphs.fonts if f.filepath]
		menu = menuForFonts(self.currentFonts)
		self.w.sourceFont.setItems(menu)
		self.w.targetFont.setItems(menu)

		if self.currentFonts:
			self.w.sourceFont.enable(True)
			self.w.targetFont.enable(True)

			sourceFontIndex = self.pref("sourceFont")
			self.w.sourceFont.set(sourceFontIndex if sourceFontIndex is not None and sourceFontIndex < len(menu) else 0)
			Glyphs.defaults[self.domain("sourceFont")] = self.w.sourceFont.get()

			targetFontIndex = self.pref("targetFont")
			self.w.targetFont.set(targetFontIndex if targetFontIndex is not None and targetFontIndex < len(menu) else 0)
			Glyphs.defaults[self.domain("targetFont")] = self.w.targetFont.get()

			# update search combobox :
			if sender != self.w.searchFor:
				searchBoxContent = self.w.searchFor.get()
				choiceIndex = self.w.sourceFont.get()
				if choiceIndex < len(self.currentFonts):
					sourceFont = self.currentFonts[choiceIndex]
					particles = masterNameParticlesForFont(sourceFont)
					self.w.searchFor.setItems(sorted(particles))
					self.w.searchFor.set(searchBoxContent)  # circumvent bug
		else:
			Glyphs.defaults[self.domain("sourceFont")] = 0
			Glyphs.defaults[self.domain("targetFont")] = 0
			self.w.sourceFont.enable(False)
			self.w.targetFont.enable(False)

		# double check
		self.w.runButton.enable(self.pref("sourceFont") != self.pref("targetFont"))

	def BatchImportMastersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Batch-Import Masters Report")

				font = self.currentFonts[self.pref("targetFont")]
				importedFont = self.currentFonts[self.pref("sourceFont")]

				print("Target:", font.filepath.lastPathComponent())
				print("Source:", importedFont.filepath.lastPathComponent())
				print()

				font.disableUpdateInterface()
				try:
					if self.prefBool("resetParameters"):
						cleanParametersFromFont(font, cpName="Import Master")
					importMastersFromFontToFont(importedFont, font, searchFor=self.pref("searchFor"), useRelativePath=self.pref("useRelativePath"))
				finally:
					font.enableUpdateInterface()
					for thisUI in (font.currentTab, font.fontView):
						NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisUI)
					if font.currentTab:
						font.currentTab.reflow()

				# only reached if the import went through without an error:
				print("\n✅ Done.")
				if not self.pref("suppressMessage"):
					Message(
						title="Imported Masters",
						message="Successfully imported all masters. Consider saving, closing and reopening the file in case you experience UI glitches.",
						OKButton=None,
					)

				# self.w.close()  # delete if you want window to stay open

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Batch-Import Masters Error: {e}")
			import traceback
			print(traceback.format_exc())


BatchImportMasters()
