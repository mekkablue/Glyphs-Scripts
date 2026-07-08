# MenuTitle: Contextual Cycler
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Builds contextual alternate (calt) feature code that cycles through numbered glyph alternates, so that repeated glyphs step through their variants (default → .cv01 → .cv02 → … → default). Glyphs are grouped by how many alternates they have: @One0/@One1 for glyphs with one alternate, @Two0/@Two1/@Two2 for two, and so on; everything else lands in @Etc. See https://glyphsapp.com/learn/features-part-3-advanced-contextual-alternates
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton, createOTFeature, createOTClass, reportFontName

# Spelled-out numbers used to name the cycle classes (@One0, @Two1, …):
numberWords = (
	"Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
	"Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty",
)


def numberWord(number):
	"""Returns a spelled-out class-name prefix for a given alternate count."""
	if 0 <= number < len(numberWords):
		return numberWords[number]
	return "Alt%i" % number


class ContextualCycler(mekkaObject):
	codeSig = "CONTEXTUAL CYCLER"
	etcClassName = "Etc"

	prefDict = {
		"targetFeature": "calt",
		"suffixes": ".cv, .ss",
		"separateFeatureEntry": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 360
		windowHeight = 175
		windowWidthResize = 400  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Contextual Cycler",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow"),  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight, tabIndent = 12, 15, 22, 130

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 28), "Build cycling contextual alternates: repeated glyphs step through their numbered alternates.", sizeStyle="small", selectable=True)
		linePos += lineHeight + 12

		self.w.suffixesText = vanilla.TextBox((inset, linePos + 3, tabIndent, 14), "Numbered suffixes:", sizeStyle="small", selectable=True)
		self.w.suffixes = vanilla.EditText((inset + tabIndent, linePos, -inset - 22, 19), ".cv, .ss", callback=self.SavePreferences, sizeStyle="small")
		tooltip = "Comma-separated list of numbered suffix stems that mark the alternates, e.g. ‘.cv, .ss’ matches s.cv01, s.cv02, s.ss01, … The trailing number determines the cycle order."
		self.w.suffixes.setToolTip(tooltip)
		self.w.suffixesText.setToolTip(tooltip)
		self.w.suffixesUpdate = UpdateButton((-inset - 18, linePos - 1, -inset, 18), callback=self.update)
		self.w.suffixesUpdate.setToolTip("Reset to defaults: ‘.cv, .ss’")
		linePos += lineHeight

		self.w.targetFeatureText = vanilla.TextBox((inset, linePos + 3, tabIndent, 14), "Target feature (tag):", sizeStyle="small", selectable=True)
		self.w.targetFeature = vanilla.EditText((inset + tabIndent, linePos, -inset - 22, 19), "calt", callback=self.SavePreferences, sizeStyle="small")
		tooltip = "Feature tag for the OpenType feature that receives the cycling code. Contextual alternates (calt) are on by default in most apps."
		self.w.targetFeature.setToolTip(tooltip)
		self.w.targetFeatureText.setToolTip(tooltip)
		self.w.targetFeatureUpdate = UpdateButton((-inset - 18, linePos - 1, -inset, 18), callback=self.update)
		self.w.targetFeatureUpdate.setToolTip("Reset to defaults: ‘calt’")
		linePos += lineHeight

		self.w.separateFeatureEntry = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "Separate feature entry (i.e. do not reuse existing feature)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.separateFeatureEntry.setToolTip("If enabled and the target feature already exists in Font Info → Features, creates a new entry with the same tag rather than appending the code to an existing feature entry.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Build", callback=self.ContextualCyclerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		if sender == self.w.targetFeatureUpdate:
			self.setPref("targetFeature", "calt")
		elif sender == self.w.suffixesUpdate:
			self.setPref("suffixes", ".cv, .ss")
		self.LoadPreferences()

	def suffixStems(self):
		"""Returns a list of normalized suffix stems (each starting with a dot)."""
		stems = []
		for stem in self.pref("suffixes").split(","):
			stem = stem.strip()
			if not stem:
				continue
			if not stem.startswith("."):
				stem = "." + stem
			# store without trailing digits, in case the user typed ‘.cv01’:
			stem = stem.rstrip("0123456789")
			if stem and stem != "." and stem not in stems:
				stems.append(stem)
		return stems

	def cycleSequences(self, thisFont, stems):
		"""
		Scans the font for base glyphs and their numbered alternates.
		Returns (groups, usedNames):
		- groups: dict mapping alternate-count → list of cycle sequences,
		  each sequence being [baseName, alt1Name, alt2Name, …] in cycle order.
		- usedNames: set of every glyph name that ended up in a cycle.
		"""
		# collect alternates per base glyph: baseName → list of (sortKey, altName)
		alternatesForBase = {}
		for glyph in thisFont.glyphs:
			if not glyph.export:
				continue
			name = glyph.name
			for stemIndex, stem in enumerate(stems):
				if stem not in name:
					continue
				baseName, _, numberPart = name.rpartition(stem)
				if not baseName or not numberPart.isdigit():
					continue
				baseGlyph = thisFont.glyphs[baseName]
				if baseGlyph is None or not baseGlyph.export:
					continue
				sortKey = (stemIndex, int(numberPart))
				alternatesForBase.setdefault(baseName, []).append((sortKey, name))
				break  # a glyph name matches at most one stem

		groups = {}
		usedNames = set()
		for baseName, alternates in alternatesForBase.items():
			# sort by (stem order, number) and drop duplicate names:
			orderedAltNames = []
			for _, altName in sorted(alternates):
				if altName not in orderedAltNames:
					orderedAltNames.append(altName)
			sequence = [baseName] + orderedAltNames
			count = len(orderedAltNames)
			groups.setdefault(count, []).append(sequence)
			usedNames.update(sequence)

		# keep the base-glyph order stable and predictable within each group:
		for count in groups:
			groups[count].sort(key=lambda sequence: sequence[0])

		return groups, usedNames

	def buildClasses(self, thisFont, groups, usedNames):
		"""Creates/updates the @<Word><position> classes and the @Etc leftover class."""
		classCount = 0
		for count in sorted(groups):
			word = numberWord(count)
			sequences = groups[count]
			# every position 0…count gets its own class; index i stays parallel across positions:
			for position in range(count + 1):
				className = "%s%i" % (word, position)
				glyphNames = [sequence[position] for sequence in sequences]
				print("\t%s" % createOTClass(className=className, classGlyphNames=glyphNames, targetFont=thisFont))
				classCount += 1

		# everything that is not part of a cycle goes into @Etc:
		etcNames = [glyph.name for glyph in thisFont.glyphs if glyph.export and glyph.name not in usedNames]
		if etcNames:
			print("\t%s" % createOTClass(className=self.etcClassName, classGlyphNames=etcNames, targetFont=thisFont))
			classCount += 1

		return classCount

	def buildFeatureCode(self, groups):
		"""
		Assembles the cycling feature code. For each group with positions 0…k, the
		current glyph (always written as the default @<Word>0) is advanced to the next
		alternate based on the preceding glyph’s position, wrapping back to the default:
			sub @Word0 @Word0' by @Word1;
			sub @Word1 @Word0' by @Word2;
			…
		"""
		featureCode = ""
		for count in sorted(groups):
			word = numberWord(count)
			featureCode += "lookup %sCycle {\n" % word
			for position in range(count):
				featureCode += "\tsub @%s%i @%s0' by @%s%i;\n" % (word, position, word, word, position + 1)
			featureCode += "} %sCycle;\n\n" % word
		return featureCode.strip()

	def ContextualCyclerMain(self, sender=None):
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
					OKButton=None,
				)
				return

			print("Contextual Cycler Report for %s\n" % reportFontName(thisFont))

			# read and sanitize user settings:
			targetFeature = self.pref("targetFeature").strip()
			if not targetFeature or len(targetFeature) > 4:
				print("⚠️ Invalid target feature tag ‘%s’. Falling back to ‘calt’." % targetFeature)
				targetFeature = "calt"
				self.setPref("targetFeature", targetFeature)
				self.LoadPreferences()

			stems = self.suffixStems()
			if not stems:
				print("⚠️ No valid numbered suffixes given. Falling back to ‘.cv, .ss’.")
				stems = [".cv", ".ss"]
				self.setPref("suffixes", ".cv, .ss")
				self.LoadPreferences()
			print("Looking for alternates with suffixes: %s\n" % ", ".join(stems))

			# collect base glyphs and their alternates:
			groups, usedNames = self.cycleSequences(thisFont, stems)
			if not groups:
				Message(
					title="Nothing to Cycle",
					message="Could not find any glyphs with numbered alternates for the suffixes: %s. Check your suffixes and try again." % ", ".join(stems),
					OKButton=None,
				)
				print("❌ No base glyphs with numbered alternates found.")
				return

			for count in sorted(groups):
				print("🔠 %s: %i glyph%s with %i alternate%s." % (
					numberWord(count),
					len(groups[count]),
					"" if len(groups[count]) == 1 else "s",
					count,
					"" if count == 1 else "s",
				))
			print()

			# build classes:
			classCount = self.buildClasses(thisFont, groups, usedNames)

			# build cycling feature code:
			featureCode = self.buildFeatureCode(groups)
			print()
			print("\t%s" % createOTFeature(
				featureName=targetFeature,
				featureCode=featureCode,
				targetFont=thisFont,
				codeSig=self.codeSig,
				createSeparateEntry=self.prefBool("separateFeatureEntry"),
			))

			# recompile so the changes take effect:
			thisFont.compileFeatures()
			self.w.close()

			Glyphs.showNotification(
				"Contextual Cycler: %s" % thisFont.familyName,
				"Built cycling code in ‘%s’, %i classes added or updated. Details in Macro Window." % (targetFeature, classCount),
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Contextual Cycler Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ContextualCycler()
