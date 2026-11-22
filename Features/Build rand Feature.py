# MenuTitle: Build rand Feature
__doc__ = """
Build rand (random) feature from .cvXX or another (numbered) suffix.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, GSFeature, Message
from mekkablue import mekkaObject, UpdateButton, fontFileName, makeWindowResizable


def getRootName(glyphName):
	if "." in glyphName:
		dotIndex = glyphName.find(".")
		return glyphName[:dotIndex]
	else:
		return glyphName


class BuildRandFeature(mekkaObject):
	prefDict = {
		"overwrite": 1,
		"suffix": ".cv",
		"exclude": 1,
		"excludeList": ".build, .ss12",
		"includeDefault": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 360
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Build rand Feature",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Build a Randomize feature with the following suffix:", sizeStyle='small', selectable=True)

		self.w.suffixText = vanilla.TextBox("auto", "Suffix:", sizeStyle='small', selectable=True)
		self.w.suffix = vanilla.ComboBox("auto", self.fillSuffixes(), sizeStyle='small', callback=self.SavePreferences)
		self.w.suffix.setToolTip("Find all (exporting) glyphs that have this suffix and in OT feature ‘rand’, build a one-from-many substitution with them. Hint: keep the dot, but avoid the figures, e.g. for all stylistic sets, type ‘.ss’.")
		self.w.suffixReset = UpdateButton("auto", callback=self.updateSuffixs)
		self.w.suffixReset.setToolTip("Updates the list of suffixes from the frontmost font.")

		self.w.exclude = vanilla.CheckBox("auto", "Exclude glyphs containing:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.exclude.setToolTip("If checked, glyphs with names containing any of the listed particles are left out of the rand feature.")
		self.w.excludeList = vanilla.EditText("auto", ".build, .ss12", callback=self.SavePreferences, sizeStyle='small')
		self.w.excludeList.setToolTip("Comma-separated list of glyph name particles. Glyphs containing these particles in their names will be excluded from the rand feature generation.")

		self.w.includeDefault = vanilla.CheckBox("auto", "Include unsuffixed default in randomisation", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeDefault.setToolTip("If enabled, will substitute A from [A A.cv01 A.cv02]. If disabled, will substitute only from [A.cv01 A.cv02]. Usually, you will want to keep this on.")

		self.w.overwrite = vanilla.CheckBox("auto", "Overwrite existing rand feature", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.overwrite.setToolTip("If enabled, will recreate the existing randomisation feature from scratch. If disabled, will append the new code instead. Usually, you will want to keep this on.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Add Feature", callback=self.BuildRandFeatureMain)
		self.w.runButton.setToolTip("Builds the rand feature in the frontmost font.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the combo box takes the leftover width:
		nsLabel = self.w.suffixText.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# the checkbox hugs its title, the field behind it takes the rest:
		self.w.exclude.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.excludeList.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[suffixText]-gap-[suffix(>=100)]-gap-[suffixReset]-inset-|",
				"H:|-inset-[exclude]-gap-[excludeList(>=60)]-inset-|",
				"H:|-inset-[includeDefault]-(>=inset)-|",
				"H:|-inset-[overwrite]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-row-[suffix]-row-[exclude]-stackRow-[includeDefault]-stackRow-[overwrite]-inset-[runButton]-inset-|",
				{"view1": self.w.suffixText, "attribute1": "centerY", "view2": self.w.suffix, "attribute2": "centerY"},
				{"view1": self.w.suffixReset, "attribute1": "centerY", "view2": self.w.suffix, "attribute2": "centerY"},
				{"view1": self.w.excludeList, "attribute1": "centerY", "view2": self.w.exclude, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "stackRow": 8},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.excludeList.enable(self.w.exclude.get())

	def updateSuffixs(self, sender=None):
		if sender == self.w.suffixReset:
			self.w.suffix.setItems(self.fillSuffixes())

	def fillSuffixes(self, sender=None):
		thisFont = Glyphs.font  # frontmost font
		if thisFont is not None:
			suffixes = []
			for glyph in thisFont.glyphs:
				if "." in glyph.name[1:]:
					parts = glyph.name.split(".")
					for part in parts[1:]:
						if part:
							cleanedPart = ""
							for letter in part:
								if letter not in "1234567890":
									cleanedPart += letter
							if cleanedPart:
								suffixes.append(".%s" % cleanedPart)
			if suffixes:
				sortedSuffixes = sorted(set(suffixes))
				return sortedSuffixes

		# if all else fails
		return (".cv", ".ss", ".rand", ".random")

	def BuildRandFeatureMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Build rand Feature Report for %s" % thisFont.familyName)
				fileName = fontFileName(thisFont)
				print(f"📄 {fileName}")
				print()

				overwrite = self.pref("overwrite")
				suffix = self.pref("suffix")
				includeDefault = self.pref("includeDefault")
				exclude = self.pref("exclude")
				if exclude:
					excludeList = [particle.strip() for particle in self.pref("excludeList").split(",") if particle.strip()]
				else:
					excludeList = ()

				print("Scanning the glyph set...")
				variantDict = {}
				for thisGlyph in thisFont.glyphs:

					# see if glyph is excluded:
					excluded = False
					if excludeList:
						for particle in excludeList:
							if particle in thisGlyph.name:
								excluded = True
								break

					# populate variantDict with alternates, based on root glyph:
					if not excluded and thisGlyph.export and "." in thisGlyph.name and suffix in thisGlyph.name:
						root = getRootName(thisGlyph.name)
						if root not in variantDict.keys():
							variantDict[root] = [thisGlyph.name]
						else:
							variantDict[root].append(thisGlyph.name)

				if not variantDict.keys():
					msg = "Could not find any dot-suffixed glyphs for building the rand feature. Aborting."
					print(msg)
					Message(title="No Glyph Variants", message=msg, OKButton=None)
				else:
					otFeatureLines = []
					for rootName in sorted(variantDict.keys()):
						altNames = sorted(variantDict[rootName])

						# if desired, add default glyph (root name) to randomisation pool
						if includeDefault:
							altNames.insert(0, rootName)

						# build feature line:
						otFeatureLine = "sub %s from [%s];" % (
							rootName,
							" ".join(altNames),
						)
						otFeatureLines.append(otFeatureLine)
						print("🆗 %s: found %i alternate glyphs." % (rootName, len(altNames)))

					if not otFeatureLines:
						msg = "❌ Error. No OT feature code could be generated."
						print(msg)
						Message(title="Build rand Feature Error", message=msg, OKButton=None)
					else:
						otFeatureCode = "\n".join(otFeatureLines)
						feature = thisFont.features["rand"]
						if not feature:
							print("Building rand feature...")
							feature = GSFeature()
							feature.name = "rand"
							feature.code = otFeatureCode
							thisFont.features.append(feature)
						else:
							if overwrite:
								print("Overwriting existing rand feature...")
								feature.code = otFeatureCode
							else:
								print("Appending to existing rand feature...")
								feature.code += "\n\n# Automatic Feature Code:\n"
								feature.code += otFeatureCode

						print("Added %i lines of code." % len(otFeatureLines))

						# Final report:
						Glyphs.showNotification(
							"%s: Done" % (thisFont.familyName),
							"New rand feature with %i lines available in Font Info → Features. Details in Macro Window" % len(otFeatureLines),
						)
						print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Build rand Feature Error: %s" % e)
			import traceback
			print(traceback.format_exc())


BuildRandFeature()
