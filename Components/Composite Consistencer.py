# MenuTitle: Composite Consistencer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Goes through all glyphs of the frontmost font, and checks for composites in the current master. If dot-suffixed glyph variants are missing them, they are reported in the Macro Window.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject

defaultSuffixes = ".dnom, .numr, .subs, .sups, .sinf, .case, .tf, .tosf, .osf"

presetItems = [
	"(Load preset…)",
	"Default (common): dnom, numr, subs, sups, sinf, case, tf, tosf, osf",
	"Numerals: dnom, numr, subs, sups, sinf, tf, tosf, osf",
	"Small caps: sc, c2sc",
	"Case: case",
	"None — check all suffixes",
]

presetValues = {
	"Default (common): dnom, numr, subs, sups, sinf, case, tf, tosf, osf": ".dnom, .numr, .subs, .sups, .sinf, .case, .tf, .tosf, .osf",
	"Numerals: dnom, numr, subs, sups, sinf, tf, tosf, osf": ".dnom, .numr, .subs, .sups, .sinf, .tf, .tosf, .osf",
	"Small caps: sc, c2sc": ".sc, .c2sc",
	"Case: case": ".case",
	"None — check all suffixes": "",
}


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
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 208
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

		self.w.presetsText = vanilla.TextBox((inset, linePos + 3, 90, 14), "Load preset:", sizeStyle='small', selectable=True)
		self.w.presets = vanilla.PopUpButton((inset + 90, linePos, -inset, 18), presetItems, callback=self.loadPreset, sizeStyle='small')
		self.w.presets.setToolTip("Load a preset set of ignored suffixes into the field below. You can edit it afterwards.")
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

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Find", callback=self.CompositeConsistencerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def loadPreset(self, sender=None):
		selectedItem = presetItems[self.w.presets.get()]
		if selectedItem in presetValues:
			self.w.ignore.set(presetValues[selectedItem])
			self.SavePreferences()
		self.w.presets.set(0)

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

			fonts = Glyphs.fonts if self.prefBool("allFonts") else [Glyphs.font]
			fonts = [f for f in fonts if f is not None]
			if not fonts:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				totalAffected = 0
				totalMissing = 0

				for thisFont in fonts:
					print("Composite Consistencer Report for %s" % thisFont.familyName)
					if thisFont.filepath:
						print(thisFont.filepath)
					else:
						print("⚠️ The font file has not been saved yet.")
					print()

					allNames = [g.name for g in thisFont.glyphs] if includeNonExporting else [g.name for g in thisFont.glyphs if g.export]
					if not suffixOrderMatters:
						allNames = [normalizedSuffixOrder(n) for n in allNames]

					countAffectedGlyphs = 0
					countMissingComposites = 0
					for thisGlyph in thisFont.glyphs:
						thisGlyphAffected = False
						# Union composites across all masters so incompatible glyphs are fully covered
						compositeNameSet = set()
						for master in thisFont.masters:
							composites = thisFont.glyphsContainingComponentWithName_masterId_(thisGlyph.name, master.id)
							if composites:
								for g in composites:
									compositeNameSet.add(g.name)
						if compositeNameSet:
							compositeNames = list(compositeNameSet)
							if not suffixOrderMatters:
								compositeNames = [normalizedSuffixOrder(n) for n in compositeNames]
							for otherName in allNames:
								if otherName.startswith(thisGlyph.name + "."):
									otherSuffix = otherName[len(thisGlyph.name) + 1:]
									if all([s not in otherSuffix.split(".") for s in ignoredSuffixes]):
										missingOtherNames = []
										for thisCompositeName in compositeNames:
											otherCompositeName = "%s.%s" % (thisCompositeName.rstrip("."), otherSuffix.strip("."))
											if not suffixOrderMatters:
												otherCompositeName = normalizedSuffixOrder(otherCompositeName)
											if otherCompositeName not in allNames:
												if not ignoreDuplicateSuffixes or len(otherCompositeName.split(".")[1:]) == len(set(otherCompositeName.split(".")[1:])):
													missingOtherNames.append(otherCompositeName)
										if missingOtherNames:
											countMissingComposites += len(missingOtherNames)
											if not thisGlyphAffected:
												countAffectedGlyphs += 1
												thisGlyphAffected = True
											print(
												"%s is missing %i composite%s:\n%s\n" % (
													otherName,
													len(missingOtherNames),
													"" if len(missingOtherNames) == 1 else "s",
													", ".join(missingOtherNames),
												)
											)

					totalAffected += countAffectedGlyphs
					totalMissing += countMissingComposites
					if not suffixOrderMatters and countMissingComposites > 0:
						print("\n⚠️ Attention: the displayed suffix order may not be intended.")
					print("Done.\n")

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


CompositeConsistencer()
