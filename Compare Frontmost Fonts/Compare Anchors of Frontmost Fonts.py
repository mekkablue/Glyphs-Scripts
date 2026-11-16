# MenuTitle: Compare Anchors
__doc__ = """
Compares anchor structure and anchor heights between the two frontmost fonts.
"""

import vanilla
from mekkablue import mekkaObject, SteppingEditText, decimalFormatter, fontFileName
from GlyphsApp import Glyphs, Message
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut


class CompareAnchorsOfFrontmostFonts(mekkaObject):
	prefDict = {
		"reportAnchorHeights": 1,
		"anchorHeightTolerance": 0,
		"ignoreExitEntry": 0,
		"ignoreHashtaggedAnchors": 0,
		"reportOnlyTopBottomCenter": 0,
		"includeNonExporting": 1,
		"openTabAndSelectAnchors": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 360
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Compare Anchors of Frontmost Fonts",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Lists all differences in anchor structures and positions in a detailed report in the Macro Window.", sizeStyle='small', selectable=True)
		# wraps to two lines, so it takes the width it is given:
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.reportAnchorHeights = vanilla.CheckBox("auto", "Also report differences in anchor heights", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportAnchorHeights.setToolTip("Lists anchors in corresponding glyphs if their y coordinates differ more than the threshold set below. Otherwise, only report anchor structures.")

		tooltipText = "Will not report if the difference in y coordinates is less or same as the given tolerance. Use this if e.g. your x-height is different in your italic. Set to zero for exact match."
		self.w.anchorHeightToleranceText = vanilla.TextBox("auto", "Deviation tolerance", sizeStyle='small', selectable=True)
		self.w.anchorHeightToleranceText.setToolTip(tooltipText)
		formatter = decimalFormatter(0)
		self.w.anchorHeightTolerance = SteppingEditText("auto", "0", callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		self.w.anchorHeightTolerance.setToolTip(tooltipText)

		self.w.ignoreExitEntry = vanilla.CheckBox("auto", "Ignore exit and entry anchors", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreExitEntry.setToolTip("Will skip cursive attachment anchors (#)exit and (#)entry.")

		self.w.ignoreHashtaggedAnchors = vanilla.CheckBox("auto", "Ignore #hashtagged anchors", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreHashtaggedAnchors.setToolTip("Will skip anchors that start with  # or _#.")

		self.w.reportOnlyTopBottomCenter = vanilla.CheckBox("auto", "Report only top, bottom, center and corresponding anchors", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportOnlyTopBottomCenter.setToolTip("Only reports default mark attachment anchors top, _top, bottom, _bottom, center and _center. Ignores other anchors such as ogonek or topright. This option makes the ignore options above obsolete.")

		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include non-exporting glyphs (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.setToolTip("Also report if glyph is set to not export. Recommended because non-exporting glyphs may appear as components in other glyphs.")

		self.w.openTabAndSelectAnchors = vanilla.CheckBox("auto", "Open tabs with affected glyph layers and preselect anchors", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTabAndSelectAnchors.setToolTip("Opens the affected glyph layers in a tab per font, resets the selection, and selects the affected anchors for immediate editing. To take advantage of the selection, do not double click a glyph for editing (the click resets the selection), but open them with the Esc key or by switching to the Edit tool.")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Compare", callback=self.CompareAnchorsOfFrontmostFontsMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[reportAnchorHeights]-(>=inset)-|",
				"H:|-indent-[anchorHeightToleranceText]-gap-[anchorHeightTolerance(55)]-(>=inset)-|",
				"H:|-inset-[ignoreExitEntry]-(>=inset)-|",
				"H:|-inset-[ignoreHashtaggedAnchors]-(>=inset)-|",
				"H:|-inset-[reportOnlyTopBottomCenter]-(>=inset)-|",
				"H:|-inset-[includeNonExporting]-(>=inset)-|",
				"H:|-inset-[openTabAndSelectAnchors]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-(>=inset)-[runButton(>=120)]-inset-|",
				"V:|-gap-[descriptionText(28)]-row-[reportAnchorHeights]-checkRow-[anchorHeightTolerance]-row-[ignoreExitEntry]-checkRow-[ignoreHashtaggedAnchors]-checkRow-[reportOnlyTopBottomCenter]-checkRow-[includeNonExporting]-checkRow-[openTabAndSelectAnchors]-barGap-[progress(16)]-inset-[runButton]-inset-|",
				{"view1": self.w.anchorHeightToleranceText, "attribute1": "centerY", "view2": self.w.anchorHeightTolerance, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "indent": inset + 18, "gap": 8, "row": 6, "checkRow": 5, "barGap": 12},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		try:
			onlyTopBottomSetting = bool(self.w.reportOnlyTopBottomCenter.get())
			ignoreSetting = not onlyTopBottomSetting
			self.w.ignoreExitEntry.enable(ignoreSetting)
			self.w.ignoreHashtaggedAnchors.enable(ignoreSetting)
		except Exception as e:
			print("Error: Could not update UI. You can ignore this warning, but let Rainer know.")
			print(e)
			import traceback
			print(traceback.format_exc())

	def selectAnchorsInLayer(self, anchorNames, layer, resetSelection=True):
		if resetSelection:
			layer.selection = None
		if anchorNames:
			for anchorName in anchorNames:
				thisAnchor = layer.anchors[anchorName]
				if thisAnchor:
					thisAnchor.selected = True

	def CompareAnchorsOfFrontmostFontsMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			# query prefs:
			reportOnlyTopBottomCenter = self.pref("reportOnlyTopBottomCenter")
			ignoreExitEntry = self.pref("ignoreExitEntry")
			ignoreHashtaggedAnchors = self.pref("ignoreHashtaggedAnchors")
			reportAnchorHeights = self.pref("reportAnchorHeights")

			if len(Glyphs.fonts) < 2:
				Message(title="Compare Error", message="You need to have at least two fonts open for comparing.", OKButton="Ooops")
			else:
				# brings macro window to front and clears its log:
				Glyphs.clearLog()
				# Glyphs.showMacroWindow()

				thisFont = Glyphs.font  # frontmost font
				otherFont = Glyphs.fonts[1]  # second font
				# unsaved fonts have no file path:
				thisFilePath = "~/" + thisFont.filepath.relativePathFromBaseDirPath_("~") if thisFont.filepath else "⚠️ The font file has not been saved yet."
				otherFilePath = "~/" + otherFont.filepath.relativePathFromBaseDirPath_("~") if otherFont.filepath else "⚠️ The font file has not been saved yet."
				thisFileName = fontFileName(thisFont)
				otherFileName = fontFileName(otherFont)
				print(
					"Compare Anchors of Frontmost Fonts Report for:\n  (1) %s: %s\n      %s\n  (2) %s: %s\n      %s" % (
						thisFont.familyName,
						thisFilePath,
						thisFileName,
						otherFont.familyName,
						otherFilePath,
						otherFileName,
					)
				)
				print()

				try:
					tolerance = abs(self.prefFloat("anchorHeightTolerance"))
				except:
					tolerance = 0.0
				if reportAnchorHeights:
					print("Anchor height tolerance: %.1f units" % tolerance)
					print()

				theseIDs = [m.id for m in thisFont.masters]
				otherIDs = [m.id for m in otherFont.masters]
				masters = tuple(zip(theseIDs, otherIDs))

				if len(theseIDs) != len(otherIDs):
					print("⚠️ Different number of masters in (1) %s and (2) %s" % (thisFileName, otherFileName))
					print()

				skippedGlyphNames = []
				affectedGlyphNames = []
				for i, thisGlyph in enumerate(thisFont.glyphs):
					self.w.progress.set(100 * i / len(thisFont.glyphs))
					otherGlyph = otherFont.glyphs[thisGlyph.name]
					if not otherGlyph:
						print("⚠️ Glyph %s missing in (2) %s" % (thisGlyph.name, otherFileName))
					else:
						if not (thisGlyph.export or self.pref("includeNonExporting")):
							skippedGlyphNames.append(thisGlyph.name)
							if otherGlyph.export:
								print("😬 Glyph %s exports in (2) %s, but not in (1) %s. Skipping." % (thisGlyph.name, otherFileName, thisFileName))
						else:
							if not (otherGlyph.export or self.pref("includeNonExporting")):
								print("😬 Glyph %s exports in (1) %s, but not in (2) %s. Skipping." % (thisGlyph.name, thisFileName, otherFileName))
								skippedGlyphNames.append(thisGlyph.name)
							else:

								for idSet in masters:
									thisID, otherID = idSet
									thisLayer, otherLayer = thisGlyph.layers[thisID], otherGlyph.layers[otherID]
									if self.pref("openTabAndSelectAnchors"):
										self.selectAnchorsInLayer(None, thisLayer, resetSelection=True)
										self.selectAnchorsInLayer(None, otherLayer, resetSelection=True)

									theseAnchors = sorted([a.name for a in thisLayer.anchors])
									otherAnchors = sorted([a.name for a in otherLayer.anchors])

									# clean up compare lists if requested:
									for anchorList in (theseAnchors, otherAnchors):
										for i in range(len(anchorList))[::-1]:
											currentAnchor = anchorList[i]
											if reportOnlyTopBottomCenter:
												# keep only top/bottom/center:
												if currentAnchor not in ("top", "bottom", "center", "_top", "_bottom", "_center"):
													del anchorList[i]
											else:
												# determine exit and entry anchors:
												anchorIsExitOrEntry = False
												for anchorname in ("exit", "entry"):
													if currentAnchor.endswith(anchorname) and len(currentAnchor) in (len(anchorname), len(anchorname) + 1):
														anchorIsExitOrEntry = True

												# determine hashtagged anchors:
												anchorIsHashtagged = currentAnchor.startswith("#") or currentAnchor.startswith("_#")

												# remove if affected:
												if (ignoreExitEntry and anchorIsExitOrEntry) or (ignoreHashtaggedAnchors and anchorIsHashtagged):
													del anchorList[i]

									if theseAnchors != otherAnchors:
										missingInOtherAnchors = [a for a in theseAnchors if a not in otherAnchors]
										missingInTheseAnchors = [a for a in otherAnchors if a not in theseAnchors]

										if missingInTheseAnchors:
											print(
												"🚫 %s (%s): missing anchor%s %s in (1) %s" % (
													thisGlyph.name,
													thisLayer.name,
													"" if len(missingInTheseAnchors) == 1 else "s",
													", ".join(["'%s'" % a for a in missingInTheseAnchors]),
													thisFileName,
												)
											)
											if self.pref("openTabAndSelectAnchors"):
												self.selectAnchorsInLayer(missingInTheseAnchors, otherLayer, resetSelection=False)
											affectedGlyphNames.append(otherGlyph.name)

										if missingInOtherAnchors:
											print(
												"🚫 %s (%s): missing anchor%s %s in (2) %s" % (
													otherGlyph.name,
													otherLayer.name,
													"" if len(missingInOtherAnchors) == 1 else "s",
													", ".join(["'%s'" % a for a in missingInOtherAnchors]),
													otherFileName,
												)
											)
											if self.pref("openTabAndSelectAnchors"):
												self.selectAnchorsInLayer(missingInOtherAnchors, thisLayer, resetSelection=False)
											affectedGlyphNames.append(thisGlyph.name)

									if reportAnchorHeights:
										differingAnchors = []
										for thisAnchorName in theseAnchors:
											if thisAnchorName in otherAnchors:
												thisAnchor = thisLayer.anchors[thisAnchorName]
												otherAnchor = otherLayer.anchors[thisAnchorName]
												if thisAnchor and otherAnchor:  # just to make sure
													heightDifference = abs(thisAnchor.position.y - otherAnchor.position.y)
													if not heightDifference <= tolerance:
														differingAnchors.append(thisAnchor.name)

										if differingAnchors:
											print(
												"↕️ %s: %s deviate%s in: (1) %s, (2) %s" % (
													thisGlyph.name,
													", ".join(["'%s'" % a for a in differingAnchors]),
													"s" if len(differingAnchors) == 1 else "",
													thisLayer.name,
													otherLayer.name,
												)
											)
											if self.pref("openTabAndSelectAnchors"):
												self.selectAnchorsInLayer(differingAnchors, thisLayer, resetSelection=False)
												self.selectAnchorsInLayer(differingAnchors, otherLayer, resetSelection=False)
											affectedGlyphNames.append(thisGlyph.name)

				# open tab or macro window:
				affectedGlyphNames = set(affectedGlyphNames)
				if affectedGlyphNames:
					tabString = "/" + "/".join(affectedGlyphNames)
					print("\nFound %i affected glyphs:\n%s" % (len(affectedGlyphNames), tabString))

					if self.pref("openTabAndSelectAnchors"):
						# opens new Edit tab:
						thisFont.newTab(tabString)
						otherFont.newTab(tabString)
					else:
						# brings macro window to front:
						Glyphs.showMacroWindow()

				if skippedGlyphNames:
					print("\nSkipped %i glyphs:\n%s" % (len(skippedGlyphNames), ", ".join(skippedGlyphNames)))

				self.w.progress.set(100)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Compare Anchors of Frontmost Fonts Error: %s" % e)
			import traceback
			print(traceback.format_exc())


CompareAnchorsOfFrontmostFonts()
