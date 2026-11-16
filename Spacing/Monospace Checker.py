# MenuTitle: Monospace Checker
__doc__ = """
Checks if all glyph widths in the frontmost font are actually monospaced. Reports in Macro Window and opens a tab with affected layers.
"""

import vanilla
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSNumberFormatter
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, newLineControlLayer, SteppingEditText, fontFileName


class MonospaceChecker(mekkaObject):
	prefDict = {
		"defaultGlyphName": "A",
		"tolerance": 0.0,
		"reportZeroWidths": False,
		"includeNonExporting": False,
		"setMonospaceFlag": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Monospace Checker",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "New tab with glyphs that do not match the width of the default glyph in each master", sizeStyle='small', selectable=True)
		# the text wraps: it takes the width it is given, and has a fixed height in the rules
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.defaultGlyphNameText = vanilla.TextBox("auto", "Default Glyph", sizeStyle='small', selectable=True)
		self.w.defaultGlyphName = vanilla.EditText("auto", "A", callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "For each master, will measure the width of this glyph, and compare all other widths to it."
		self.w.defaultGlyphNameText.setToolTip(tooltipText)
		self.w.defaultGlyphName.setToolTip(tooltipText)

		self.w.toleranceText = vanilla.TextBox("auto", "Tolerance in units", sizeStyle='small', selectable=True)
		formatter = NSNumberFormatter.alloc().init()  # decimals allowed
		formatter.setMinimum_(0)
		self.w.tolerance = SteppingEditText("auto", "0.0", callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		tooltipText = "Allow deviations up to this value. 1 unit may be acceptable. If you are not sure, keep it at zero."
		self.w.toleranceText.setToolTip(tooltipText)
		self.w.tolerance.setToolTip(tooltipText)

		self.w.reportZeroWidths = vanilla.CheckBox("auto", "Report Zero Widths in Macro Window", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportZeroWidths.setToolTip("In the Macro Window (and only there), will also report glyphs that have zero width. Usually you can ignore those.")

		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include Non-Exporting Glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.setToolTip("If disabled, will ignore non-exporting glyphs. If you are unsure, leave it off.")

		self.w.setMonospaceFlag = vanilla.CheckBox("auto", "Set ‘isFixedPitch’ flag in Font Info", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.setMonospaceFlag.setToolTip("Will set the isFixedPitch parameter in Font Info > Font. The parameter sets the isFixedPitch flag in the post table. Indicates whether the font is monospaced. Software can use this information to make sure that all glyphs are rendered with the same amount of pixels horizontally at any given PPM size.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Check", callback=self.MonospaceCheckerMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned, hug their text and share one width:
		for labelName in ("defaultGlyphNameText", "toleranceText"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[defaultGlyphNameText]-gap-[defaultGlyphName]-inset-|",
				"H:|-inset-[toleranceText]-gap-[tolerance(55)]-(>=inset)-|",
				"H:|-inset-[reportZeroWidths]-(>=inset)-|",
				"H:|-inset-[includeNonExporting]-(>=inset)-|",
				"H:|-inset-[setMonospaceFlag]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText(28)]-headlineGap-[defaultGlyphName]-row-[tolerance]-sectionGap-[reportZeroWidths]-checkRow-[includeNonExporting]-checkRow-[setMonospaceFlag]-inset-[runButton]-inset-|",
				{"view1": self.w.defaultGlyphNameText, "attribute1": "centerY", "view2": self.w.defaultGlyphName, "attribute2": "centerY"},
				{"view1": self.w.toleranceText, "attribute1": "centerY", "view2": self.w.tolerance, "attribute2": "centerY"},
				{"view1": self.w.toleranceText, "attribute1": "width", "view2": self.w.defaultGlyphNameText, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "headlineGap": 8, "sectionGap": 12, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def MonospaceCheckerMain(self, sender):
		try:
			# brings macro window to front and clears its log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			else:
				print("Monospace Checker Report for %s" % thisFont.familyName)
				print(fontFileName(thisFont, fullPath=True))
				print()

			defaultGlyphName = self.pref("defaultGlyphName").strip()
			defaultGlyph = thisFont.glyphs[defaultGlyphName]
			tolerance = self.prefFloat("tolerance")
			includeNonExporting = self.prefBool("includeNonExporting")
			reportZeroWidths = self.prefBool("reportZeroWidths")

			if not defaultGlyph:
				Message(
					title="Glyph Not Found",
					message="Could not find a glyph named '%s' in the frontmost font (%s). Aborting." % (defaultGlyphName, thisFont.familyName),
					OKButton="Oops",
				)
				return
			else:
				affectedLayers = []
				deviatingWidthCount = 0
				for thisMaster in thisFont.masters:
					masterID = thisMaster.id
					defaultWidth = defaultGlyph.layers[masterID].width
					layerCountBeforeMaster = len(affectedLayers)
					print("\nⓂ️ Master %s, default width: %.1f" % (thisMaster.name, defaultWidth))
					for thisGlyph in thisFont.glyphs:
						if thisGlyph.export or includeNonExporting:
							for thisLayer in thisGlyph.layers:
								if thisLayer.associatedMasterId == masterID and (thisLayer.isMasterLayer or thisLayer.isSpecialLayer):
									thisWidth = thisLayer.width
									if thisWidth == 0.0:
										if reportZeroWidths:
											print("ℹ️ %s, layer '%s': zero width" % (thisGlyph.name, thisLayer.name))
									elif not (defaultWidth - tolerance) <= thisWidth <= (defaultWidth + tolerance):
										affectedLayers.append(thisLayer)
										deviatingWidthCount += 1
										print("⛔️ %s, layer '%s': %.1f" % (thisGlyph.name, thisLayer.name, thisWidth))

					# add a newline after the layers of this master:
					if len(affectedLayers) > layerCountBeforeMaster:
						newLine = newLineControlLayer()
						affectedLayers.append(newLine)

			if affectedLayers:
				# Floating notification:
				Glyphs.showNotification(
					"Inconsistent widths in %s" % (thisFont.familyName),
					"Found %i width deviation%s. Details in Macro Window." % (
						deviatingWidthCount,
						"" if deviatingWidthCount == 1 else "s",
					),
				)
				# opens new Edit tab:
				newTab = thisFont.newTab()
				newTab.layers = affectedLayers
			else:
				# Floating notification:
				Glyphs.showNotification(
					"🥇 %s has consistent widths" % (thisFont.familyName),
					"All glyph widths are monospaced. Congrats!",
				)

			if self.prefBool("setMonospaceFlag"):
				print("\nℹ️ Font Info > Font > Custom Parameters:")
				if thisFont.customParameters["isFixedPitch"]:
					print("👍🏻 isFixedPitch parameter already set. OK.")
				else:
					if thisFont.customParameters["isFixedPitch"] is None:
						print("⚠️✅ isFixedPitch parameter was missing, now set. OK.")
					else:
						print("😱✅ isFixedPitch parameter was turned off, now set. OK.")
					thisFont.customParameters["isFixedPitch"] = True

			# self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Monospace Checker Error: %s" % e)
			import traceback
			print(traceback.format_exc())


MonospaceChecker()
