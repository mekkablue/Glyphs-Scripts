# MenuTitle: Compare Glyph Heights
__doc__ = """
Lists all glyphs that differ from the second font in height beyond a given threshold.
"""

import objc
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


class CompareGlyphHeightsOfFrontmostFonts(mekkaObject):
	prefDict = {
		"heights": 0,
		"depths": 0,
		"tolerate": 0,
		"includeNonExporting": 0,
		"verbose": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Compare Glyph Heights of Frontmost Fonts",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Lists all glyphs that differ in height more than the given threshold. Detailed report in Macro Window.", sizeStyle='small', selectable=True)
		# wraps to two lines, so it takes the width it is given:
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		tooltipText = "How much of a difference is OK. Hint: overshoot size is a good idea for this one."
		self.w.tolerateText = vanilla.TextBox("auto", "Tolerate difference up to", sizeStyle='small', selectable=True)
		self.w.tolerateText.setToolTip(tooltipText)
		formatter = NSNumberFormatter.alloc().init()
		formatter.setMinimum_(0)
		self.w.tolerate = SteppingEditText("auto", "5", callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		self.w.tolerate.setToolTip(tooltipText)

		self.w.heights = vanilla.CheckBox("auto", "Compare top bounds (‘heights’)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.heights.setToolTip("Measures and compares the heights of the top edges (bbox maximum).")

		self.w.depths = vanilla.CheckBox("auto", "Compare bottom bounds (‘depths’)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.depths.setToolTip("Measures and compares the heights of the bottom edges (bbox minimum).")

		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.setToolTip("If enabled, also measures glyphs that are set to not export.")

		self.w.verbose = vanilla.CheckBox("auto", "Verbose output in Macro Window (slow)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose.setToolTip("Will output a detailed progress report in Window > Macro Panel. This slows down the script significantly, so only use for debugging.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Compare", callback=self.CompareGlyphHeightsOfFrontmostFontsMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[tolerateText]-gap-[tolerate(55)]-(>=inset)-|",
				"H:|-inset-[heights]-(>=inset)-|",
				"H:|-inset-[depths]-(>=inset)-|",
				"H:|-inset-[includeNonExporting]-(>=inset)-|",
				"H:|-inset-[verbose]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=120)]-inset-|",
				"V:|-gap-[descriptionText(28)]-row-[tolerate]-row-[heights]-checkRow-[depths]-checkRow-[includeNonExporting]-checkRow-[verbose]-inset-[runButton]-inset-|",
				{"view1": self.w.tolerateText, "attribute1": "centerY", "view2": self.w.tolerate, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		if not self.w.heights.get() and not self.w.depths.get():
			self.w.runButton.enable(False)
		else:
			self.w.runButton.enable(True)

	def CompareGlyphHeightsOfFrontmostFontsMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			if len(Glyphs.fonts) < 2:
				Message(title="Compare Error", message="You need to have at least two fonts open for comparing.", OKButton="Ooops")
			else:
				Glyphs.clearLog()

				thisFont = Glyphs.font  # frontmost font
				otherFont = Glyphs.fonts[1]  # second font
				# unsaved fonts have no file path:
				thisFileName = thisFont.filepath.lastPathComponent() if thisFont.filepath else f"{thisFont.familyName} (unsaved)"
				otherFileName = otherFont.filepath.lastPathComponent() if otherFont.filepath else f"{otherFont.familyName} (unsaved)"
				print(
					"Compare Glyph Heights of Frontmost Fonts Report for:\n  (1) %s: %s\n      %s\n  (2) %s: %s\n      %s" % (
						thisFont.familyName,
						thisFileName,
						thisFont.filepath if thisFont.filepath else "⚠️ The font file has not been saved yet.",
						otherFont.familyName,
						otherFileName,
						otherFont.filepath if otherFont.filepath else "⚠️ The font file has not been saved yet.",
					)
				)
				print()

				heights = self.pref("heights")
				depths = self.pref("depths")
				tolerate = self.prefFloat("tolerate")
				includeNonExporting = self.pref("includeNonExporting")
				verbose = self.prefBool("verbose")

				theseIDs = [m.id for m in thisFont.masters]
				otherIDs = [m.id for m in otherFont.masters]
				masterIDs = tuple(zip(theseIDs, otherIDs))
				collectedGlyphNames = []

				if len(theseIDs) != len(otherIDs):
					print("⚠️ Different number of masters in %s and %s" % (thisFileName, otherFileName))

				for thisGlyph in thisFont.glyphs:
					if thisGlyph.export or includeNonExporting:
						if verbose:
							print("🔠 Comparing %s" % thisGlyph.name)
						glyphName = thisGlyph.name
						otherGlyph = otherFont.glyphs[glyphName]
						if not otherGlyph:
							if verbose:
								print("🚫 %s not in %s" % (glyphName, otherFileName))
							continue
						if not otherGlyph.export and verbose:
							print("⚠️ %s not exporting in %s" % (glyphName, otherFileName))
						for idPair in masterIDs:
							thisID, otherID = idPair
							thisLayer = thisGlyph.layers[thisID]
							otherLayer = otherGlyph.layers[otherID]
							if not (thisLayer and otherLayer):
								if verbose:
									print("⚠️ Cannot compare layers in %s" % glyphName)
							else:
								if heights:
									thisHeight = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
									otherHeight = otherLayer.bounds.origin.y + otherLayer.bounds.size.height
									if abs(thisHeight - otherHeight) > tolerate:
										if verbose:
											print("  ❌ %s heights: (1) %.1f, (2) %.1f" % (glyphName, thisHeight, otherHeight))
										collectedGlyphNames.append(glyphName)
								if depths:
									thisDepth = thisLayer.bounds.origin.y
									otherDepth = otherLayer.bounds.origin.y
									if abs(thisDepth - otherDepth) > tolerate:
										if verbose:
											print("  ❌ %s depths: (1) %.1f, (2) %.1f" % (glyphName, thisDepth, otherDepth))
										collectedGlyphNames.append(glyphName)

				if not collectedGlyphNames:
					Message(
						title="No significant differences",
						message="No differences larger than %.1f found between the two frontmost fonts. See the macro window for error messages." % tolerate,
						OKButton="😎 Cool"
					)
				else:
					collectedGlyphNames = tuple(set(collectedGlyphNames))
					tabText = "/" + "/".join(collectedGlyphNames)
					thisFont.newTab(tabText)
					otherFont.newTab(tabText)

				print("✅ Done.")
				if verbose:
					Glyphs.showMacroWindow()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Compare Glyph Heights of Frontmost Fonts Error: %s" % e)
			import traceback
			print(traceback.format_exc())


CompareGlyphHeightsOfFrontmostFonts()
