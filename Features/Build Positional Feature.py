# MenuTitle: Build Positional Feature
__doc__ = """
Create or update OpenType feature code for positional forms (isolated, initial, medial and final). Will also add respective OpenType classes.
"""

import vanilla
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, GSFeature, GSClass, Message
from mekkablue import mekkaObject, UpdateButton


def updatedCode(oldcode, beginsig, endsig, newcode):
	"""Replaces text in oldcode with newcode, but only between beginsig and endsig."""
	begin_offset = oldcode.find(beginsig)
	end_offset = oldcode.find(endsig) + len(endsig)
	newcode = oldcode[:begin_offset] + beginsig + newcode + "\n" + endsig + oldcode[end_offset:]
	return newcode


def createOTFeature(featureName="calt", featureCode="# empty feature code", targetFont=None, codeSig="DEFAULT-CODE-SIGNATURE", createSeparateEntry=False):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	"""

	if targetFont:
		beginSig = "# BEGIN " + codeSig + "\n"
		endSig = "# END " + codeSig + "\n"

		featuresWithTag = [f for f in targetFont.features if f.name == featureName and f.name]
		featureExists = len(featuresWithTag) > 0
		featuresWithSig = [f for f in targetFont.features if beginSig in f.code and endSig in f.code and f.active]
		sigExists = len(featuresWithSig) > 0

		if sigExists:
			for targetFeature in featuresWithSig:
				# replace old code with new code:
				targetFeature.code = updatedCode(targetFeature.code, beginSig, endSig, featureCode)
			return "✅ Updated %i existing OT feature%s ‘%s’." % (
				len(featuresWithSig),
				"" if len(featuresWithSig) == 1 else "s",
				featureName,
			)
		elif featureExists and not createSeparateEntry:
			# feature already exists:
			targetFeature = targetFont.features[featureName]  # take the first available one
			targetFeature.code += "\n" + beginSig + featureCode + "\n" + endSig
			return "✅ Added code to first available OT feature ‘%s’." % featureName
		else:
			# create feature with new code:
			newFeature = GSFeature()
			newFeature.name = featureName
			newFeature.code = beginSig + featureCode + "\n" + endSig
			targetFont.features.append(newFeature)
			return "🌟 Created new OT feature entry ‘%s’" % featureName
	else:
		return "🛑 ERROR: Could not create OT feature %s. No font detected." % (featureName)


def createOTClass(className="@default", classGlyphNames=[], targetFont=None, automate=False):
	"""
	Creates an OpenType class in the font.
	Default: class @default with currently selected glyphs in the current font.
	Returns a status message in form of a string.
	"""

	if targetFont and (classGlyphNames or automate):
		className = className.lstrip("@")  # strip '@' from beginning
		classCode = " ".join(classGlyphNames)
		otClass = None

		# build or update class:
		if className in [c.name for c in targetFont.classes]:
			otClass = targetFont.classes[className]
			otClass.code = classCode
			returnText = "✅ Updated existing OT class ‘%s’." % (className)
		else:
			otClass = GSClass()
			otClass.name = className
			otClass.code = classCode
			targetFont.classes.append(otClass)
			returnText = "🌟 Created new OT class: ‘%s’" % (className)

		# automate the class:
		if automate and otClass is not None:
			if Glyphs.versionNumber >= 3:
				# GLYPHS 3
				if otClass.canBeAutomated():
					otClass.automatic = True
			else:
				# GLYPHS 2
				otClass.automatic = True

			returnText = returnText.rstrip(".") + " (automated)."

		return returnText
	else:
		return "🛑 ERROR: Could not create OT class %s. Missing either font or glyph names, or both." % (className)


class BuildPositionalFeature(mekkaObject):
	prefDomain = "com.mekkablue.BuildPositionalFeature"
	prefDict = {
		"targetFeature": "calt",
		"suffixes": "init, medi, fina, isol",
		"sourceSuffix": "Def",
		"targetSuffix": "Sub",
		"automateAllLetters": True,
		"separateFeatureEntry": False,
	}

	title = "Build Positional Feature"

	def __init__(self):
		# Window 'self.w':
		windowWidth = 440
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			self.title,  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Build or update code for initial, medial, final and isolated forms", sizeStyle='small', selectable=True)

		self.w.targetFeatureText = vanilla.TextBox("auto", "Target feature (tag):", sizeStyle='small', selectable=True)
		self.w.targetFeature = vanilla.EditText("auto", "calt", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Feature tag for the OpenType feature that is supposed to receive the positional code."
		self.w.targetFeature.setToolTip(tooltip)
		self.w.targetFeatureText.setToolTip(tooltip)
		self.w.targetFeatureUpdate = UpdateButton("auto", callback=self.update)
		self.w.targetFeatureUpdate.setToolTip("Reset to defaults: ‘calt’")

		self.w.suffixesText = vanilla.TextBox("auto", "Suffixes (in,me,fi,is):", sizeStyle='small', selectable=True)
		self.w.suffixes = vanilla.EditText("auto", "init, medi, fina, isol", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Glyph suffixes in the font, for the four positions, in this order:\n1. initial\n2. medial\n3. final\n4. isolated"
		self.w.suffixes.setToolTip(tooltip)
		self.w.suffixesText.setToolTip(tooltip)
		self.w.suffixesUpdate = UpdateButton("auto", callback=self.update)
		self.w.suffixesUpdate.setToolTip("Reset to defaults: ‘init, medi, fina, isol’")

		tooltip = "Newly generated OT classes will be named after the positional tag (init, medi, fina, isol) plus a suffix for the source class (for the unsuffixed glyphs) or the target class (for the respectively suffixed glyphs). One of the suffixes can be left empty, but not both."
		self.w.sourceSuffixText = vanilla.TextBox("auto", "Suffix for source classes:", sizeStyle='small', selectable=True)
		self.w.sourceSuffix = vanilla.EditText("auto", "Def", callback=self.SavePreferences, sizeStyle='small')
		self.w.sourceSuffix.setToolTip(tooltip)
		self.w.sourceSuffixText.setToolTip(tooltip)
		self.w.sourceSuffixUpdate = UpdateButton("auto", callback=self.update)
		self.w.sourceSuffixUpdate.setToolTip("Reset to defaults: ‘Def’")

		self.w.targetSuffixText = vanilla.TextBox("auto", "Suffix for target classes:", sizeStyle='small', selectable=True)
		self.w.targetSuffix = vanilla.EditText("auto", "Sub", callback=self.SavePreferences, sizeStyle='small')
		self.w.targetSuffix.setToolTip(tooltip)
		self.w.targetSuffixText.setToolTip(tooltip)
		self.w.targetSuffixUpdate = UpdateButton("auto", callback=self.update)
		self.w.targetSuffixUpdate.setToolTip("Reset to defaults: ‘Sub’")

		self.w.automateAllLetters = vanilla.CheckBox("auto", "Automate ‘AllLetters’ feature class", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.automateAllLetters.setToolTip("The @AllLetters OpenType class can be automated (and thus, automatically kept up to date) by Glyphs. Enabling this option will add this class with the ‘Generate automatically’ option ON. Strongly recommended.")

		self.w.separateFeatureEntry = vanilla.CheckBox("auto", "Separate feature entry (i.e. do not reuse existing feature)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.separateFeatureEntry.setToolTip("If this option is enabled and the target feature already exists in Font Info → Features, will create a new entry with the same feature tag, rather than append the code to an existing feature entry.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Build", callback=self.BuildPositionalFeatureMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned, hug their text, and share the width of the widest one, so the fields line up:
		labelNames = ("targetFeatureText", "suffixesText", "sourceSuffixText", "targetSuffixText")
		widestLabel = "sourceSuffixText"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# one baseline per row:
		rowRules = []
		for labelName, fieldName, buttonName in (
			("targetFeatureText", "targetFeature", "targetFeatureUpdate"),
			("suffixesText", "suffixes", "suffixesUpdate"),
			("sourceSuffixText", "sourceSuffix", "sourceSuffixUpdate"),
			("targetSuffixText", "targetSuffix", "targetSuffixUpdate"),
		):
			rowRules.append({"view1": getattr(self.w, labelName), "attribute1": "centerY", "view2": getattr(self.w, fieldName), "attribute2": "centerY"})
			rowRules.append({"view1": getattr(self.w, buttonName), "attribute1": "centerY", "view2": getattr(self.w, fieldName), "attribute2": "centerY"})

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[targetFeatureText]-gap-[targetFeature]-gap-[targetFeatureUpdate]-inset-|",
				"H:|-inset-[suffixesText]-gap-[suffixes]-gap-[suffixesUpdate]-inset-|",
				"H:|-inset-[sourceSuffixText]-gap-[sourceSuffix]-gap-[sourceSuffixUpdate]-inset-|",
				"H:|-inset-[targetSuffixText]-gap-[targetSuffix]-gap-[targetSuffixUpdate]-inset-|",
				"H:|-inset-[automateAllLetters]-(>=inset)-|",
				"H:|-inset-[separateFeatureEntry]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[targetFeature]-row-[suffixes]-row-[sourceSuffix]-row-[targetSuffix]-row-[automateAllLetters]-checkRow-[separateFeatureEntry]-inset-[runButton]-inset-|",
			] + rowRules + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "headlineGap": 10, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		if sender == self.w.targetFeatureUpdate:
			self.setPref("targetFeature", "calt")
		elif sender == self.w.suffixesUpdate:
			self.setPref("suffixes", "init, medi, fina, isol")
		elif sender == self.w.sourceSuffixUpdate:
			self.setPref("sourceSuffix", "Def")
		elif sender == self.w.targetSuffixUpdate:
			self.setPref("targetSuffix", "Sub")

		self.LoadPreferences()

	def BuildPositionalFeatureMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(
					title="No Font Open",
					message="The script requires a font. Open a font and run the script again.",
					OKButton=None
				)
			else:
				print(f"‘{self.title}’ Report for {thisFont.familyName}")
				fileName = thisFont.filepath.lastPathComponent() if thisFont.filepath else f"{thisFont.familyName} (unsaved)"
				print(f"📄 {fileName}")
				print()

				# read user settings and supply fallback values if necessary:
				positionalFeature = self.pref("targetFeature").strip()
				if not positionalFeature or len(positionalFeature) > 4:
					print(f"⚠️ Invalid target feature tag: ‘{positionalFeature}’")
					positionalFeature = "calt"
					self.setPref("targetFeature", positionalFeature)
					self.LoadPreferences()

				extensionDef = self.pref("sourceSuffix").strip()
				extensionSub = self.pref("targetSuffix").strip()
				if not extensionDef and not extensionSub:
					print("⚠️ Both class suffixes cannot be empty at the same time. Restoring defaults.")
					extensionDef = "Def"
					extensionSub = "Sub"
					self.setPref("sourceSuffix", extensionDef)
					self.setPref("targetSuffix", extensionSub)
					self.LoadPreferences()

				suffixKeys = ("init", "medi", "fina", "isol")
				suffixDict = {}
				for suffix in suffixKeys:
					suffixDict[suffix] = suffix

				userSuppliedSuffixes = [suffix.strip() for suffix in self.pref("suffixes").split(",")]
				for suffixKey, userSuppliedSuffix in zip(suffixKeys, userSuppliedSuffixes):
					if userSuppliedSuffix:
						suffixDict[suffixKey] = userSuppliedSuffix

				# create or update AllLetters class
				anyLetterClassName = "AllLetters"
				automateAllLetters = self.prefBool("automateAllLetters")
				allLetterNames = [g.name for g in thisFont.glyphs if g.category == "Letter" and g.export]
				print("\t%s" % createOTClass(
					className=anyLetterClassName,
					classGlyphNames=allLetterNames,
					targetFont=thisFont,
					automate=automateAllLetters,
				))
				classCount = 1

				# build ignore statements
				ignoreStatements = {
					"isol": "ignore sub @isol%s' @%s, @%s @isol%s';" % (extensionDef, anyLetterClassName, anyLetterClassName, extensionDef),
					"init": "ignore sub @%s @init%s';" % (anyLetterClassName, extensionDef),
					"fina": "ignore sub @fina%s' @%s;" % (extensionDef, anyLetterClassName),
					"medi": "sub @%s @medi%s' @%s by @medi%s;" % (anyLetterClassName, extensionDef, anyLetterClassName, extensionSub),
				}

				positionalFeatureCode = "\n"
				for suffixKey in suffixKeys:
					thisSuffix = suffixDict[suffixKey]
					dotSuffix = "." + thisSuffix.strip(".")
					theseSuffixedGlyphNames = [
						g.name for g in thisFont.glyphs if dotSuffix in g.name  # glyph has suffix
						and g.export  # suffixed glyph exports
						and thisFont.glyphs[g.name.replace(dotSuffix, "")] is not None  # unsuffixed counterpart exists
						and thisFont.glyphs[g.name.replace(dotSuffix, "")].export  # unsuffixed glyph exports
					]
					theseSuffixedGlyphNames = list(set(theseSuffixedGlyphNames))  # make sure every glyph is unique
					theseUnsuffixedGlyphNames = [n.replace(dotSuffix, "") for n in theseSuffixedGlyphNames]

					print("\n\t🔠 Found %i glyphs with a %s suffix, and %i unsuffixed counterparts." % (len(theseSuffixedGlyphNames), dotSuffix, len(theseUnsuffixedGlyphNames)))

					if len(theseSuffixedGlyphNames) > 0:
						# BUILD SOURCE AND TARGET CLASSES

						print("\t%s" % createOTClass(className=suffixKey + extensionDef, classGlyphNames=theseUnsuffixedGlyphNames, targetFont=thisFont))
						print("\t%s" % createOTClass(className=suffixKey + extensionSub, classGlyphNames=theseSuffixedGlyphNames, targetFont=thisFont))
						classCount += 2

						# COLLECT FEATURE CODE

						thisIgnoreCode = ignoreStatements[suffixKey]

						if thisIgnoreCode.startswith("ignore"):
							ignoreSubstitution = "\tsub @%s%s' by @%s%s;\n" % (
								suffixKey,
								extensionDef,
								suffixKey,
								extensionSub,
							)
						else:
							ignoreSubstitution = ""

						positionalFeatureCode += "lookup %sForms {\n" % thisSuffix.title()
						positionalFeatureCode += "\t%s\n" % thisIgnoreCode
						positionalFeatureCode += ignoreSubstitution
						positionalFeatureCode += "} %sForms;\n\n" % thisSuffix.title()

				# BUILD FEATURE WITH COLLECTED CODE

				separateFeatureEntry = self.prefBool("separateFeatureEntry")
				positionalFeatureCode = f"\n{positionalFeatureCode.strip()}\n"
				print(
					"\n\t%s" % createOTFeature(
						featureName=positionalFeature,
						featureCode=positionalFeatureCode,
						targetFont=thisFont,
						codeSig="POSITIONAL ALTERNATES",
						createSeparateEntry=separateFeatureEntry,
					)
				)

				# close script window and update features:
				self.w.close()
				# thisFont.updateFeatures()
				thisFont.compileFeatures()

				# Final report:
				Glyphs.showNotification(
					f"{thisFont.familyName}: positional features built",
					"%i lines of code generated in %s, %i classes added or updated. Details in Macro Window." % (
						len(positionalFeatureCode.splitlines()),
						positionalFeature,
						classCount,
					),
				)
				print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"‘{self.title}’ Error: {e}")
			import traceback
			print(traceback.format_exc())


BuildPositionalFeature()
