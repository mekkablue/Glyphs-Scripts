# MenuTitle: Find in Features
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds expressions (glyph, lookup or class names) in OT Features, Prefixes and Classes.
"""

import vanilla
from fnmatch import fnmatchcase
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, UpdateButton, getLegibleFont


class FindInFeatures(mekkaObject):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 180
		windowHeight = 200
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 1100  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Find in Features",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 3, 5, 28
		self.w.searchFor = vanilla.ComboBox((4, linePos, -22, 22), self.glyphNamesAndClassNames(), callback=self.FindInFeaturesMain)
		self.w.searchFor.setToolTip("Type the name of a glyph or (prefixed with @) a class, or choose it from the menu. Supports wildcards: * matches any sequence of characters, ? matches any single character.")
		self.w.updateButton = UpdateButton((-19, linePos, -2, 18), callback=self.update)
		self.w.updateButton.setToolTip("Update the autocompletion list for the frontmost font.")
		linePos += lineHeight

		self.w.result = vanilla.TextEditor((inset, linePos, -inset, -inset), "")
		self.w.result.getNSTextView().setEditable_(False)
		self.w.result.getNSTextView().setFont_(getLegibleFont())
		self.w.result.getNSTextView().setToolTip_("Search results: OT classes, prefixes, and features that contain the searched name.")
		linePos += lineHeight

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

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
			classReportText = "OT Classes:\n"
			classes = []
			for c in thisFont.classes:
				if any(fnmatchcase(word, searchfor) for word in self.codeClean(c.code).split()):
					classes.append(c.name)

			if not classes:
				classReportText += "(nothing found)\n"
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
				(thisFont.featurePrefixes, "\nOT Prefixes:\n"),
				(thisFont.features, "\nOT Features:\n"),
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
					prefixFeatureReportText += "(nothing found)\n"

			# Assemble report:
			reportText = ""
			if isWildcard and glyphFeatures:
				reportText += "GLYPH OVERVIEW\n"
				for glyphName in sorted(glyphFeatures.keys()):
					reportText += "%s: %s\n" % (glyphName, ", ".join(glyphFeatures[glyphName]))
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
