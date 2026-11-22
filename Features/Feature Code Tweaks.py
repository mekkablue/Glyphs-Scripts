# MenuTitle: Feature Code Tweaks
__doc__ = """
Adds tweaks to OT feature code. Reports in Macro window.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, GSFeature, GSClass, GSFeaturePrefix, Message
from mekkablue import mekkaObject, createOTFeature, fontFileName


def filterActiveCode(code):
	activeCode = ""
	for line in code.splitlines():
		line = line.strip()
		if line and line[0] != "#" and not line.startswith("lookup") and not line.startswith("}") and not line.startswith("feature"):
			if "#" in line:
				activeCode += line[:line.find("#")]
			else:
				activeCode += line
			activeCode += "\n"
	return activeCode


def correspondingUppercaseForGlyphName(glyphname):
	glyphinfo = Glyphs.glyphInfoForName(glyphname)
	if not glyphinfo:
		return None
	else:
		lowercaseChar = glyphinfo.unicharString()
		if not lowercaseChar:
			return None
		else:
			uppercaseChar = glyphinfo.unicharString().upper()
			uppercaseName = Glyphs.niceGlyphName(uppercaseChar)
			if not uppercaseName:
				return None
			else:
				return uppercaseName


def addClass(otClassName, thisFont, forceUpdate=False):
	autoFeatures = ("All", "AllLetters", "Uppercase", "Lowercase")

	# Add class:
	otClass = thisFont.classes[otClassName]
	if not otClass:
		otClass = GSClass()
		otClass.name = otClassName
		if otClassName in autoFeatures:
			otClass.automatic = True
		thisFont.classes.append(otClass)
		print(f"✅ OT class @{otClassName} added.")

	# Force the update if required:
	if forceUpdate and not otClass.automatic:
		otClass.automatic = True
		print(f"✅ OT class @{otClassName}: Automated code.")

		# TODO: check if class still exists after force update, run again without forceUpdate

	# Update class:
	if otClass.automatic:
		otClass.update()
		print(f"✅ OT class @{otClassName}: Updated automatic code.")
	else:
		print(f"⚠️ Warning: OT class @{otClassName} is not set to automatic.")


def updateAndAutodisableFeatureInFont(featureName, thisFont):
	feature = thisFont.features[featureName]
	if feature:
		if feature.automatic:
			# update code, report if something changed
			oldCode = feature.code
			feature.update()
			if feature.code != oldCode:
				print(f"✅ Updated {featureName} feature code.")
			# disable automation and report:
			feature.automatic = False
			print(f"✅ Disabled automation in {featureName}.")
	else:
		print(f"⚠️ Feature {featureName} does not exist (yet).")


def createManyToOneFromDict(codeDict, thisFont):
	featureLines = ""
	ligNames = sorted(codeDict.keys(), key=lambda thisListItem: thisListItem.lower())

	for ligName in ligNames:

		# check if ligature glyphs is in font:
		ligGlyph = thisFont.glyphs[ligName]
		if ligGlyph and ligGlyph.export:

			# check if all parts are present:
			allParts = codeDict[ligName]
			allPartsPresent = True
			for thisPart in allParts:
				partGlyph = thisFont.glyphs[thisPart]
				if not (partGlyph and partGlyph.export):
					allPartsPresent = False

			if allPartsPresent:

				# build code line:
				separateGlyphs = " ".join(allParts)
				featureLines += f"	sub {separateGlyphs} by {ligName};\n"

				# frequent autocorrect replacements:
				autocorrectDict = {
					"hyphen hyphen": ("endash", "emdash"),
					"period period period": ("ellipsis", ),
				}
				for autocorrectString in autocorrectDict:
					possibleReplacements = autocorrectDict[autocorrectString]
					if autocorrectString in separateGlyphs:
						replacementClass = []
						for replacement in possibleReplacements:
							if thisFont.glyphs[replacement]:
								replacementClass.append(replacement)
						if replacementClass:
							replacementCode = " ".join(replacementClass)
							if len(replacementClass) > 1:
								replacementCode = f"[{replacementCode}]"
							separateGlyphs = separateGlyphs.replace(autocorrectString, replacementCode)
							featureLines += f"	sub {separateGlyphs} by {ligName};\n"

				print(f"✅ Adding ligature substitution for {ligName}.")
			else:
				print(f"⚠️ Warning: not all parts present for {ligName} ({', '.join(allParts)}), no substitution added.")
		else:
			print(f"⚠️ Warning: {ligName} is not present (or not set to export), no substitution added.")
	return featureLines


def wrapCodeInLookup(featureCode, lookupName):
	code = f"lookup {lookupName} {{" + "\n" + f"{featureCode.rstrip()}" + "\n" + f"}} {lookupName};" + "\n"
	return code


def createOTFeatureWithNote(
	featureName="calt",
	featureCode="# empty feature code",
	targetFont=None,
	codeSig="CUSTOM-CONTEXTUAL-ALTERNATES",
	appendCode=True,
	compileFeatures=True,
):
	"""
	Creates or updates an OpenType feature in the font (see createOTFeature), and adds the code with
	an instruction where it goes to the notes of the feature, for those who prefer to add it manually.
	"""
	if targetFont is None:
		targetFont = Glyphs.font
	featureCode = featureCode.rstrip()
	print(createOTFeature(featureName, featureCode, targetFont, codeSig, appendCode=appendCode, compileFeatures=compileFeatures))

	targetFeature = targetFont.features[featureName]
	if not targetFeature.notes:
		targetFeature.notes = ""
	if featureCode not in targetFeature.notes:
		position = "end" if appendCode else "beginning"
		targetFeature.notes = f"# Add at {position}:\n{featureCode}\n\n" + targetFeature.notes
		print(f"✅ Added manual instructions into notes of OT feature '{featureName}'.")


def featureLineContainingXAlsoContains(font, featureName="ccmp", lineContaining="@Markscomb =", alsoContains="acute"):
	"""
	Does feature featureName:
	a. have a line containing lineContaining?
	b. and if so, does that line contain alsoContains?
	"""
	feature = font.features[featureName]
	if feature:
		featureLines = feature.code.splitlines()
		relevantFeatureLines = [line for line in featureLines if lineContaining in line]
		for line in relevantFeatureLines:
			if alsoContains in line:
				return True
	return False


class FeatureCodeTweaks(mekkaObject):
	prefDict = {
		"scFeatureFix": 0,
		"addArrowLigs": 0,
		"germanLocalization": 0,
		"dutchLocalization": 0,
		"decomposePresentationForms": 0,
		"includeIJ": 0,
		"includeLdot": 0,
		"includeBalkan": 0,
		"repeatDecompositionInSC": 0,
		"repeatDecompositionInOtherAffectedFeatures": 0,
		"disableLiga": 0,
		"fShortSubstitution": 0,
		"magistra": 0,
		"ssXX2salt": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 410
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Feature Code Tweaks",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", __doc__.strip(), sizeStyle='small')

		self.w.scFeatureFix = vanilla.CheckBox("auto", "Fix smallcap features (smcp/c2sc)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.scFeatureFix.setToolTip("Adds missing smallcap substitutions for glyphs like idotless, jdotless, kgreenlandic and longs.")

		self.w.addArrowLigs = vanilla.CheckBox("auto", "Add arrow ligatures (dlig)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.addArrowLigs.setToolTip("Adds ligatures of hyphens with greater and less for left and right arrows, and double hyphen ligatures for arrows with .long suffix.")

		self.w.germanLocalization = vanilla.CheckBox("auto", "Add German cap sharp S code (locl, calt)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.germanLocalization.setToolTip("Automatically substitutes lowercase sharp s for uppercase sharp S between other uppercase letters. Adds a lookup in locl and calls the lookup in calt.")

		self.w.dutchLocalization = vanilla.CheckBox("auto", "Add proper Dutch localization (locl)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.dutchLocalization.setToolTip("Adds a different Dutch localization than the default. Will not substitute uppercase /J for /Jacute if a combining accent follows (as would be the case if the user follows the proper Unicode text entry).")

		self.w.decomposePresentationForms = vanilla.CheckBox("auto", "Decompose Latin presentation forms like fi and fl (ccmp)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.decomposePresentationForms.setToolTip("Adds precomposed but ligature characters like /fi and /fl (which are not supposed to be used in texts) to ccmp, and decomposes them into their character equivalents, f+i, f+l, etc. Strongly recommended because it preserves tracking and smallcap compatibility.")

		self.w.includeLdot = vanilla.CheckBox("auto", "Include Ldot, ldot, napostrophe (if present)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeLdot.setToolTip("Includes deprecated Ldot/ldot in ccmp decomposition.")

		self.w.includeBalkan = vanilla.CheckBox("auto", "Include Balkan digraphs ǳ, ǆ, ǉ, ǌ (if present)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeBalkan.setToolTip("Includes deprecated Slavic/Balkan digraphs in ccmp decomposition.")

		self.w.includeIJ = vanilla.CheckBox("auto", "Include IJ, ij (if present)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeIJ.setToolTip("Includes unused Durch and deprecated Afrikaans digraphs in ccmp decomposition.")

		self.w.disableLiga = vanilla.CheckBox("auto", "Disable affected ligature lines in liga, dlig (if present)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.disableLiga.setToolTip("Also disables ligatures in liga. Only recommended if your fi, fl, etc. look exactly like separate f+i, f+l, etc., i.e., if they are not really ligated.")

		self.w.repeatDecompositionInSC = vanilla.CheckBox("auto", "Repeat decomposition in smcp and c2sc", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.repeatDecompositionInSC.setToolTip("Calls the ccmp lookup at the beginning of smcp and c2sc. This makes decompositions (and hence, the small caps) work in the Adobe (Latin) Composers, which ignore ccmp.")

		self.w.repeatDecompositionInOtherAffectedFeatures = vanilla.CheckBox("auto", "Repeat decomposition in affected (non-SC) features", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.repeatDecompositionInOtherAffectedFeatures.setToolTip("Calls the ccmp lookup at the beginnings of all features that substitute affected glyphs, e.g., in ss01. This option ignores smcp and c2sc. ATTENTION: cannot parse nested lookups yet, so the result may be incomplete.")

		self.w.fShortSubstitution = vanilla.CheckBox("auto", "Add f.short contextual substitutions (calt)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.fShortSubstitution.setToolTip("Not implemented yet.")

		self.w.magistra = vanilla.CheckBox("auto", "Add Mag.a substitution (calt) and 90% kerning", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.magistra.setToolTip("Automatic feature code substitution for Austrian academic title Mag.a (Magistra). Recommended for fonts for the Austrian market or an Austrian client.")

		self.w.ssXX2salt = vanilla.CheckBox("auto", "Overwrite salt feature with ssXX lookups", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.ssXX2salt.setToolTip("Creates a universal salt feature including all ssXX substitutions. Careful: does not update, but overwrite the feature code. Will park the old feature code in the feature notes, though.")

		# self.w.scFeatureFix.enable(False)
		self.w.fShortSubstitution.enable(False)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Tweak", callback=self.FeatureCodeTweaksMain)
		self.w.runButton.setToolTip("Applies the checked tweaks to the feature code of the frontmost font.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[scFeatureFix]-(>=inset)-|",
				"H:|-inset-[addArrowLigs]-(>=inset)-|",
				"H:|-inset-[germanLocalization]-(>=inset)-|",
				"H:|-inset-[dutchLocalization]-(>=inset)-|",
				"H:|-inset-[decomposePresentationForms]-(>=inset)-|",
				"H:|-subInset-[includeLdot]-(>=inset)-|",
				"H:|-subInset-[includeBalkan]-(>=inset)-|",
				"H:|-subInset-[includeIJ]-(>=inset)-|",
				"H:|-subInset-[disableLiga]-(>=inset)-|",
				"H:|-subInset-[repeatDecompositionInSC]-(>=inset)-|",
				"H:|-subInset-[repeatDecompositionInOtherAffectedFeatures]-(>=inset)-|",
				"H:|-inset-[fShortSubstitution]-(>=inset)-|",
				"H:|-inset-[magistra]-(>=inset)-|",
				"H:|-inset-[ssXX2salt]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-row-[scFeatureFix]-stackRow-[addArrowLigs]-stackRow-[germanLocalization]-stackRow-[dutchLocalization]-stackRow-[decomposePresentationForms]-stackRow-[includeLdot]-stackRow-[includeBalkan]-stackRow-[includeIJ]-stackRow-[disableLiga]-stackRow-[repeatDecompositionInSC]-stackRow-[repeatDecompositionInOtherAffectedFeatures]-stackRow-[fShortSubstitution]-stackRow-[magistra]-stackRow-[ssXX2salt]-inset-[runButton]-inset-|",
			],
			metrics={"inset": inset, "subInset": inset + 24, "row": 8, "stackRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		onOrOff = self.pref("decomposePresentationForms")
		self.w.includeIJ.enable(onOrOff)
		self.w.includeLdot.enable(onOrOff)
		self.w.includeBalkan.enable(onOrOff)
		self.w.disableLiga.enable(onOrOff)
		self.w.repeatDecompositionInSC.enable(onOrOff)
		self.w.repeatDecompositionInOtherAffectedFeatures.enable(onOrOff)

	def decomposePresentationForms(self, feature="ccmp", includeIJ=False, includeLdot=False):
		decomposeDict = {
			"ff": ("f", "f"),
			"fi": ("f", "i"),
			"ffi": ("f", "f", "i"),
			"fl": ("f", "l"),
			"ffl": ("f", "f", "l"),
			"s_t": ("s", "t"),
			"longs_t": ("longs", "t"),
		}

		if self.pref("includeIJ"):
			includeIJ = {
				"ij": ("i", "j"),
				"IJ": ("I", "J"),
			}
			decomposeDict.update(includeIJ)

		if self.pref("includeLdot"):
			includeLdot = {
				"Ldot": ("L", "periodcentered.loclCAT.case"),
				"ldot": ("l", "periodcentered.loclCAT"),
				"napostrophe": ("quoteright", "n"),
			}
			decomposeDict.update(includeLdot)

		if self.pref("includeBalkan"):
			includeBalkan = {
				"LJ": ("L", "J"),
				"lj": ("l", "j"),
				"Lj": ("L", "j"),
				"NJ": ("N", "J"),
				"Nj": ("N", "j"),
				"nj": ("n", "j"),
				"DZ": ("D", "Z"),
				"Dz": ("D", "z"),
				"dz": ("d", "z"),
				"DZcaron": ("D", "Zcaron"),
				"Dzcaron": ("D", "zcaron"),
				"dzcaron": ("d", "zcaron"),
			}
			decomposeDict.update(includeBalkan)

		# collect feature code for all present glyphs:
		featureLines = ""
		thisFont = Glyphs.font
		ligNames = sorted(decomposeDict.keys(), key=lambda thisListItem: thisListItem.lower())
		disableList = []
		for ligName in ligNames:
			ligGlyph = thisFont.glyphs[ligName]
			if ligGlyph and ligGlyph.export:
				# check if all decomposition parts are in the font:
				decomposeParts = decomposeDict[ligName]
				shouldAddLine = True
				shouldConsiderUCInstead = False
				actualDecomposeParts = [name for name in decomposeParts]
				for i, glyphName in enumerate(decomposeParts):
					glyph = thisFont.glyphs[glyphName]

					# this should give the UC name in an all-cap double-encoding font:
					if glyph:
						actualDecomposeParts[i] = glyph.name

					# it it does not exist, check if a corresponding UC is there (all-cap font):
					if not glyph:
						uppercaseGlyphName = correspondingUppercaseForGlyphName(glyphName)
						if uppercaseGlyphName:
							uppercaseGlyph = thisFont.glyphs[uppercaseGlyphName]
							if uppercaseGlyph:
								shouldConsiderUCInstead = True
								actualDecomposeParts[i] = uppercaseGlyphName

					# if it exists, check if it also exports:
					elif not glyph.export:
						shouldAddLine = False

				if not shouldAddLine:
					print(f"⚠️ Warning: not all parts ({', '.join(decomposeParts)}) for decomposition of {ligName} present and exporting.")
				else:
					# build and add the code line:
					if ligGlyph.unicode is not None:
						disableList.append(actualDecomposeParts)
						decomposeResult = " ".join(actualDecomposeParts)
						featureLines += f"	sub {ligName} by {decomposeResult};\n"
						print(f"✅ {feature}: Adding decomposition for {ligName}.")
					else:
						print(f"⚠️ Ligature {ligName} has no Unicode, so no decomposition added.")

		# check if any code has been collected:
		if not featureLines:
			print(f"⚠️ Warning: No (exporting) presentation-form ligatures found in font, {feature} unchanged.")
		else:
			lookupName = "latinPresentationForms"

			# wrap featureLines in lookup block
			featureLines = wrapCodeInLookup(featureLines, lookupName)

			# see if ccmp exists, and create it if not:
			ccmpFeature = thisFont.features[feature]
			if not ccmpFeature:
				ccmpFeature = GSFeature()
				ccmpFeature.name = feature
				ccmpFeature.code = f"# Warning: {feature} created by script, please review."
				ccmpFeature.automatic = False
				print(f"⚠️ Warning: added empty, non-automated {feature} feature. Please review.")

				# check if aalt exists in first place:
				aaltExists = False
				if thisFont.features:
					if thisFont.features[0].name == "aalt":
						aaltExists = True
				thisFont.features.insert(
					1 if aaltExists else 0,
					ccmpFeature,
				)

			# prepare feature and inject code:
			updateAndAutodisableFeatureInFont(feature, thisFont)
			createOTFeatureWithNote(
				featureName=ccmpFeature.name,
				featureCode=featureLines,
				targetFont=thisFont,
				codeSig="Decompose presentation forms",
				appendCode=False,
				compileFeatures=False,
			)

			# repeat in Small Caps if necessary:

			affectedFeatures = []
			if self.pref("repeatDecompositionInSC"):
				affectedFeatures.extend(("smcp", "c2sc"))
			if self.pref("repeatDecompositionInOtherAffectedFeatures"):
				for affectedFeature in thisFont.features:
					if affectedFeature.name != feature:  # ccmp
						print("-----", affectedFeature.name)
						shouldAdd = False
						activeCode = filterActiveCode(affectedFeature.code)
						for removeWord in (";", "sub", "by", "pos", "feature"):
							activeCode = activeCode.replace(removeWord, "")
						activeCodeWords = activeCode.split()
						for ligName in decomposeDict:
							for particle in decomposeDict[ligName]:
								if particle in activeCodeWords:
									shouldAdd = True
						if shouldAdd:
							affectedFeatures.append(affectedFeature.name)

			if affectedFeatures:
				lookupCall = f"lookup {lookupName};"
				for featureTag in affectedFeatures:
					affectedFeature = thisFont.features[featureTag]
					if not affectedFeature:
						print(f"🤷🏻‍♀️ No {featureTag} feature found, could not repeat decomposition lookup.")
					else:
						createOTFeatureWithNote(
							featureName=featureTag,
							featureCode=lookupCall,
							targetFont=thisFont,
							codeSig="Decompose presentation forms",
							appendCode=False,
							compileFeatures=False,
						)
						if affectedFeature.automatic:
							affectedFeature.automatic = False
							print(f"✅ Disabled automatism for '{featureTag}'.")

						print(f"✅ Added call for decomposition lookup in {featureTag}.")

			# disable codelines if necessary:

			if self.pref("disableLiga"):
				# collect code to recognize (for disabling further below)
				linestarts = []
				for ligParts in disableList:
					linestart = f"sub {' '.join(ligParts)} by"
					linestarts.append(linestart)

				# look for code snippets and disable where found:
				for ligatureFeatureTag in ("dlig", "liga"):
					feature = thisFont.features[ligatureFeatureTag]
					if feature:
						originalCode = feature.code
						codeLines = originalCode.splitlines()
						for i, codeLine in enumerate(codeLines):
							for linestart in linestarts:
								if codeLine.startswith(linestart):
									codeLines[i] = f"# {codeLine}"
									if feature.automatic:
										feature.automatic = False
										print(f"✅ Disabled automatism for '{ligatureFeatureTag}'.")
									print(f"✅ Commented out line in {ligatureFeatureTag}: {codeLine}")

						newCode = "\n".join(codeLines)
						if originalCode == newCode or feature.automatic:
							print(f"🤷🏻‍♀️ Feature {ligatureFeatureTag} not changed. No ligatures to disable.")
						else:
							thisFont.features[ligatureFeatureTag].code = newCode
							print(f"✅ {ligatureFeatureTag}: updated feature code.")

	def dutchLocalization(self, feature="locl"):
		"""
		lookup NLD {
			language NLD;
			sub iacute j' by jacute;
			# Try other ignore line if first one does not work:
			ignore sub J' [@MarkscombCase @Markscomb];
			# ignore sub J' @CombiningTopAccents;
			sub Iacute J' by Jacute;
			# Make sure Glyph Info for ...comb.sc accents has subcategory=Nonspacing
			# Don't forget: j.sc=jdotless.sc (& verify kerning groups)
		} NLD;
		# DO NOT FORGET TO UPDATE LANGUAGESYSTEMS
		# DO NOT FORGET TO REMOVE DEFAULT NLD CODE
		"""
		thisFont = Glyphs.font

		# check for I, J, Iacute, Jacute, i, j, iacute, jacute, jdotless:

		# collect exporting combining top accents:
		ccmpFeature = thisFont.features["ccmp"]
		markCode = None
		if ccmpFeature and "@Markscomb" in ccmpFeature.code and featureLineContainingXAlsoContains(
			thisFont, featureName="ccmp", lineContaining="@Markscomb =", alsoContains="acute"
		):
			# reuse ccmp classes:
			wordsInFeature = ccmpFeature.code.split()
			marks = []
			for searchWord in ("@Markscomb", "@MarkscombCase"):
				if searchWord in wordsInFeature:
					marks.append(searchWord)
			markCode = " ".join(marks)
			if len(marks) > 1:
				markCode = f"[{markCode}]"
		elif ccmpFeature and "@CombiningTopAccents" in ccmpFeature.code and featureLineContainingXAlsoContains(
			thisFont, featureName="ccmp", lineContaining="@CombiningTopAccents =", alsoContains="acute"
		):
			# reuse ccmp class:
			markCode = "@CombiningTopAccents"
		else:
			# build own class:
			accentNames = [g.name for g in thisFont.glyphs if g.category == "Mark" and g.subCategory == "Nonspacing"]
			if not accentNames:
				print("⚠️ Warning: No combining accents found in font. Consider adding at least acutecomb(.case/.sc).")
			else:
				markCode = " ".join(accentNames)
				if len(accentNames) > 1:
					markCode = f"[{markCode}]"

		if not markCode:
			ignoreLine = ""
		else:
			ignoreLine = f"\tignore sub J' {markCode};\n"

		loclCode = "\tlanguage NLD;"
		originalLength = len(loclCode)
		codesNLD = (
			("\n\tsub iacute j' by jacute;", ("jacute", "j", "iacute")),
			(f"\n{ignoreLine}\tsub Iacute J' by Jacute;", ("Iacute", "J", "Jacute")),
		)

		for codeLineData in codesNLD:
			lineToAdd = codeLineData[0]
			partsForCode = codeLineData[1]
			addLine = True
			for glyphName in partsForCode:
				glyph = thisFont.glyphs[glyphName]
				if not glyph or not glyph.export:
					addLine = False
					print(f"⚠️ Warning: Necessary glyph {glyphName} is missing or not exporting. Feature code will be incomplete.")
			if addLine:
				loclCode += lineToAdd

		if not len(loclCode) > originalLength:
			print(f"⛔️ Error: Could not add any NLD code, {feature} unchanged.")
		else:
			# prepare locl code:
			loclCode = wrapCodeInLookup(loclCode, "NLD")

			# prepare OT feature:
			updateAndAutodisableFeatureInFont("locl", thisFont)
			loclFeature = thisFont.features["locl"]

			if not loclFeature:
				print("⛔️ Error: Feature locl not present anymore. Aborting.")
			else:

				# Remove existing NLD code:
				if "NLD" in loclFeature.code:
					codeLines = loclFeature.code.splitlines()
					updatedCode = ""
					isDutch = False
					for line in codeLines:
						if line.startswith("language NLD;"):
							isDutch = True
						elif line.startswith("language "):
							isDutch = False
						if not isDutch or line.startswith("#"):
							updatedCode += line
							updatedCode += "\n"
					if loclFeature.code != updatedCode:
						loclFeature.code = updatedCode
						print("✅ Removed old NLD code from locl.")

				# Add/update NLD code:
				createOTFeatureWithNote(
					featureName="locl",
					featureCode=loclCode,
					targetFont=thisFont,
					codeSig="Dutch accented IJ/ij",
					appendCode=True,
					compileFeatures=False,
				)

			# TODO create jdotless.sc

	def germanLocalization(self, feature="calt"):
		thisFont = Glyphs.font
		ucClassName = "Uppercase"

		lcSharpS = thisFont.glyphs["germandbls"]
		ucSharpS = thisFont.glyphs["germandbls.calt"]
		if not ucSharpS or not ucSharpS.export:
			ucSharpS = thisFont.glyphs["Germandbls"]

		if not lcSharpS or not ucSharpS:
			print(f"⚠️ Warning: No LC and UC sharp s found in the font, {feature} unchanged.")
		elif not lcSharpS.export or not ucSharpS.export:
			print(f"⚠️ Warning: /{lcSharpS.name} and /{ucSharpS.name} are not both set to export, {feature} unchanged.")
		else:
			# Add @Uppercase:
			addClass("Uppercase", thisFont)

			# Feature code:
			lookupName = "uppercaseSharpS"
			featureLines = "\tsub @%s @%s %s' by %s;\n\tsub %s' @%s by %s;" % (
				ucClassName,
				ucClassName,
				lcSharpS.name,
				ucSharpS.name,
				# ucClassName,
				lcSharpS.name,
				ucClassName,
				ucSharpS.name,
			)
			featureLines = wrapCodeInLookup(featureLines, lookupName)

			# see if locl exists, and create it if not:
			loclFeature = thisFont.features["locl"]
			if not loclFeature:
				loclFeature = GSFeature()
				loclFeature.name = "locl"
				loclFeature.code = "# Warning: locl created by script, please review."
				loclFeature.automatic = False

				# check if aalt/ccmp exist at beginning place:
				insertIndex = 0
				if thisFont.features:
					for featureIndex in (0, 1):
						thisFeature = thisFont.features[featureIndex]
						if thisFeature:
							if thisFeature.name in ("aalt", "ccmp"):
								insertIndex += 1
				thisFont.features.insert(insertIndex, loclFeature)
				print(f"✅ Added locl feature at index {insertIndex}.")

			# if locl is automated, update it once more and disable automation:
			updateAndAutodisableFeatureInFont("locl", thisFont)

			# add lookup to locl:
			loclCode = f"language DEU;\n{featureLines}\n"
			createOTFeatureWithNote(
				featureName="locl",
				featureCode=loclCode,
				targetFont=thisFont,
				codeSig="German cap sharp s",
				appendCode=True,
				compileFeatures=False,
			)

			# call lookup in calt:
			caltCode = f"lookup {lookupName};"
			createOTFeatureWithNote(
				featureName=feature,
				featureCode=caltCode,
				targetFont=thisFont,
				codeSig="German cap sharp s",
				appendCode=True,
				compileFeatures=False,
			)

			# Update Languagesystems:
			prefixName = "Languagesystems"
			prefix = thisFont.featurePrefixes[prefixName]
			if not prefix:
				prefix = GSFeaturePrefix()
				prefix.name = prefixName
				prefix.automatic = True
				thisFont.featurePrefixes.insert(0, prefix)
				print("✅ Added 'Languagesystems' to feature code prefixes.")

			if not prefix.automatic:
				prefix.automatic = True
				print("✅ Automated 'Languagesystems' prefix.")

			oldCode = prefix.code
			prefix.update()
			if prefix.code != oldCode:
				print("✅ Updated 'Languagesystems' prefix.")

	def addArrowLigs(self, feature="dlig"):
		"""
		sub hyphen hyphen greater by rightArrow.long;
		sub hyphen greater by rightArrow;
		sub less hyphen hyphen by leftArrow.long;
		sub less hyphen by leftArrow;
		sub less hyphen greater by leftRightArrow;
		sub less hyphen hyphen greater by leftRightArrow.long;
		"""
		thisFont = Glyphs.font
		ligDict = {
			"leftArrow": ["less", "hyphen"],
			"leftArrow.long": ["less", "hyphen", "hyphen"],
			"leftRightArrow": ["less", "hyphen", "greater"],
			"leftRightArrow.long": ["less", "hyphen", "hyphen", "greater"],
			"rightArrow": ["hyphen", "greater"],
			"rightArrow.long": ["hyphen", "hyphen", "greater"],
		}

		# create feature code:
		featureLines = createManyToOneFromDict(ligDict, thisFont)
		if not featureLines:
			print(f"🤷🏻‍♀️ Warning: could not create arrow ligatures, {feature} unchanged.")
		else:
			# wrap featureLines in lookup block:
			featureLines = wrapCodeInLookup(featureLines, "arrows")

			# add to dlig:
			createOTFeatureWithNote(
				featureName=feature,
				featureCode=featureLines,
				targetFont=thisFont,
				codeSig="Arrows as ligatures",
				appendCode=True,
				compileFeatures=False,
			)

	def magistraSubstitution(self, feature="calt"):
		"""
		sub M a g period a' by ordfeminine;
		# add .sc
		pos M a g period a' <-50 0 -50 0>;
		"""
		thisFont = Glyphs.font

		canBuildCode = True
		requiredGlyphs = ("M", "a", "g", "period", "ordfeminine")
		for glyphName in requiredGlyphs:
			glyph = thisFont.glyphs[glyphName]
			if not glyph:
				print(f"⛔️ Missing glyph '{glyphName}' required for the feature code.")
				canBuildCode = False
			elif not glyph.export:
				print(f"⛔️ Glyph '{glyphName}' required for feature code exists, but is not exporting.")
				canBuildCode = False

		if not canBuildCode:
			print(f"⚠️ Leaving {feature} unchanged.")
		else:
			# add class if missing:
			addClass("AllLetters", thisFont, forceUpdate=True)

			# add feature code
			featureCode = "\tignore sub M a g period a' @AllLetters;"
			featureCode += "\n\tsub M a g period a' by ordfeminine;"
			featureCode = wrapCodeInLookup(featureCode, "magistra")
			createOTFeatureWithNote(
				featureName=feature,
				featureCode=featureCode,
				targetFont=thisFont,
				codeSig="Magistra",
				appendCode=True,
				compileFeatures=False,
			)

			# add kerning:
			for thisMaster in thisFont.masters:
				masterID = thisMaster.id

				# take the smaller glyph width and kern by 90% of that:
				minimalWidth = min(thisFont.glyphs["period"].layers[masterID].width, thisFont.glyphs["ordfeminine"].layers[masterID].width)

				# compoensate by kerning value on Other side: Mag<>.
				g = thisFont.glyphs["g"]
				period = thisFont.glyphs["period"]
				kernValueOnOtherSide = 0
				potentialKernValuesOnOtherSide = (
					thisFont.kerningForPair(masterID, f"@MMK_L_{g.rightKerningGroup}", f"@MMK_R_{period.leftKerningGroup}"),
					thisFont.kerningForPair(masterID, "g", f"@MMK_R_{period.leftKerningGroup}"),
					thisFont.kerningForPair(masterID, f"@MMK_L_{g.rightKerningGroup}", "period"),
					thisFont.kerningForPair(masterID, "g", "period"),
				)
				for value in potentialKernValuesOnOtherSide:
					if value is not None and value < 100000:
						kernValueOnOtherSide = value

				# calculate and add kerning:
				kernValue = round(-0.9 * minimalWidth - kernValueOnOtherSide)
				if abs(kernValue) > 5.0:
					thisFont.setKerningForPair(masterID, "period", "ordfeminine", kernValue)
					print(f"✅ Added kerning for period-ordfeminine ({kernValue:.1f}) in master '{thisMaster.name}'")
				else:
					print(f"⚠️ Calculated kerning for period-ordfeminine too small ({kernValue:.1f}), no pair added in master '{thisMaster.name}'")

	def fShortSubstitution(self, feature="calt"):
		"""
		@TooHighOnLeftSide = [b eth h hbar i iacute ibreve icaron icircumflex idieresis idotaccent idotbelow igrave imacron iogonek itilde j k kcommaaccent l lacute lcaron lcommaaccent ldot ncaron ntilde obreve ocaron ocircumflex odieresis ograve omacron otilde thorn rcaron scaron germandbls ubreve ucaron ucircumflex udieresiscaron udieresisgrave udieresismacron ugrave uhungarumlaut umacron utilde ygrave zcaron parenright braceright bracketright parenright.case braceright.case bracketright.case quotedblright quoteright quotedblleft quoteleft quotedbl quotesingle];
		sub f' @TooHighOnLeftSide by f.short;
		# other short variants?
		# - compounds (fdotaccent)
		# - ligatures like f_f.(liga.)short
		"""
		pass

	def ssXX2salt(self, saltTag="salt"):
		"""Creates a universal salt feature including all ssXX substitutions."""
		thisFont = Glyphs.font  # frontmost font
		ssXXfeatures = [f for f in thisFont.features if f.name.startswith("ss") and f.name[-1] in "0123456789" and f.name[-2] in "012"]

		if not ssXXfeatures:
			print(f"🤷🏻‍♀️ Warning: no ssXX features found in frontmost font ({thisFont.familyName}), skipping 'salt'.")
		else:
			print(
				"✅ Found %i stylistic set%s: %s. Building salt code..." % (
					len(ssXXfeatures),
					"" if len(ssXXfeatures) == 1 else "s",
					", ".join([f.name for f in ssXXfeatures]),
				)
			)
			saltFeature = GSFeature()
			saltFeature.name = saltTag
			saltFeature.automatic = False
			saltFeature.code = ""
			alreadyHadTheFeature = []
			alreadyHadTheLookup = []
			for thisFeature in ssXXfeatures:
				if "lookup" in thisFeature.code:
					if thisFeature.code.strip() not in alreadyHadTheLookup:
						saltFeature.code += f"# Lookup code for {thisFeature.name}:\n"
						saltFeature.code += thisFeature.code
						saltFeature.code += "\n"
						alreadyHadTheLookup.append(thisFeature.code.strip())
				else:
					ssXXcode = ""
					for ssXXline in thisFeature.code.splitlines():
						ssXXcode += f"\t{ssXXline}\n"

					# avoid duplicate lookup names
					ssXXname = thisFeature.name
					i = 0
					while ssXXname in alreadyHadTheFeature:
						i += 1
						ssXXname = f"{thisFeature.name}_{i:03}"
					alreadyHadTheFeature.append(ssXXname)

					lookupCode = "lookup salt_%s {\n%s\n} salt_%s;\n\n" % (
						ssXXname,
						ssXXcode.rstrip(),
						ssXXname,
					)
					saltFeature.code += lookupCode

			saltFeature.code = saltFeature.code.strip() + "\n"

			if thisFont.features["salt"] and thisFont.features["salt"].code == saltFeature.code:
				print("🤷🏻‍♀️ Feature salt already exists and is up to date, skipping 'salt'.")
			elif saltFeature.code:
				# delete existing salt feature, if there is one:
				if thisFont.features["salt"]:
					saltFeature.notes = "# OLD CODE:\n" + thisFont.features["salt"].code
					del (thisFont.features["salt"])
					print("✅ Deleted existing 'salt' feature.")

				# add salt in front of first ssXX:
				i = 0
				# step through features until we can add salt:
				while not thisFont.features["salt"]:
					f = thisFont.features[i]
					# first ssXX feature:
					if f.name == ssXXfeatures[0].name:
						# add the new salt feature in the right spot:
						thisFont.insertObject_inFeaturesAtIndex_(saltFeature, i)
						print("✅ Inserted new 'salt' feature in front of first ssXX.")
					i += 1
			else:
				print("⛔️ Build salt error: No salt feature code could be assembled. Please check the contents of your ssXX features. Skipping 'salt'.")

	def scFeatureFix(self):
		"""
		MarksCombCase --> MarksComb
		lookup capMarksToSC {
			sub @MarkscombCase by @Markscomb;
		} capMarksToSC;

		jdotless --> j.sc
		idotless --> i.sc
		"""
		thisFont = Glyphs.font
		ccmpFeature = thisFont.features["ccmp"]

		# 1. CAP MARKS IN C2SC
		scFeatureTag = "c2sc"
		if not thisFont.features[scFeatureTag]:
			print(f"⚠️ No {scFeatureTag} feature found. Skipping.")
		else:
			code = ""
			if ccmpFeature and "@MarkscombCase" in ccmpFeature.code:
				# reuse ccmp classes:
				code = "\tsub @MarkscombCase by @Markscomb;"
			else:
				# TODO or make your own:
				print("⚠️ Warning: could not create c2sc code for *comb.case marks (not implemented yet)")
				pass

			if not code:
				print(f"🤷🏻‍♀️ No code could be formed based on the available glyphs. Leaving {scFeatureTag} unchanged.")
			else:
				# add code to feature:
				updateAndAutodisableFeatureInFont(scFeatureTag, thisFont)
				code = wrapCodeInLookup(code, "capMarksToSC")
				createOTFeatureWithNote(
					featureName=scFeatureTag,
					featureCode=code,
					targetFont=thisFont,
					codeSig="Prepare cap marks for smallcaps",
					appendCode=False,
					compileFeatures=False,
				)

		# 2. SMCP: SMALL LETTERS WHERE CASEFOLDING CAN OVERLAP WITH OTHERS
		scFeatureTag = "smcp"
		if not thisFont.features[scFeatureTag]:
			print(f"⚠️ No {scFeatureTag} feature found. Skipping.")
		else:
			code = ""
			casefoldings = {
				"kgreenlandic": "k",
				"idotless": "i",
				"jdotless": "j",
				"longs": "s",
			}
			scSuffixes = ("sc", "smcp", "c2sc", "small", "smallcap")
			for smallGlyphName in sorted(casefoldings.keys()):
				smallGlyph = thisFont.glyphs[smallGlyphName]

				# determine proper .sc glyph:
				correspondingSC = None
				for suffix in scSuffixes:
					if not correspondingSC:
						correspondingSC = thisFont.glyphs[f"{smallGlyphName}.{suffix}"]

				# if proper .sc does not exist, casemap it to alternate SC:
				if smallGlyph and smallGlyph.export:
					if not correspondingSC or (correspondingSC and not correspondingSC.export):
						altSCcore = casefoldings[smallGlyphName]
						altSCexists = False
						for suffix in scSuffixes:
							if not altSCexists:
								altSCname = f"{altSCcore}.{suffix}"
								altSC = thisFont.glyphs[altSCname]
								if altSC and altSC.export:
									altSCexists = True
						if altSCexists and altSCname:
							code += f"sub {smallGlyphName} by {altSCname};\n"
							if thisFont.glyphs["quoteright"]:
								code = code.replace(f"sub kgreenlandic by {altSCname};", f"sub kgreenlandic by {altSCname} quoteright;")
							print(f"✅ {scFeatureTag}: Adding substitution for {smallGlyphName} to {altSCname}.")

			if not code:
				print(f"🤷🏻‍♀️ No code could be formed based on the available glyphs. Leaving {scFeatureTag} unchanged.")
			else:
				# add code to feature:
				updateAndAutodisableFeatureInFont(scFeatureTag, thisFont)
				createOTFeatureWithNote(
					featureName=scFeatureTag,
					featureCode=code.rstrip(),
					targetFont=thisFont,
					codeSig="Alternate small-cap mappings",
					appendCode=True,
					compileFeatures=False,
				)

	def FeatureCodeTweaksMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences(self)

			# brings macro window to front and clears its log:
			Glyphs.clearLog()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			print(f"Feature Code Tweaks for {thisFont.familyName}")
			fileName = fontFileName(thisFont)
			print(f"📄 {fileName}")

			# ccmp fi, fl, etc.
			if self.pref("scFeatureFix"):
				print("\n- SC Feature Fix")
				self.scFeatureFix()

			# arrows
			if self.pref("addArrowLigs"):
				print("\n- Add Arrow Ligs")
				self.addArrowLigs()

			# locl DEU: calt G/germandbls
			if self.pref("germanLocalization"):
				print("\n- German Localization")
				self.germanLocalization()

			# locl NLD
			if self.pref("dutchLocalization"):
				print("\n- Dutch Localization")
				self.dutchLocalization()

			# SC additions (i/jdotless)
			if self.pref("decomposePresentationForms"):
				print("\n- Decompose Presentation Forms")
				self.decomposePresentationForms()

			# short f substitution
			if self.pref("fShortSubstitution"):
				print("\n- Add f.short substitutions")
				self.fShortSubstitution()

			# Mag.a
			if self.pref("magistra"):
				print("\n- Add Mag.a substitutions")
				self.magistraSubstitution()

			# ssXX to salt
			if self.pref("ssXX2salt"):
				print("\n- Add salt feature with ssXX lookups")
				self.ssXX2salt()

			# all feature code is in place, so compile once, after the last addition:
			tweakNames = ("scFeatureFix", "addArrowLigs", "germanLocalization", "dutchLocalization", "decomposePresentationForms", "fShortSubstitution", "magistra", "ssXX2salt")
			if any(self.pref(tweakName) for tweakName in tweakNames):
				print("\n🫱🏾‍🫲🏻 Recompiling features...")
				thisFont.compileFeatures()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"❌ Feature Code Tweaks Error: {e}")
			import traceback
			print(traceback.format_exc())


FeatureCodeTweaks()
