# MenuTitle: Set ssXX Names
__doc__ = """
Prefills names for ssXX features with ‘Alternate’ or another chosen text, plus the name of the first substituted glyph, e.g., ‘Alternate a’.
"""

import vanilla
from mekkablue import mekkaObject, UpdateButton, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut

if Glyphs.versionNumber < 4.0:
	# Glyphs 3 only had the old name, renamed in Glyphs 4:
	from GlyphsApp import GSFontInfoValue as GSInfoValue
else:
	from GlyphsApp import GSInfoValue


def featureHasName(feature):
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		return bool(feature.labels)
	else:
		# GLYPHS 2
		return feature.notes and feature.notes.startswith("Name:")


def addNameToFeature(feature, featureName):
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		featureLabel = GSInfoValue()
		featureLabel.languageTag = "dflt"
		featureLabel.value = featureName
		feature.labels = [featureLabel]
	else:
		# GLYPHS 2
		feature.notes = f"Name: {featureName}"


class SetSSXXNames(mekkaObject):
	defaultName = "Alternate"
	prefDict = {
		# "prefName": defaultValue,
		"alternate": defaultName,
		"overwrite": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 420
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set SSXX Names",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		self.w.descriptionText = vanilla.TextBox("auto", "Prefill names for Stylistic Set features ss01–ss20 with a default phrase:", sizeStyle='small', selectable=True)

		tooltipText = "The script will look for the first substituted glyph in every ssXX, e.g., ‘a’, and construct a Stylistic Set name with this Default Name plus the name of the first substituted glyph, e.g., ‘Alternate a’."
		self.w.alternateText = vanilla.TextBox("auto", "Default Name:", sizeStyle='small', selectable=True)
		self.w.alternateText.setToolTip(tooltipText)
		self.w.alternate = vanilla.EditText("auto", self.defaultName, callback=self.SavePreferences, sizeStyle='small')
		self.w.alternate.setToolTip(tooltipText)
		self.w.alternateUpdateButton = UpdateButton("auto", callback=self.alternateUpdateButtonAction)
		self.w.alternateUpdateButton.setToolTip(f"Will reset default name to ‘{self.defaultName}’.")

		self.w.overwrite = vanilla.CheckBox("auto", "Overwrite existing names", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.overwrite.setToolTip("If set, will reset all ssXX names. If unset, will skip ssXX features that already have a name.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Fill Names", callback=self.SetSSXXNamesMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the field takes the leftover width:
		nsLabel = self.w.alternateText.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[alternateText]-gap-[alternate]-gap-[alternateUpdateButton]-inset-|",
				"H:|-inset-[overwrite]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[alternate]-row-[overwrite]-inset-[runButton]-inset-|",
				{"view1": self.w.alternateText, "attribute1": "centerY", "view2": self.w.alternate, "attribute2": "centerY"},
				{"view1": self.w.alternateUpdateButton, "attribute1": "centerY", "view2": self.w.alternate, "attribute2": "centerY"},
			],
			metrics={"inset": 12, "gap": 8, "row": 6, "headlineGap": 10},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def alternateUpdateButtonAction(self, sender):
		self.w.alternate.set(self.defaultName)
		self.SavePreferences()

	def SetSSXXNamesMain(self, sender=None):
		try:
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			Glyphs.showMacroWindow()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if not thisFont:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			# query user settings:
			alternate = self.pref("alternate")
			overwrite = self.pref("overwrite")

			print(f"Setting ssXX Names for {thisFont.familyName}")
			if thisFont.filepath:
				print(thisFont.filepath)
			else:
				print("⚠️ The font file has not been saved yet.")

			ssXXtags = tuple(f"ss{i + 1:02}" for i in range(20))
			for thisFeature in thisFont.features:
				if thisFeature.name in ssXXtags:
					if overwrite or not featureHasName(thisFeature):
						codeLines = [line.strip() for line in thisFeature.code.strip().split(";") if " by " in line and not line.strip().startswith("#")]
						if codeLines:
							replacedLetter = codeLines[0].split("by")[0].split("sub")[1].strip()
							if replacedLetter:
								newName = f"{alternate} {replacedLetter}"
								print(f"  {thisFeature.name}: {newName}")
								addNameToFeature(thisFeature, newName)

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Set ssXX Names Error: {e}")
			import traceback
			print(traceback.format_exc())


SetSSXXNames()
