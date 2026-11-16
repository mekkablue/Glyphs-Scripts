# MenuTitle: Find in Features
__doc__ = """
Finds expressions (glyph, lookup or class names) in OT Features, Prefixes and Classes.
"""

from fnmatch import fnmatchcase
import vanilla
from AppKit import NSFont, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultLow, NSFontFeatureSettingsAttribute, NSFontFeatureTypeIdentifierKey, NSFontFeatureSelectorIdentifierKey
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, UpdateButton, getLegibleFont


class FindInFeatures(mekkaObject):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 180
		windowHeight = 200
		# the result list is the main content, so the window stays resizable (hence minSize):
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Find in Features",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		self.w.searchFor = vanilla.ComboBox("auto", self.glyphNamesAndClassNames(), callback=self.FindInFeaturesMain)
		self.w.searchFor.setToolTip("Type the name of a glyph or (prefixed with @) a class, or choose it from the menu. Supports wildcards: * matches any sequence of characters, ? matches any single character.")
		self.w.updateButton = UpdateButton("auto", callback=self.update)
		self.w.updateButton.setToolTip("Update the autocompletion list for the frontmost font.")

		self.w.result = vanilla.TextEditor("auto", "")
		self.w.result.getNSTextView().setEditable_(False)
		self.w.result.getNSTextView().setFont_(self.legibleTabularFont())
		self.w.result.getNSTextView().setToolTip_("Search results: OT classes, prefixes, and features that contain the searched name.")

		# the result takes all the height the user gives the window:
		self.w.result.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[searchFor(>=100)]-gap-[updateButton]-inset-|",
				"H:|-inset-[result]-inset-|",
				"V:|-inset-[searchFor]-gap-[result(>=100)]-inset-|",
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.searchFor, "attribute2": "centerY"},
			],
			metrics={"inset": 5, "gap": 5},
		)

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def legibleTabularFont(self):
		font = getLegibleFont()
		try:
			descriptor = font.fontDescriptor().fontDescriptorByAddingAttributes_({
				NSFontFeatureSettingsAttribute: [{
					NSFontFeatureTypeIdentifierKey: 6,   # Number Spacing
					NSFontFeatureSelectorIdentifierKey: 0,  # Monospaced numbers
				}]
			})
			font = NSFont.fontWithDescriptor_size_(descriptor, font.pointSize()) or font
		except Exception:
			pass
		return font

	def update(self, sender=None):
		self.w.searchFor.setItems(self.glyphNamesAndClassNames())

	def glyphNamesAndClassNames(self, sender=None):
		fullList = []
		font = Glyphs.font
		if font:
			# add all exporting glyphs:
			fullList.extend([g.name for g in font.glyphs if g.export])

			# add all OT class names:
			fullList.extend(["@%s" % c.name for c in font.classes])

			# sort it:
			fullList = sorted(fullList)

		return fullList

	def codeClean(self, code):
		# get rid of comments:
		lines = code.splitlines()
		for i, line in enumerate(lines):
			if "#" in line:
				lines[i] = line[:line.find("#")]
		code = "\n".join(lines)

		# get rid of control chars:
		removeThese = "[];{}()'"
		for removeThis in removeThese:
			code = code.replace(removeThis, " ").replace("  ", " ")
		return code

	def FindInFeaturesMain(self, sender=None):
		try:
			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				return

			searchfor = sender.get()
			isWildcard = '*' in searchfor or '?' in searchfor

			# Find in Classes:
			classReportText = "OT CLASSES\n"
			classes = []
			for c in thisFont.classes:
				if any(fnmatchcase(word, searchfor) for word in self.codeClean(c.code).split()):
					classes.append(c.name)

			if not classes:
				classReportText += "\t(nothing found)\n"
				classSet = None
			else:
				classSet = set(classes)
				for className in classSet:
					classReportText += "\t%s" % className
					if classes.count(className) > 1:
						classReportText += " (%i×)" % classes.count(className)
					classReportText += "\n"

			# Find in Prefixes and Features:
			prefixAndFeatures = (
				(thisFont.featurePrefixes, "\nOT PREFIXES\n"),
				(thisFont.features, "\nOT FEATURES\n"),
			)

			glyphFeatures = {}  # {glyphName: [featureTag, ...]} — for the overview
			prefixFeatureReportText = ""
			foundInFeaturesCount = 0
			for featureSet in prefixAndFeatures:
				originalFeatureCount = foundInFeaturesCount
				prefixFeatureReportText += featureSet[1]
				for feature in featureSet[0]:
					if feature.active:
						cleanCode = self.codeClean(feature.code)
						for i, l in enumerate(cleanCode.splitlines()):
							split = l.split()
							matchedWords = list(dict.fromkeys(w for w in split if fnmatchcase(w, searchfor)))
							if matchedWords:
								prefixFeatureReportText += "\t%s, line %i (%s)\n" % (feature.name, i + 1, ", ".join(matchedWords))
								foundInFeaturesCount += 1
								if isWildcard:
									for w in matchedWords:
										if w not in glyphFeatures:
											glyphFeatures[w] = []
										if feature.name not in glyphFeatures[w]:
											glyphFeatures[w].append(feature.name)

							# also find the classes the term appears in:
							if classSet:
								for otclass in classSet:
									if "@%s" % otclass in split:
										prefixFeatureReportText += "\t%s, line %i (@%s)\n" % (feature.name, i + 1, otclass)
										foundInFeaturesCount += 1

				if foundInFeaturesCount == originalFeatureCount:
					prefixFeatureReportText += "\t(nothing found)\n"

			# Assemble report:
			reportText = ""
			if isWildcard and glyphFeatures:
				reportText += "GLYPH OVERVIEW\n"
				for glyphName in sorted(glyphFeatures.keys()):
					reportText += "\t%s: %s\n" % (glyphName, ", ".join(glyphFeatures[glyphName]))
				reportText += "\n"
			reportText += classReportText
			reportText += prefixFeatureReportText

			self.w.result.set(reportText)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Find in Features Error: %s" % e)
			import traceback
			print(traceback.format_exc())


FindInFeatures()
