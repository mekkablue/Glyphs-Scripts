# MenuTitle: Tabular Checker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Goes through tabular glyphs and checks if they are monospaced. Reports exceptions.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkaCore import mekkaObject


class TabularChecker(mekkaObject):
	prefDict = {
		"suffixesEntry": "tf, tosf",
		"allowDifferingWidthsPerSuffix": 0,
		"includeNonExporting": 0,
		"allFonts": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 440
		windowHeight = 160
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Tabular Checker",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), u"Goes through all glyphs with specified suffixes, and compares their widths:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.suffixesText = vanilla.TextBox((inset, linePos + 2, 95, 14), u"Tabular suffixes:", sizeStyle='small', selectable=True)
		self.w.suffixesEntry = vanilla.EditText((inset + 95, linePos - 1, -inset, 19), "tf, tosf", callback=self.SavePreferences, sizeStyle='small')
		self.w.suffixesEntry.getNSTextField().setToolTip_(u"Comma-separated list of suffixes, with or without dots. Usually, you want ‘.tf, .tosf’.")
		linePos += lineHeight

		self.w.allowDifferingWidthsPerSuffix = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Allow different widths in different suffixes", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allowDifferingWidthsPerSuffix.getNSButton().setToolTip_(u"If checked, e.g., .tf and .tosf can have different widths in the same master. Otherwise .tf and .tosf must be same width.")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Also include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_(u"If not set, non-exporting glyphs will be ignored.")
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Search in ⚠️ ALL fonts", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.status = vanilla.TextBox((inset, linePos + 2, -inset, 14), u"", sizeStyle='small', selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Report", sizeStyle='regular', callback=self.TabularCheckerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Tabular Checker' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def reportStatus(self, reportString):
		if not reportString:
			reportString = u""
		self.w.status.set(reportString)

	def widthReport(self, numOfDifferentWidths, suffix, suffixes, m, lengths, glyphnames, allowDifferingWidthsPerSuffix):
		if numOfDifferentWidths > 1:
			# bring macro window to front:
			Glyphs.showMacroWindow()

			# report
			print()
			print(u"❌ Found %i differing widths for '%s' in master %s:" % (numOfDifferentWidths, suffix, m.name))
			for length, gname in zip(lengths, glyphnames):
				print("   %.1f: %s" % (length, gname))
			print()

		elif numOfDifferentWidths == 1:
			print(u"✅ OK: %.1f in all %s of %s" % (
				lengths[0],
				suffix if allowDifferingWidthsPerSuffix else " & ".join(suffixes),
				m.name,
			))

		else:
			print(u"⚠️ Not found in font: %s" % (suffix if allowDifferingWidthsPerSuffix else " & ".join(suffixes)))

	def TabularCheckerMain(self, sender):
		try:
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			Glyphs.showMacroWindow()

			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print(u"Note: 'Tabular Checker' could not write preferences.")

			# query user input:
			suffixString = self.pref("suffixesEntry")
			suffixes = [".%s" % s.strip().lstrip(".") for s in suffixString.split(",")]
			includeNonExporting = self.pref("includeNonExporting")
			allowDifferingWidthsPerSuffix = self.pref("allowDifferingWidthsPerSuffix")

			if self.pref("allFonts"):
				fonts = Glyphs.fonts
			else:
				fonts = (Glyphs.font, )

			for Font in fonts:
				print(u"Tabular Checker Report for %s" % Font.familyName)
				print(Font.filepath)
				print()
				for m in Font.masters:
					lengths = []
					glyphnames = []

					# iterate through suffixes:
					for suffix in suffixes:
						if allowDifferingWidthsPerSuffix:
							lengths = []
							glyphnames = []

						# update status:
						reportString = u"Testing '%s' in %s..." % (suffix, m.name)
						self.reportStatus(reportString)

						for g in Font.glyphs:
							if suffix in g.name and (g.export or includeNonExporting):
								layer = g.layers[m.id]
								lengths.append(layer.width)
								glyphnames.append(g.name)

						numOfDifferentWidths = len(set(lengths))
						if allowDifferingWidthsPerSuffix:
							self.widthReport(numOfDifferentWidths, suffix, suffixes, m, lengths, glyphnames, allowDifferingWidthsPerSuffix)

					if not allowDifferingWidthsPerSuffix:
						self.widthReport(numOfDifferentWidths, suffix, suffixes, m, lengths, glyphnames, allowDifferingWidthsPerSuffix)

			reportString = "Done."
			self.reportStatus(reportString)
			print(reportString)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Tabular Checker Error: %s" % e)
			import traceback
			print(traceback.format_exc())


TabularChecker()
