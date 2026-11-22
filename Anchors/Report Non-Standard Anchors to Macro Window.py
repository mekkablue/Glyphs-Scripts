# MenuTitle: Report Non-Standard Anchors to Macro Window
__doc__ = """
Goes through all glyphs in the font and reports in the Macro Window if it finds non-default anchors. Lines are copy-paste-able in Editview.
"""

import vanilla
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
)
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class ReportNonStandardAnchorsInMacroWindow(mekkaObject):
	prefDict = {
		"includeNonExporting": 0,
		"reportExitEntry": 0,
		"reportCarets": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 255
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Report Non-Standard Anchors",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 16
		self.w.text_1 = vanilla.TextBox("auto", __doc__.strip(), sizeStyle="small")
		# a wrapping block takes the width it is given instead of demanding one long line:
		self.w.text_1.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeNonExporting.setToolTip("Also check glyphs that are set to not export.")
		self.w.reportExitEntry = vanilla.CheckBox("auto", "Report exit and entry anchors", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.reportExitEntry.setToolTip("Also list exit and entry anchors, which are normally skipped.")
		self.w.reportCarets = vanilla.CheckBox("auto", "Report ligature caret anchors", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.reportCarets.setToolTip("Also list caret anchors in ligatures, which are normally skipped.")

		# Status line and Run Button:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.runButton = vanilla.Button("auto", "Report", callback=self.ReportNonStandardAnchorsInMacroWindowMain)
		self.w.runButton.setToolTip("Report the unusual anchors in the Macro Window.")
		self.w.setDefaultButton(self.w.runButton)

		# the status line takes the leftover width, the button stays as wide as its title needs:
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-inset-|",
				"H:|-inset-[includeNonExporting]-(>=inset)-|",
				"H:|-inset-[reportExitEntry]-(>=inset)-|",
				"H:|-inset-[reportCarets]-(>=inset)-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[text_1(56)]-row-[includeNonExporting]-checkRow-[reportExitEntry]-checkRow-[reportCarets]-inset-[runButton]-inset-|",
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 10, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def ReportNonStandardAnchorsInMacroWindowMain(self, sender):
		currentGlyphName = None
		try:
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			thisFont = Glyphs.font
			if not thisFont:
				Glyphs.showMacroWindow()
				print("⚠️ No font open.")
				self.setStatus("⚠️ No font open.")
				return

			self.SavePreferences()
			includeNonExporting = self.prefBool("includeNonExporting")
			reportExitEntry = self.prefBool("reportExitEntry")
			reportCarets = self.prefBool("reportCarets")

			print(f"Reporting non-standard anchors in {thisFont.familyName}")
			if thisFont.filepath:
				print(thisFont.filepath)
			print()

			self.setStatus(f"🛠️ Processing {len(thisFont.glyphs)} glyphs…")
			reportedCount = 0
			for thisGlyph in thisFont.glyphs:
				currentGlyphName = thisGlyph.name
				self.setStatus(f"🔠 {thisGlyph.name}")
				if thisGlyph.export or includeNonExporting:
					thisLayer = thisGlyph.layers[0]
					if thisLayer.anchors:

						# determine defaults
						defaultAnchors = None
						glyphinfo = thisFont.glyphsInfo().glyphInfoForName_(thisGlyph.name)
						if glyphinfo:
							defaultAnchors = glyphinfo.anchors

						# find unusual anchors in this glyph
						unusualAnchors = []
						if not defaultAnchors:
							defaultAnchors = ()
						glyphIsLigature = (thisGlyph.subCategory == "Ligature" or "_" in thisGlyph.name[1:])
						for thisAnchor in thisLayer.anchors:
							if thisAnchor.name not in defaultAnchors:
								anchorIsExitEntry = thisAnchor.name in ("exit", "entry") or thisAnchor.name[1:] in ("exit", "entry")
								anchorIsCaret = thisAnchor.name.startswith("caret")

								# see if exceptions apply:
								if anchorIsCaret and glyphIsLigature and not reportCarets:
									pass  # carets in ligatures
								elif anchorIsExitEntry and not reportExitEntry:
									pass  # exit and entry anchors
								else:
									unusualAnchors.append(thisAnchor.name)

						if unusualAnchors:
							print(f"/{thisGlyph.name} : {', '.join(unusualAnchors)}")
						reportedCount += 1

			print("\n(Hint: Lines can be copied and pasted in Edit view.)")
			print("\n✅ Done.")
			if reportedCount:
				self.setStatus(f"✅ Reported {reportedCount} glyph{'' if reportedCount == 1 else 's'}.")
			else:
				self.setStatus("✅ No non-standard anchors found.")
			Glyphs.showMacroWindow()

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			self.setStatus(f"❌ Error at {currentGlyphName}. Details in Macro Window." if currentGlyphName else "❌ Error. Details in Macro Window.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Report Non-Standard Anchors to Macro Window Error: {e}")
			import traceback
			print(traceback.format_exc())


ReportNonStandardAnchorsInMacroWindow()
