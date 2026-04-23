# MenuTitle: Composite Consistencer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Goes through all glyphs of the frontmost font (or all open fonts), and checks for composites. If dot-suffixed glyph variants are missing them, they are reported in the Macro Window and can optionally be created automatically.
"""

import vanilla
from GlyphsApp import Glyphs, Message, GSGlyph, GSComponent
from mekkablue import mekkaObject

defaultSuffixes = ".dnom, .numr, .subs, .sups, .sinf, .case, .tf, .tosf, .osf"


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
		windowWidth = 320
		windowHeight = 242
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Composite Consistencer",  # window title
			minSize=(windowWidth, windowHeight + 19),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize + 19),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Find missing suffixed composites:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.ignoreText = vanilla.TextBox((inset, linePos + 3, 90, 14), "Ignore suffixes:", sizeStyle='small', selectable=True)
		self.w.ignore = vanilla.EditText((inset + 90, linePos, -inset, 19), defaultSuffixes, callback=self.SavePreferences, sizeStyle='small')
		self.w.ignore.setToolTip("Comma-separated suffixes to skip when reporting missing composites.")
		linePos += lineHeight

		self.w.ignoreDuplicateSuffixes = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Ignore duplicate suffixes (.ss01.ss01)", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.suffixOrderMatters = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Order of suffixes matters (.case.ss01 and .ss01.case)", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Check all open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allFonts.setToolTip("When checked, all open fonts are scanned instead of just the frontmost one.")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.setToolTip("When checked, glyphs with export disabled are also checked for missing composite counterparts.")
		linePos += lineHeight

		self.w.selectedOnly = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Check selected glyphs only", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.selectedOnly.setToolTip("When checked, only glyphs currently selected in the Font tab are treated as potential bases.")
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos + 4, -inset, 16))
		self.w.progress.set(0)
		linePos += lineHeight

		self.w.status = vanilla.TextBox((inset, -20 - inset, -186, -inset), "", sizeStyle='small')

		# Buttons:
		self.w.createButton = vanilla.Button((-178, -20 - inset, -95, -inset), "Create", callback=self.CompositeConsistencerCreate, sizeStyle='small')
		self.w.createButton.setToolTip("Create all missing composite glyphs found by the current settings.")
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Find", callback=self.CompositeConsistencerMain, sizeStyle='small')
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

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

	def CompositeConsistencerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
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
			else:
				totalAffected = 0
				totalMissing = 0
				self.w.status.set("")
				self.w.progress.set(0)

				for thisFont in fonts:
					print("Composite Consistencer Report for %s" % thisFont.familyName)
					if thisFont.filepath:
						print(thisFont.filepath)
					else:
						print("⚠️ The font file has not been saved yet.")
					print()

					missingData = self.collectMissingData(thisFont, ignoredSuffixes, ignoreDuplicateSuffixes, suffixOrderMatters, includeNonExporting, selectedOnly)

					countAffectedGlyphs = 0
					countMissingComposites = 0
					for otherName, missingItems in missingData:
						countAffectedGlyphs += 1
						missingNames = [m[1] for m in missingItems]
						countMissingComposites += len(missingNames)
						print(
							"%s is missing %i composite%s:\n%s\n" % (
								otherName,
								len(missingNames),
								"" if len(missingNames) == 1 else "s",
								", ".join(missingNames),
							)
						)

					totalAffected += countAffectedGlyphs
					totalMissing += countMissingComposites
					if not suffixOrderMatters and countMissingComposites > 0:
						print("\n⚠️ Attention: the displayed suffix order may not be intended.")
					print("Done.\n")

				self.w.progress.set(100)
				self.w.status.set(
					"%i glyph%s missing %i composite%s" % (
						totalAffected,
						"" if totalAffected == 1 else "s",
						totalMissing,
						"" if totalMissing == 1 else "s",
					)
				)

				fontLabel = fonts[0].familyName if len(fonts) == 1 else "%i fonts" % len(fonts)
				Glyphs.showNotification(
					"%s: %i glyph%s missing composites" % (
						fontLabel,
						totalAffected,
						"" if totalAffected == 1 else "s",
					),
					"%i glyph%s missing %i composite%s. Details in Macro Window." % (
						totalAffected,
						"" if totalAffected == 1 else "s",
						totalMissing,
						"" if totalMissing == 1 else "s",
					),
				)

				# brings macro window to front:
				Glyphs.showMacroWindow()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Composite Consistencer Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	def CompositeConsistencerCreate(self, sender=None):
		try:
			Glyphs.clearLog()
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

			self.w.status.set("")
			self.w.progress.set(0)
			totalCreated = 0

			for thisFont in fonts:
				print("Composite Consistencer: Creating composites in %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				missingData = self.collectMissingData(thisFont, ignoredSuffixes, ignoreDuplicateSuffixes, suffixOrderMatters, includeNonExporting, selectedOnly)
				seen = set()  # avoid creating the same glyph twice if it appears under multiple base glyphs

				for otherName, missingItems in missingData:
					for sourceCompositeName, missingCompName, suffix in missingItems:
						if missingCompName in seen or thisFont.glyphs[missingCompName]:
							continue
						seen.add(missingCompName)

						sourceGlyph = thisFont.glyphs[sourceCompositeName]
						if not sourceGlyph:
							print("⚠️ Source glyph '%s' not found, skipping %s" % (sourceCompositeName, missingCompName))
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
								targetLayer.components.append(newComp)

						print("✅ Created %s (based on %s)" % (missingCompName, sourceCompositeName))
						totalCreated += 1

			self.w.progress.set(100)
			self.w.status.set("Created %i composite%s" % (totalCreated, "" if totalCreated == 1 else "s"))
			Glyphs.showNotification(
				"Composite Consistencer",
				"Created %i composite%s. Details in Macro Window." % (totalCreated, "" if totalCreated == 1 else "s"),
			)
			Glyphs.showMacroWindow()

		except Exception as e:
			Glyphs.showMacroWindow()
			print("Composite Consistencer Create Error: %s" % e)
			import traceback
			print(traceback.format_exc())


CompositeConsistencer()
