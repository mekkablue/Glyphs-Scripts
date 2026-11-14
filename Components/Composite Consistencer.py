# MenuTitle: Composite Consistencer
__doc__ = """
Goes through all glyphs of the frontmost font (or all open fonts), and checks for composites. If dot-suffixed glyph variants are missing them, they are reported in the Macro Window and can optionally be created automatically.
"""

import vanilla
from AppKit import NSTextAlignmentRight, NSWindowStyleMaskResizable, NSSize, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message, GSGlyph, GSComponent
from mekkablue import mekkaObject, UpdateButton, setMacroDivider

defaultSuffixes = ".dnom, .numr, .subs, .sups, .sinf, .alt, .case, .tf, .tosf, .osf"


def normalizedSuffixOrder(name):
	particles = name.split(".")
	if len(particles) > 1:
		particles = [particles[0]] + sorted(particles[1:])
		name = ".".join(particles)
	return name


class CompositeConsistencer(mekkaObject):
	prefDict = {
		"ignore": defaultSuffixes,
		"ignoreDuplicateSuffixes": True,
		"suffixOrderMatters": False,
		"allFonts": False,
		"includeNonExporting": False,
		"selectedOnly": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Composite Consistencer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Find missing suffixed composites", sizeStyle='small', selectable=True)
		self.w.descriptionText.setToolTip("For every glyph used as a component, the script checks whether equivalent composites exist for all dot-suffixed variants of that glyph. For example, if 'a' is used in 'ae' and 'a.sc' exists, it checks that 'ae.sc' also exists.")

		self.w.ignoreText = vanilla.TextBox("auto", "Ignore suffixes", sizeStyle='small', selectable=True)
		self.w.ignoreText.setToolTip("Suffixes listed here are skipped entirely. Missing composites for these suffixes are not reported.")
		self.w.ignore = vanilla.EditText("auto", defaultSuffixes, callback=self.SavePreferences, sizeStyle='small')
		self.w.ignore.setToolTip("Comma-separated dot-suffixes to skip. Composites whose suffix appears here are not reported as missing. Example: .sc, .tf")
		self.w.updateIgnore = UpdateButton("auto", callback=self.updateIgnoreSuffixes)
		self.w.updateIgnore.setToolTip("Collect all dot-suffixes present in the current font and merge them into the ignore list, so you can edit the list yourself more easily. If no font is open, resets the list to the default suffixes.")

		self.w.ignoreDuplicateSuffixes = vanilla.CheckBox("auto", "Ignore duplicate suffixes (.ss01.ss01)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreDuplicateSuffixes.setToolTip("Skip composites whose generated name would repeat the same suffix twice. For example: if ae.ss01 uses a as a component and a.ss01 exists, the script would normally flag ae.ss01.ss01 as missing — this option suppresses that.")

		self.w.suffixOrderMatters = vanilla.CheckBox("auto", "Order of suffixes matters (.case.ss01 and .ss01.case)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.suffixOrderMatters.setToolTip("When unchecked (recommended), suffix order is normalised alphabetically so .case.ss01 and .ss01.case are treated as the same glyph. When checked, they are treated as distinct glyphs and both may be reported.")

		self.w.allFonts = vanilla.CheckBox("auto", "Check all open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allFonts.setToolTip("Scan all currently open fonts instead of only the frontmost one. Each font is reported separately in the Macro Window.")

		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.setToolTip("Also look for missing composites among glyphs whose Export is disabled. By default only exported glyphs are considered as targets.")

		self.w.selectedOnly = vanilla.CheckBox("auto", "Check selected glyphs only", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.selectedOnly.setToolTip("Restrict the base-glyph search to glyphs currently selected in the Font tab. Useful for checking a specific subset without scanning the entire font.")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)

		self.w.status = vanilla.TextBox("auto", "", sizeStyle='small')
		self.w.status.setToolTip("Result of the last Find or Create run.")
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Buttons:
		self.w.createButton = vanilla.Button("auto", "Create", callback=self.CompositeConsistencerCreate)
		self.w.createButton.setToolTip("Create all missing composite glyphs found with the current settings. Each new glyph copies the component structure of the existing composite, substituting component names with their suffixed equivalents where available.")
		self.w.runButton = vanilla.Button("auto", "Find", callback=self.CompositeConsistencerMain)
		self.w.runButton.setToolTip("Scan the font and list all missing suffixed composites in the Macro Window.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the field takes the leftover width:
		nsLabel = self.w.ignoreText.getNSTextField()
		nsLabel.setAlignment_(NSTextAlignmentRight)
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[ignoreText]-gap-[ignore]-gap-[updateIgnore]-inset-|",
				"H:|-inset-[ignoreDuplicateSuffixes]-(>=inset)-|",
				"H:|-inset-[suffixOrderMatters]-(>=inset)-|",
				"H:|-inset-[allFonts]-(>=inset)-|",
				"H:|-inset-[includeNonExporting]-(>=inset)-|",
				"H:|-inset-[selectedOnly]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-inset-[createButton(>=70)]-gap-[status]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[ignore]-headlineGap-[ignoreDuplicateSuffixes]-checkRow-[suffixOrderMatters]-checkRow-[allFonts]-checkRow-[includeNonExporting]-checkRow-[selectedOnly]-barGap-[progress(16)]-inset-[runButton]-inset-|",
				"V:[createButton]-inset-|",
				{"view1": self.w.ignoreText, "attribute1": "centerY", "view2": self.w.ignore, "attribute2": "centerY"},
				{"view1": self.w.updateIgnore, "attribute1": "centerY", "view2": self.w.ignore, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "headlineGap": 10, "checkRow": 5, "barGap": 14},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# make the window horizontally resizable, but keep the height that Auto Layout determined.
		# (Content sizes set directly on the NSWindow, so the title bar is not counted twice.)
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()  # make sure the content has its final size before we read it
		contentSize = nsWindow.contentView().frame().size
		nsWindow.setContentMinSize_(NSSize(contentSize.width, contentSize.height))
		nsWindow.setContentMaxSize_(NSSize(contentSize.width + 1000, contentSize.height))

	def prepareReport(self):
		"""
		Brings up the Macro Window FIRST, then clears the log and moves the divider up, so the report has room.
		In Glyphs 4, output printed before the Macro Window is shown does not appear in it.
		"""
		Glyphs.showMacroWindow()
		Glyphs.clearLog()
		setMacroDivider(0.1)

	def fileLabel(self, thisFont):
		return thisFont.filepath.lastPathComponent() if thisFont.filepath else f"{thisFont.familyName} (unsaved)"

	def collectMissingData(self, thisFont, ignoredSuffixes, ignoreDuplicateSuffixes, suffixOrderMatters, includeNonExporting, selectedOnly):
		"""
		Scan thisFont for missing suffixed composites.
		Returns a list of (otherName, [(sourceCompositeName, missingCompositeName, suffix), ...]) tuples.
		sourceCompositeName is the actual (un-normalized) glyph name to use as template when creating.
		"""
		allNames = [g.name for g in thisFont.glyphs] if includeNonExporting else [g.name for g in thisFont.glyphs if g.export]
		allNamesSet = set(allNames)
		if not suffixOrderMatters:
			allNames = [normalizedSuffixOrder(n) for n in allNames]
			allNamesSet = set(allNames)

		if selectedOnly:
			selectedGlyphNames = set(layer.parent.name for layer in thisFont.selectedLayers)
			glyphsToCheck = [g for g in thisFont.glyphs if g.name in selectedGlyphNames]
		else:
			glyphsToCheck = list(thisFont.glyphs)

		results = []
		for glyphIndex, thisGlyph in enumerate(glyphsToCheck):
			self.w.progress.set(int(100 * glyphIndex / max(len(glyphsToCheck), 1)))
			# Union composites across all masters so incompatible glyphs are fully covered
			compositesByNorm = {}  # normalized name → actual name (first seen)
			for master in thisFont.masters:
				composites = thisFont.glyphsContainingComponentWithName_masterId_(thisGlyph.name, master.id)
				if composites:
					for g in composites:
						normName = normalizedSuffixOrder(g.name) if not suffixOrderMatters else g.name
						if normName not in compositesByNorm:
							compositesByNorm[normName] = g.name

			if not compositesByNorm:
				continue

			for otherName in allNames:
				if not otherName.startswith(thisGlyph.name + "."):
					continue
				otherSuffix = otherName[len(thisGlyph.name) + 1:]
				if any(s in otherSuffix.split(".") for s in ignoredSuffixes):
					continue

				missingItems = []
				for normCompName, actualCompName in compositesByNorm.items():
					missingCompName = "%s.%s" % (normCompName.rstrip("."), otherSuffix.strip("."))
					if not suffixOrderMatters:
						missingCompName = normalizedSuffixOrder(missingCompName)
					if missingCompName not in allNamesSet:
						if not ignoreDuplicateSuffixes or len(missingCompName.split(".")[1:]) == len(set(missingCompName.split(".")[1:])):
							missingItems.append((actualCompName, missingCompName, otherSuffix))

				if missingItems:
					results.append((otherName, missingItems))

		return results

	def updateIgnoreSuffixes(self, sender=None):
		thisFont = Glyphs.font
		if not thisFont:
			self.w.ignore.set(defaultSuffixes)
			self.SavePreferences()
			return
		existing = set(s.strip().strip(".") for s in self.pref("ignore").split(",") if s.strip())
		for glyph in thisFont.glyphs:
			parts = glyph.name.split(".")
			for suffix in parts[1:]:
				if suffix:
					existing.add(suffix)
		self.w.ignore.set(", ".join(".%s" % s for s in sorted(existing)))
		self.SavePreferences()

	def CompositeConsistencerMain(self, sender=None):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			ignoredSuffixes = [s.strip().strip(".") for s in self.pref("ignore").split(",")]
			ignoreDuplicateSuffixes = self.prefBool("ignoreDuplicateSuffixes")
			suffixOrderMatters = self.prefBool("suffixOrderMatters")
			includeNonExporting = self.prefBool("includeNonExporting")
			selectedOnly = self.prefBool("selectedOnly")

			fonts = Glyphs.fonts if self.prefBool("allFonts") else [Glyphs.font]
			fonts = [f for f in fonts if f is not None]
			if not fonts:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			self.prepareReport()
			print("Composite Consistencer Report\n")
			self.w.status.set("")
			self.w.progress.set(0)

			totalAffected = 0
			missingNames = []  # all missing glyph names, each once, in order
			for thisFont in fonts:
				print(f"📄 {self.fileLabel(thisFont)}")
				missingData = self.collectMissingData(thisFont, ignoredSuffixes, ignoreDuplicateSuffixes, suffixOrderMatters, includeNonExporting, selectedOnly)
				if not missingData:
					print("\t✅ No missing composites.")
				for otherName, missingItems in missingData:
					totalAffected += 1
					names = [m[1] for m in missingItems]
					for name in names:
						if name not in missingNames:
							missingNames.append(name)
					print(f"\t⚠️ {otherName} is missing {len(names)}: {', '.join(names)}")
				print()

			self.w.progress.set(100)
			summary = f"{totalAffected} glyph{'' if totalAffected == 1 else 's'} missing {len(missingNames)} composite{'' if len(missingNames) == 1 else 's'}"
			self.w.status.set(summary)
			print(f"{'⚠️' if missingNames else '✅'} {summary}.")
			if missingNames:
				if not suffixOrderMatters:
					print("The displayed suffix order may not be intended.")
				print("\nFor Glyph > Add Glyphs…:")
				print(" ".join(missingNames))

			Glyphs.showNotification("Composite Consistencer", f"{summary}. Details in Macro Window.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Composite Consistencer Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	def CompositeConsistencerCreate(self, sender=None):
		try:
			self.SavePreferences()

			ignore = self.pref("ignore")
			ignoredSuffixes = [s.strip().strip(".") for s in ignore.split(",")]
			ignoreDuplicateSuffixes = self.prefBool("ignoreDuplicateSuffixes")
			suffixOrderMatters = self.prefBool("suffixOrderMatters")
			includeNonExporting = self.prefBool("includeNonExporting")
			selectedOnly = self.prefBool("selectedOnly")

			fonts = Glyphs.fonts if self.prefBool("allFonts") else [Glyphs.font]
			fonts = [f for f in fonts if f is not None]
			if not fonts:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			self.prepareReport()
			print("Composite Consistencer: Create Report\n")
			self.w.status.set("")
			self.w.progress.set(0)
			totalCreated = 0

			for thisFont in fonts:
				print(f"📄 {self.fileLabel(thisFont)}")

				missingData = self.collectMissingData(thisFont, ignoredSuffixes, ignoreDuplicateSuffixes, suffixOrderMatters, includeNonExporting, selectedOnly)
				createdNames = []
				seen = set()  # avoid creating the same glyph twice if it appears under multiple base glyphs

				for otherName, missingItems in missingData:
					for sourceCompositeName, missingCompName, suffix in missingItems:
						if missingCompName in seen or thisFont.glyphs[missingCompName]:
							continue
						seen.add(missingCompName)

						sourceGlyph = thisFont.glyphs[sourceCompositeName]
						if not sourceGlyph:
							print("\t⚠️ Source glyph '%s' not found, skipping %s" % (sourceCompositeName, missingCompName))
							continue

						newGlyph = GSGlyph()
						newGlyph.name = missingCompName
						thisFont.glyphs.append(newGlyph)

						for sourceLayer in sourceGlyph.layers:
							if not sourceLayer.isMasterLayer:
								continue
							targetLayer = newGlyph.layers[sourceLayer.associatedMasterId]
							if targetLayer is None:
								continue
							for sourceComp in sourceLayer.components:
								suffixedName = "%s.%s" % (sourceComp.name, suffix)
								newCompName = suffixedName if thisFont.glyphs[suffixedName] else sourceComp.name
								newComp = GSComponent(newCompName)
								newComp.position = sourceComp.position
								newComp.automaticAlignment = sourceComp.automaticAlignment
								targetLayer.shapes.append(newComp)

						print("\t✅ %s (based on %s)" % (missingCompName, sourceCompositeName))
						totalCreated += 1
						createdNames.append(missingCompName)

				# always open a new tab with the newly created glyphs:
				if createdNames:
					thisFont.newTab("".join("/%s" % name for name in createdNames))
				print()

			self.w.progress.set(100)
			self.w.status.set("Created %i composite%s" % (totalCreated, "" if totalCreated == 1 else "s"))
			print("✅ Created %i composite%s." % (totalCreated, "" if totalCreated == 1 else "s"))
			Glyphs.showNotification(
				"Composite Consistencer",
				"Created %i composite%s. Details in Macro Window." % (totalCreated, "" if totalCreated == 1 else "s"),
			)

		except Exception as e:
			Glyphs.showMacroWindow()
			print("Composite Consistencer Create Error: %s" % e)
			import traceback
			print(traceback.format_exc())


CompositeConsistencer()
