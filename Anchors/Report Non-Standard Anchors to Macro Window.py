# MenuTitle: Report Non-Standard Anchors to Macro Window
__doc__ = """
Goes through all glyphs in the font and reports in the Macro Window if it finds non-default anchors. Lines are copy-paste-able in Editview.
"""

import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
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
		windowWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Report Non-Standard Anchors to Macro Window",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 16
		self.w.text_1 = vanilla.TextBox("auto", __doc__.strip(), sizeStyle="small")
		# a wrapping block takes the width it is given instead of demanding one long line:
		self.w.text_1.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.reportExitEntry = vanilla.CheckBox("auto", "Report exit and entry anchors", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.reportCarets = vanilla.CheckBox("auto", "Report ligature caret anchors", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Report", callback=self.ReportNonStandardAnchorsInMacroWindowMain)
		self.w.setDefaultButton(self.w.runButton)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-inset-|",
				"H:|-inset-[includeNonExporting]-(>=inset)-|",
				"H:|-inset-[reportExitEntry]-(>=inset)-|",
				"H:|-inset-[reportCarets]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[text_1(42)]-row-[includeNonExporting]-checkRow-[reportExitEntry]-checkRow-[reportCarets]-inset-[runButton]-inset-|",
			],
			metrics={"inset": inset, "gap": 10, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def ReportNonStandardAnchorsInMacroWindowMain(self, sender):
		try:
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			thisFont = Glyphs.font
			if not thisFont:
				print("⚠️ No font open.")
				return

			self.SavePreferences()
			includeNonExporting = self.prefBool("includeNonExporting")
			reportExitEntry = self.prefBool("reportExitEntry")
			reportCarets = self.prefBool("reportCarets")

			print(f"Unusual anchors in {thisFont.familyName}")
			print(f"File: {thisFont.filepath}\n")

			for thisGlyph in thisFont.glyphs:
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

			print("\n(Hint: Lines can be copied and pasted in Edit view.)")
			Glyphs.showMacroWindow()

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Report Non-Standard Anchors to Macro Window Error: {e}")
			import traceback
			print(traceback.format_exc())


ReportNonStandardAnchorsInMacroWindow()
