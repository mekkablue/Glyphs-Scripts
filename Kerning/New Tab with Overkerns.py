# MenuTitle: New Tab with Overkerned Pairs
__doc__ = """
Asks a threshold percentage, and opens a new tab with all kern pairs going beyond the width threshold. Option to fix them too.
"""

import objc
import vanilla
from mekkablue import mekkaObject, newLineControlLayer, reportFontName
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def integerFormatter(minimum=None, maximum=None):
	"""Number formatter that only accepts integers, optionally within a range."""
	formatter = NSNumberFormatter.alloc().init()
	formatter.setAllowsFloats_(False)
	if minimum is not None:
		formatter.setMinimum_(minimum)
	if maximum is not None:
		formatter.setMaximum_(maximum)
	return formatter


def roundedDownBy(value, base):
	return base * round(value // base)


class NewTabwithOverkernedPairs(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"threshold": 40,
		"limitToExportingGlyphs": 1,
		"rounding": 5,
		"scope": 1,
		"verbose": False,
		"ignore": "fraction, .dnom, .numr, inferior, superior, .percent, slash, ordfeminine, ordmasculine",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 460
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Negative Overkerns in this Master",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		tooltipText = "Max percentage of the (narrower) glyph or group width that may be kerned."
		self.w.thresholdText = vanilla.TextBox("auto", "Open tab with kerns beyond threshold:", sizeStyle='small', selectable=True)
		self.w.threshold = vanilla.EditText("auto", "40", callback=self.SavePreferences, sizeStyle='small')
		self.w.thresholdPercent = vanilla.TextBox("auto", "%", sizeStyle='small', selectable=True)
		self.w.thresholdText.setToolTip(tooltipText)
		self.w.threshold.setToolTip(tooltipText)

		self.w.descriptionText2 = vanilla.TextBox("auto", "(Max percentage of widths that may be kerned.)", sizeStyle='small', selectable=True)
		self.w.descriptionText2.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())

		tooltipText = "When fixing overkerns, kerning values are rounded to a multiple of this value."
		self.w.roundingText = vanilla.TextBox("auto", "When fixing, round kerning values by:", sizeStyle='small', selectable=True)
		self.w.rounding = SteppingEditText("auto", "5", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter(1))
		self.w.roundingText.setToolTip(tooltipText)
		self.w.rounding.setToolTip(tooltipText)

		self.w.limitToExportingGlyphs = vanilla.CheckBox("auto", "Limit to exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.limitToExportingGlyphs.setToolTip("Ignore glyphs that are set not to export.")
		self.w.verbose = vanilla.CheckBox("auto", "Verbose reporting (slow)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose.setToolTip("Report every overkerned pair in the Macro Window.")

		tooltipText = "Glyphs and kerning groups whose names contain any of these comma-separated particles are ignored."
		self.w.ignoreText = vanilla.TextBox("auto", "Ignore glyphs containing:", sizeStyle="small", selectable=True)
		self.w.ignore = vanilla.EditText("auto", "fraction, .percent", callback=self.SavePreferences, sizeStyle="small")
		self.w.ignoreText.setToolTip(tooltipText)
		self.w.ignore.setToolTip(tooltipText)

		tooltipText = "Which masters of which fonts to look at."
		self.w.scopeText = vanilla.TextBox("auto", "Apply to:", sizeStyle="small", selectable=True)
		self.w.scope = vanilla.PopUpButton("auto", ("current master of current font", "⚠️ ALL masters of current font", "⚠️ ALL masters of ⚠️ ALL open fonts"), sizeStyle="small", callback=self.SavePreferences)
		self.w.scopeText.setToolTip(tooltipText)
		self.w.scope.setToolTip(tooltipText)

		# Buttons:
		self.w.fixButton = vanilla.Button("auto", "Fix", callback=self.NewTabwithOverkernedPairsMain)
		self.w.fixButton.setToolTip("Rounds overkerned pairs down to the maximum allowed value and opens a tab with the affected pairs.")
		self.w.runButton = vanilla.Button("auto", "Report", callback=self.NewTabwithOverkernedPairsMain)
		self.w.runButton.setToolTip("Opens a tab with the overkerned pairs, without changing any kerning.")
		self.w.setDefaultButton(self.w.runButton)

		# labels: right-aligned, same width
		labelNames = ("thresholdText", "roundingText", "ignoreText", "scopeText")
		widestLabel = "thresholdText"  # the label with the longest text
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[thresholdText]-gap-[threshold(50)]-gap-[thresholdPercent]-(>=inset)-|",
				"H:|-inset-[descriptionText2]-inset-|",
				"H:|-inset-[roundingText]-gap-[rounding(50)]-(>=inset)-|",
				"H:|-inset-[limitToExportingGlyphs]-gap-[verbose]-(>=inset)-|",
				"H:|-inset-[ignoreText]-gap-[ignore]-inset-|",
				"H:|-inset-[scopeText]-gap-[scope]-inset-|",
				"H:|-(>=inset)-[fixButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[threshold]-row-[descriptionText2]-row-[rounding]-row-[limitToExportingGlyphs]-row-[ignore]-row-[scope]-inset-[runButton]-inset-|",
				"V:[fixButton]-inset-|",
				{"view1": self.w.thresholdText, "attribute1": "centerY", "view2": self.w.threshold, "attribute2": "centerY"},
				{"view1": self.w.thresholdPercent, "attribute1": "centerY", "view2": self.w.threshold, "attribute2": "centerY"},
				{"view1": self.w.roundingText, "attribute1": "centerY", "view2": self.w.rounding, "attribute2": "centerY"},
				{"view1": self.w.verbose, "attribute1": "centerY", "view2": self.w.limitToExportingGlyphs, "attribute2": "centerY"},
				{"view1": self.w.ignoreText, "attribute1": "centerY", "view2": self.w.ignore, "attribute2": "centerY"},
				{"view1": self.w.scopeText, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def NewTabwithOverkernedPairsMain(self, sender=None):
		try:
			def glyphNameContainsIgnoredParticle(glyphName, ignoredParticles):
				for particle in ignoredParticles:
					if particle in glyphName:
						return True
				return False

			# clear macro window log:
			Glyphs.clearLog()
			shouldFix = sender == self.w.fixButton

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			if self.pref("scope") < 2:
				theseFonts = (thisFont, )
			else:
				theseFonts = Glyphs.fonts

			thresholdFactor = None
			try:
				thresholdFactor = self.prefFloat("threshold") / 100.0
			except:
				Message(title="Value Error", message="The threshold value you entered is invalid", OKButton="Oops")
				return

			verbose = bool(self.pref("verbose"))
			ignores = [particle.strip() for particle in self.pref("ignore").split(",") if len(particle.strip()) > 0]

			overKernCount = 0
			for thisFont in theseFonts:
				report = reportFontName(thisFont)
				print(f"Overkerned Pairs report for {report}")

				rounding = self.prefInt("rounding")

				if self.pref("scope") > 0:
					theseMasters = thisFont.masters
				else:
					theseMasters = (thisFont.selectedFontMaster, )

				layers = []
				for thisMaster in theseMasters:
					print(f"\n\tⓂ️ Master ‘{thisMaster.name}’")
					masterKerning = thisFont.kerning[thisMaster.id]  # kerning dictionary
					# tabText = ""  # the text appearing in the new tab

					# collect minimum widths for every kerning group:
					leftGroupMinimumWidths = {}
					leftGroupNarrowestGlyphs = {}
					rightGroupMinimumWidths = {}
					rightGroupNarrowestGlyphs = {}
					if self.pref("limitToExportingGlyphs"):
						theseGlyphs = [g for g in thisFont.glyphs if g.export]
					else:
						theseGlyphs = thisFont.glyphs
					for thisGlyph in theseGlyphs:
						if glyphNameContainsIgnoredParticle(thisGlyph.name, ignores):
							continue

						thisLayer = thisGlyph.layers[thisMaster.id]

						# left side of the glyph (= right side of kern pair)
						if thisGlyph.leftKerningGroup:
							if thisGlyph.leftKerningGroup in leftGroupMinimumWidths.keys():
								if thisLayer.width < leftGroupMinimumWidths[thisGlyph.leftKerningGroup]:
									leftGroupMinimumWidths[thisGlyph.leftKerningGroup] = thisLayer.width
									leftGroupNarrowestGlyphs[thisGlyph.leftKerningGroup] = thisGlyph.name
							else:
								leftGroupMinimumWidths[thisGlyph.leftKerningGroup] = thisLayer.width
								leftGroupNarrowestGlyphs[thisGlyph.leftKerningGroup] = thisGlyph.name

						# right side of the glyph (= left side of kern pair)
						if thisGlyph.rightKerningGroup:
							if thisGlyph.rightKerningGroup in rightGroupMinimumWidths.keys():
								if thisLayer.width < rightGroupMinimumWidths[thisGlyph.rightKerningGroup]:
									rightGroupMinimumWidths[thisGlyph.rightKerningGroup] = thisLayer.width
									rightGroupNarrowestGlyphs[thisGlyph.rightKerningGroup] = thisGlyph.name
							else:
								rightGroupMinimumWidths[thisGlyph.rightKerningGroup] = thisLayer.width
								rightGroupNarrowestGlyphs[thisGlyph.rightKerningGroup] = thisGlyph.name

					# go through kern values and collect them in tabText:
					for leftKey in masterKerning.keys():
						if leftKey[0] == "@" and (not leftKey[7:] in rightGroupMinimumWidths.keys() or glyphNameContainsIgnoredParticle(leftKey, ignores)):
							continue
						if leftKey[0] != "@" and glyphNameContainsIgnoredParticle(thisFont.glyphForId_(leftKey).name, ignores):
							continue

						for rightKey in masterKerning[leftKey].keys():
							if rightKey[0] == "@" and (not rightKey[7:] in leftGroupMinimumWidths.keys() or glyphNameContainsIgnoredParticle(rightKey, ignores)):
								continue
							if rightKey[0] != "@" and glyphNameContainsIgnoredParticle(thisFont.glyphForId_(rightKey).name, ignores):
								continue

							kernValue = masterKerning[leftKey][rightKey]
							if kernValue >= 0:
								continue

							leftWidth = None
							rightWidth = None
							try:
								# collect widths for comparison
								if leftKey[0] == "@":
									# leftKey is a group name like "@MMK_L_y"
									groupName = leftKey[7:]
									leftWidth = rightGroupMinimumWidths[groupName]
									leftGlyphName = rightGroupNarrowestGlyphs[groupName]
								else:
									# leftKey is a glyph ID like "59B740DA-A4F4-43DF-B6DD-1DFA213FFFE7"
									leftGlyph = thisFont.glyphForId_(leftKey)
									if not leftGlyph:
										continue
									# exclude if non-exporting and user limited to exporting glyphs:
									if self.pref("limitToExportingGlyphs") and not leftGlyph.export:
										continue
									leftWidth = leftGlyph.layers[thisMaster.id].width
									leftGlyphName = leftGlyph.name

								if rightKey[0] == "@":
									# rightKey is a group name like "@MMK_R_y"
									groupName = rightKey[7:]
									rightWidth = leftGroupMinimumWidths[groupName]
									rightGlyphName = leftGroupNarrowestGlyphs[groupName]
								else:
									# rightKey is a glyph ID like "59B740DA-A4F4-43DF-B6DD-1DFA213FFFE7"
									rightGlyph = thisFont.glyphForId_(rightKey)
									if not rightGlyph:
										continue
									# exclude if non-exporting and user limited to exporting glyphs:
									if self.pref("limitToExportingGlyphs") and not rightGlyph.export:
										continue
									rightWidth = rightGlyph.layers[thisMaster.id].width
									rightGlyphName = rightGlyph.name

								# possibly update the value, considering exceptions:
								# (this eliminates false positives)
								kernValueException = thisFont.kerningForPair(thisMaster.id, leftGlyphName, rightGlyphName)
								if kernValueException is not None:
									kernValue = kernValueException
									# note: for class kerning, we are only checking the narrowest glyph-glyph pair.
									#       if this pair has overkerning that is fixed via an exception
									#       we might miss overkerned glyph-glyph pairs covered by the class kerning pair.
									# TODO: to be really correct and complete, we need to check all possible glyph-glyph pairs
									#       considering exceptions.
									#       however, this would mean we may generate warnings
									#       for pairs that practically do not occur in real life.

								# compare widths and collect overkern if it is one:
								minAllowedKernValue = - thresholdFactor * min(leftWidth, rightWidth)
								if kernValue < minAllowedKernValue:
									overKernCount += 1
									layers.append(thisFont.glyphs[leftGlyphName].layers[thisMaster.id])
									layers.append(thisFont.glyphs[rightGlyphName].layers[thisMaster.id])
									if verbose:
										print(f"\tOverkern: {leftGlyphName} ↔️ {rightGlyphName} ({kernValue:.0f} vs. min {minAllowedKernValue:.1f})")
									if thisFont.glyphs["space"]:
										layers.append(thisFont.glyphs["space"].layers[thisMaster.id])
									if shouldFix:
										masterKerning[leftKey][rightKey] = -roundedDownBy(-minAllowedKernValue, rounding)

							except Exception as e:
								# probably a kerning group name found in the kerning data, but no glyph assigned to it:
								# brings macro window to front and reports warning:
								print("*", e)
								import traceback
								errormsg = traceback.format_exc()
								print(errormsg)
								for side in ("left", "right"):
									if side not in errormsg.lower():
										print(
											f"⚠️ Warning: The {side} group ‘{groupName}’ found in your kerning data does not appear in any glyph. Clean up your kerning, and run the script again."
										)
										Glyphs.showMacroWindow()

					if layers:
						layers.append(newLineControlLayer())
				if layers:
					if not (thisFont.currentTab and layers == thisFont.currentTab.layers):
						tab = thisFont.newTab()
						tab.layers = layers

				print()

			message = ""
			if overKernCount > 0:
				message = "%s %i overkerns in %i font%s." % (
					"Fixed" if shouldFix else "Found",
					overKernCount,
					len(theseFonts),
					"" if len(theseFonts) == 1 else "s",
				)
				Message(
					title="Found Overkerns",
					message=message,
					OKButton=None,
				)
			else:
				message = "Could not find any kern pairs beyond the threshold."
				Message(
					title="No Overkerns Found",
					message=message,
					OKButton="🫶Phew!",
				)

			print(f"✅ Done. {message}")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"New Tab with Overkerned Pairs Error: {e}")
			import traceback
			print(traceback.format_exc())


NewTabwithOverkernedPairs()
