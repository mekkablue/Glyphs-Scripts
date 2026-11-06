# MenuTitle: Realign Stacking Anchors
__doc__ = """
On all layers in combining marks, top/_top, bottom/_bottom, etc. anchor pairs are realigned in their italic angle. Only moves anchors horizontally.
"""

import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
	NSWindowStyleMaskResizable,
)
from Foundation import NSPoint
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton
from mekkablue.geometry import italicize


class RealignStackingAnchors(mekkaObject):
	prefDict = {
		"whichAnchorPairs": "top, bottom",
		"allGlyphs": 1,
		"limitToCombiningMarks": 1,
		"includeNonExporting": 0,
		"allFonts": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 380
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		windowWidthResize = 100  # user can resize width by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Realign Stacking Anchors in Combining Accents",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox(
			"auto",
			"Realign stacking anchor pairs to each other (anchors with and without leading underscore, e.g. _top to top) in their respective italic angle, for pairs of these anchors:",
			sizeStyle="small",
			selectable=True,
		)
		# a wrapping block takes the width it is given instead of demanding one long line
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.whichAnchorPairs = vanilla.EditText("auto", "top, bottom", callback=self.SavePreferences, sizeStyle="small")
		self.w.whichAnchorPairs.setToolTip("Comma-separated list of anchor names. With or without underscore does not matter. You only need to specify one of both. Example: ‘top, bottom’.")
		self.w.resetButton = UpdateButton("auto", callback=self.resetAnchorPairs)
		self.w.resetButton.setToolTip("Reset the anchor names to ‘top, bottom’.")

		self.w.allGlyphs = vanilla.CheckBox("auto", "Include all glyphs in font (i.e., ignore selection, recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allGlyphs.setToolTip("If checked, will ignore the current glyph selection, and process all glyphs in the font, minus the glyphs that are excluded by the following two settings.")

		self.w.limitToCombiningMarks = vanilla.CheckBox("auto", "Limit to combining marks (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.limitToCombiningMarks.setToolTip("If checked, among the processed glyphs, will process only glyphs that are categorised as combining marks. Usually this is where you want the realignment if stacking anchors. Uncheck if your accents are not correctly categorised.")

		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include non-exporting glyphs (recommended)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeNonExporting.setToolTip("If checked, will also process glyphs that are set to not export. Otherwise only exporting glyphs.")

		self.w.allFonts = vanilla.CheckBox("auto", "⚠️ Apply to ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.setToolTip("If checked, will apply to ALL fonts currently open in Glyphs. You have been warned.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Realign", callback=self.RealignStackingAnchorsMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[whichAnchorPairs]-gap-[resetButton(20)]-inset-|",
				"H:|-inset-[allGlyphs]-(>=inset)-|",
				"H:|-inset-[limitToCombiningMarks]-(>=inset)-|",
				"H:|-inset-[includeNonExporting]-(>=inset)-|",
				"H:|-inset-[allFonts]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText(42)]-row-[whichAnchorPairs]-row-[allGlyphs]-checkRow-[limitToCombiningMarks]-checkRow-[includeNonExporting]-checkRow-[allFonts]-inset-[runButton]-inset-|",
				{"view1": self.w.resetButton, "attribute1": "centerY", "view2": self.w.whichAnchorPairs, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# resizable horizontally only: content height stays fixed
		nsWindow = self.w.getNSWindow()
		contentHeight = nsWindow.contentRectForFrameRect_(nsWindow.frame()).size.height
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.setContentMinSize_((windowWidth, contentHeight))
		nsWindow.setContentMaxSize_((windowWidth + windowWidthResize, contentHeight))

	def resetAnchorPairs(self, sender=None):
		self.w.whichAnchorPairs.set(self.prefDict["whichAnchorPairs"])
		self.SavePreferences()

	def RealignStackingAnchorsMain(self, sender):
		try:
			Glyphs.clearLog()  # clears macro window log
			print("Realign Stacking Anchors:")

			# update settings to the latest user input:
			self.SavePreferences()

			whichAnchorPairs = self.pref("whichAnchorPairs")
			anchorPairs = [a.strip() for a in whichAnchorPairs.split(",")]
			allGlyphs = self.pref("allGlyphs")
			limitToCombiningMarks = self.pref("limitToCombiningMarks")
			includeNonExporting = self.pref("includeNonExporting")
			allFonts = self.pref("allFonts")
			movedAnchorCount = 0
			glyphCount = 0

			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			for thisFont in theseFonts:
				fontNameForReport = thisFont.familyName
				if thisFont.filepath:
					fontNameForReport = thisFont.filepath.lastPathComponent()
				print("\n📄 %s" % fontNameForReport)

				if not allGlyphs:
					if includeNonExporting:
						glyphs = [layer.parent for layer in thisFont.selectedLayers]
					else:
						glyphs = [layer.parent for layer in thisFont.selectedLayers if layer.parent.export]
				else:
					if includeNonExporting:
						glyphs = thisFont.glyphs
					else:
						glyphs = [g for g in thisFont.glyphs if g.export]

				if limitToCombiningMarks:
					glyphs = [g for g in glyphs if g.category == "Mark" and g.subCategory == "Nonspacing"]

				glyphCount += len(glyphs)
				print("🔢 Processing %i glyph%s..." % (
					len(glyphs),
					"" if len(glyphs) == 1 else "s",
				))

				for thisGlyph in glyphs:
					for thisLayer in thisGlyph.layers:
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:

							# Nomenclature:
							#  top: default anchor
							# _top: underscore Anchor
							for defaultAnchorName in anchorPairs:

								# sanitize user entry:
								# get the default anchor name by getting rid of leading underscores
								while defaultAnchorName[0] == "_" and len(defaultAnchorName) > 1:
									defaultAnchorName = defaultAnchorName[1:]

								# derive underscore anchor from default anchor
								underscoreAnchorName = "_%s" % defaultAnchorName
								underscoreAnchor = thisLayer.anchors[underscoreAnchorName]

								# only proceed if there are both anchors:
								if underscoreAnchor:
									defaultAnchor = thisLayer.anchors[defaultAnchorName]
									if defaultAnchor:
										# record original position:
										oldPosition = defaultAnchor.position

										# determine italic angle and move the anchor accordingly:
										if Glyphs.versionNumber >= 3:
											# GLYPHS 3
											italicAngle = thisLayer.italicAngle
										else:
											# GLYPHS 2
											italicAngle = thisLayer.associatedFontMaster().italicAngle
										straightPosition = NSPoint(underscoreAnchor.position.x, defaultAnchor.position.y)
										if italicAngle:
											defaultAnchor.position = italicize(straightPosition, italicAngle, underscoreAnchor.position.y)
										else:
											defaultAnchor.position = straightPosition

										# compare new position to original position, and report if moved:
										if defaultAnchor.position != oldPosition:
											print("↔️ Moved %s in 🔠 %s, layer ‘%s’" % (defaultAnchorName, thisGlyph.name, thisLayer.name))
											movedAnchorCount += 1

			self.w.close()  # delete if you want window to stay open

			# wrap up and report:
			report = "Moved %i anchor%s in %i glyph%s%s." % (
				movedAnchorCount,
				"" if movedAnchorCount == 1 else "s",
				glyphCount,
				"" if glyphCount == 1 else "s",
				" in %i fonts" % len(theseFonts) if len(theseFonts) > 1 else "",
			)
			print("\n%s\nDone." % report)
			Message(
				title="Realigned Anchors",
				message="%s Detailed report in Macro Window." % report,
				OKButton=None,
			)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Realign Stacking Anchors in Combining Accents Error: %s" % e)
			import traceback
			print(traceback.format_exc())


RealignStackingAnchors()
