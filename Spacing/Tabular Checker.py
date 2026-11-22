# MenuTitle: Tabular Checker
__doc__ = """
Goes through tabular glyphs and checks if they are monospaced. Reports exceptions.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, fontFileName, makeWindowResizable


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
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Tabular Checker",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Goes through all glyphs with specified suffixes, and compares their widths", sizeStyle='small')

		suffixesTooltip = "Comma-separated list of suffixes, with or without dots. Usually, you want ‘.tf, .tosf’."
		self.w.suffixesText = vanilla.TextBox("auto", "Tabular suffixes", sizeStyle='small')
		self.w.suffixesText.setToolTip(suffixesTooltip)
		self.w.suffixesEntry = vanilla.EditText("auto", "tf, tosf", callback=self.SavePreferences, sizeStyle='small')
		self.w.suffixesEntry.setToolTip(suffixesTooltip)

		self.w.allowDifferingWidthsPerSuffix = vanilla.CheckBox("auto", u"Allow different widths in different suffixes", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allowDifferingWidthsPerSuffix.setToolTip("If checked, e.g., .tf and .tosf can have different widths in the same master. Otherwise .tf and .tosf must be same width.")

		self.w.includeNonExporting = vanilla.CheckBox("auto", "Also include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.setToolTip("If not set, non-exporting glyphs will be ignored.")

		self.w.allFonts = vanilla.CheckBox("auto", "Search in ⚠️ ALL fonts", value=True, callback=self.SavePreferences, sizeStyle="small")

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle='small')
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Report", callback=self.TabularCheckerMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.suffixesText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[suffixesText]-gap-[suffixesEntry]-inset-|",
				"H:|-inset-[allowDifferingWidthsPerSuffix]-(>=inset)-|",
				"H:|-inset-[includeNonExporting]-(>=inset)-|",
				"H:|-inset-[allFonts]-(>=inset)-|",
				"H:|-inset-[status]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-headlineGap-[suffixesEntry]-headlineGap-[allowDifferingWidthsPerSuffix]-checkRow-[includeNonExporting]-checkRow-[allFonts]-inset-[runButton]-inset-|",
				{"view1": self.w.suffixesText, "attribute1": "centerY", "view2": self.w.suffixesEntry, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "headlineGap": 10, "checkRow": 5},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def reportStatus(self, reportString):
		if not reportString:
			reportString = ""
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
			self.SavePreferences()

			# query user input:
			suffixString = self.pref("suffixesEntry")
			suffixes = [".%s" % s.strip().lstrip(".") for s in suffixString.split(",")]
			includeNonExporting = self.pref("includeNonExporting")
			allowDifferingWidthsPerSuffix = self.pref("allowDifferingWidthsPerSuffix")

			if self.pref("allFonts"):
				fonts = Glyphs.fonts
			else:
				fonts = (Glyphs.font, ) if Glyphs.font else ()

			for Font in fonts:
				print(u"Tabular Checker Report for %s" % Font.familyName)
				print(fontFileName(Font, fullPath=True))
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
						reportString = "🛠️ Testing '%s' in %s..." % (suffix, m.name)
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

			self.reportStatus("✅ Done.")
			print("Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Tabular Checker Error: %s" % e)
			import traceback
			print(traceback.format_exc())


TabularChecker()
