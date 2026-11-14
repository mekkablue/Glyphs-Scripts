# MenuTitle: Exception Cleaner
__doc__ = """
Removes kerning exceptions (glyph-to-glyph, glyph-to-group and group-to-glyph pairs) in the current master, all masters of the current font, or all masters of all open fonts. Optionally only those that differ less than a threshold from the group kerning they would fall back to. Group-to-group kerning is never touched.
"""

import objc
import vanilla
from mekkablue import mekkaObject, reportFontName
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSBeep,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
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


class DeleteExceptionsTooCloseToGroupKerning(mekkaObject):
	prefDict = {
		"glyphGlyph": True,
		"glyphGroup": True,
		"groupGlyph": True,
		"keepGrouplessKerning": False,
		"onlyBelowThreshold": True,
		"threshold": 10,
		"removeOnMasters": 0,
		"countPairs": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Exception Cleaner",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		# Which kinds of exceptions:
		self.w.glyphGlyph = vanilla.CheckBox("auto", "Remove 🅰️🅰️ glyph-to-glyph pairs", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.glyphGlyph.setToolTip("Remove kerning pairs between two glyphs, e.g., ‘A’ and ‘V’.")
		self.w.glyphGroup = vanilla.CheckBox("auto", "Remove 🅰️🔠 glyph-to-group pairs", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.glyphGroup.setToolTip("Remove kerning pairs between a glyph on the left and a group on the right.")
		self.w.groupGlyph = vanilla.CheckBox("auto", "Remove 🔠🅰️ group-to-glyph pairs", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.groupGlyph.setToolTip("Remove kerning pairs between a group on the left and a glyph on the right.")
		self.w.keepGrouplessKerning = vanilla.CheckBox("auto", "Keep kerning for groupless glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.keepGrouplessKerning.setToolTip("Glyphs without a kerning group on the relevant side have nothing to fall back to. If enabled, their pairs are kept.")

		# Scope:
		self.w.scopeText = vanilla.TextBox("auto", "Scope:", sizeStyle="small", selectable=True)
		self.w.scopeText.setToolTip("Which of the exceptions above are removed, and where.")

		self.w.onlyBelowThreshold = vanilla.CheckBox("auto", "Only if difference to group kerning below:", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.onlyBelowThreshold.setToolTip(
			"If enabled, an exception is only removed if it is less than the threshold value away from its corresponding group-to-group kerning, i.e., if it is insignificant. Exceptions of glyphs without groups cannot be compared and are kept. If disabled, all exceptions of the checked kinds are removed."
		)
		self.w.threshold = SteppingEditText("auto", "10", callback=self.SavePreferences, sizeStyle="small", formatter=integerFormatter(0))
		self.w.threshold.setToolTip("An exception must be at least this number of units different from its corresponding group kern pair, otherwise it will be removed.")

		self.w.removeOnMastersText = vanilla.TextBox("auto", "Remove in:", sizeStyle="small", selectable=True)
		self.w.removeOnMasters = vanilla.PopUpButton(
			"auto",
			("current master", "⚠️ all masters of current font", "⚠️ all masters of ⚠️ all open fonts"),
			sizeStyle="small",
			callback=self.SavePreferences,
		)
		tooltipText = "Where to remove the exceptions: in the current master only, in all masters of the frontmost font, or in all masters of all open fonts."
		self.w.removeOnMastersText.setToolTip(tooltipText)
		self.w.removeOnMasters.setToolTip(tooltipText)

		# Prediction:
		self.w.countPairs = vanilla.CheckBox("auto", "Prediction:", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.countPairs.setToolTip("Count the exceptions that would be removed with the current settings (may be slow in large fonts).")
		self.w.statusText = vanilla.TextBox("auto", "will remove – pairs.", sizeStyle="small")
		self.w.statusText.setToolTip("Number of kerning pairs the Clean button would remove right now.")

		# Buttons:
		self.w.nextMasterButton = vanilla.Button("auto", "Next Master", callback=self.NextMaster)
		self.w.nextMasterButton.setToolTip("Switches the frontmost font to its next master, so you can clean master after master.")
		self.w.runButton = vanilla.Button("auto", "Clean", callback=self.DeleteExceptionsTooCloseToGroupKerningMain)
		self.w.runButton.setToolTip("Removes the exceptions as set above. If the button is greyed out, check at least one kind of exception.")
		self.w.setDefaultButton(self.w.runButton)

		# the checkbox hugs its text, so the stepping field sits right behind it; the popup takes the leftover width
		self.w.onlyBelowThreshold.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.countPairs.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.removeOnMastersText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.removeOnMasters.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[glyphGlyph]-(>=inset)-|",
				"H:|-inset-[glyphGroup]-(>=inset)-|",
				"H:|-inset-[groupGlyph]-(>=inset)-|",
				"H:|-inset-[keepGrouplessKerning]-(>=inset)-|",
				"H:|-inset-[scopeText]-(>=inset)-|",
				"H:|-inset-[onlyBelowThreshold]-gap-[threshold(50)]-(>=inset)-|",
				"H:|-inset-[removeOnMastersText]-gap-[removeOnMasters]-inset-|",
				"H:|-inset-[countPairs]-gap-[statusText]-(>=inset)-|",
				"H:|-inset-[nextMasterButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[glyphGlyph]-checkRow-[glyphGroup]-checkRow-[groupGlyph]-checkRow-[keepGrouplessKerning]-section-[scopeText]-titleGap-[onlyBelowThreshold]-tallRow-[removeOnMasters]-tallRow-[countPairs]-inset-[runButton]-inset-|",
				{"view1": self.w.threshold, "attribute1": "centerY", "view2": self.w.onlyBelowThreshold, "attribute2": "centerY"},
				{"view1": self.w.removeOnMastersText, "attribute1": "centerY", "view2": self.w.removeOnMasters, "attribute2": "centerY"},
				{"view1": self.w.statusText, "attribute1": "centerY", "view2": self.w.countPairs, "attribute2": "centerY"},
				{"view1": self.w.nextMasterButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "checkRow": 5, "section": 12, "titleGap": 2, "tallRow": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def NextMaster(self, sender=None):
		thisFont = Glyphs.font
		if thisFont:
			thisFont.masterIndex = (thisFont.masterIndex + 1) % len(thisFont.masters)
			self.updateUI()
		else:
			NSBeep()

	def updateUI(self, sender=None):
		self.w.threshold.enable(self.w.onlyBelowThreshold.get())
		anyKindIsSelected = self.w.glyphGlyph.get() or self.w.glyphGroup.get() or self.w.groupGlyph.get()
		self.w.runButton.enable(bool(anyKindIsSelected))

		countEnabled = self.prefBool("countPairs")
		self.w.statusText.getNSTextField().setEnabled_(countEnabled)
		if countEnabled and anyKindIsSelected:
			total = sum(
				len(self.exceptionsToRemove(font, master, verbose=False))
				for font in self.fontsToProcess()
				for master in self.mastersToProcess(font)
			)
			self.w.statusText.set(f"will remove {total} pair{'' if total == 1 else 's'}.")
		else:
			self.w.statusText.set("will remove – pairs.")

	def fontsToProcess(self):
		"""The fonts to clean, according to the ‘Remove in’ popup."""
		if self.prefInt("removeOnMasters") == 2:
			return tuple(Glyphs.fonts)
		return (Glyphs.font, ) if Glyphs.font else ()

	def mastersToProcess(self, font):
		"""The masters of a font to clean, according to the ‘Remove in’ popup."""
		if self.prefInt("removeOnMasters") >= 1:
			return tuple(font.masters)
		return (font.selectedFontMaster, )

	def exceptionsToRemove(self, font, master, verbose=True):
		"""Returns (left, right, report) tuples for the exceptions to remove in this master. Left and right are as removeKerningForPair() takes them."""
		kerning = font.kerning[master.id]
		if not kerning:
			return []

		removeGlyphGlyph = self.prefBool("glyphGlyph")
		removeGlyphGroup = self.prefBool("glyphGroup")
		removeGroupGlyph = self.prefBool("groupGlyph")
		keepGrouplessKerning = self.prefBool("keepGrouplessKerning")
		onlyBelowThreshold = self.prefBool("onlyBelowThreshold")
		threshold = self.prefInt("threshold")

		pairs = []
		for leftSide in list(kerning.keys()):
			leftIsGlyph = not leftSide.startswith("@")
			leftGlyph = font.glyphForId_(leftSide) if leftIsGlyph else None
			if leftIsGlyph and leftGlyph is None:
				if verbose:
					print(f"\t⚠️ Could not find glyph for ID {leftSide}, consider cleaning up kerning.")
				continue
			if leftIsGlyph:
				leftGroupKey = f"@MMK_L_{leftGlyph.rightKerningGroup}" if leftGlyph.rightKerningGroup else None
				leftName = leftGlyph.name
			else:
				leftGroupKey = leftSide
				leftName = leftSide
			leftMayBeRemoved = not (leftIsGlyph and leftGroupKey is None and keepGrouplessKerning)

			for rightSide in list(kerning[leftSide].keys()):
				rightIsGlyph = not rightSide.startswith("@")
				rightGlyph = font.glyphForId_(rightSide) if rightIsGlyph else None
				if rightIsGlyph and rightGlyph is None:
					if verbose:
						print(f"\t⚠️ Could not find glyph for ID {rightSide}, consider cleaning up kerning.")
					continue
				if rightIsGlyph:
					rightGroupKey = f"@MMK_R_{rightGlyph.leftKerningGroup}" if rightGlyph.leftKerningGroup else None
					rightName = rightGlyph.name
				else:
					rightGroupKey = rightSide
					rightName = rightSide
				rightMayBeRemoved = not (rightIsGlyph and rightGroupKey is None and keepGrouplessKerning)

				if leftIsGlyph and rightIsGlyph:
					shouldRemove = removeGlyphGlyph and leftMayBeRemoved and rightMayBeRemoved
				elif leftIsGlyph:
					shouldRemove = removeGlyphGroup and leftMayBeRemoved
				elif rightIsGlyph:
					shouldRemove = removeGroupGlyph and rightMayBeRemoved
				else:
					continue  # group-to-group kerning is never removed
				if not shouldRemove:
					continue

				exceptionValue = kerning[leftSide][rightSide]
				report = f"{leftName}-{rightName}: {exceptionValue:g}"
				if onlyBelowThreshold:
					if leftGroupKey is None or rightGroupKey is None:
						continue  # no group to compare with
					groupValue = font.kerningForPair(master.id, leftGroupKey, rightGroupKey)
					if groupValue is None or groupValue > 100000:  # NSNotFound
						groupValue = 0
					if abs(exceptionValue - groupValue) >= threshold:
						continue
					report += f" vs. {leftGroupKey}-{rightGroupKey}: {groupValue:g}"
				pairs.append((leftName, rightName, report))
		return pairs

	def DeleteExceptionsTooCloseToGroupKerningMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			font = Glyphs.font  # frontmost font
			if font is None:
				Message(title="No Font Open", message="The script requires at least one font. Open a font and run the script again.", OKButton=None)
				return

			fonts = self.fontsToProcess()

			print("Exception Cleaner Report\n")
			totalCount = 0
			for thisFont in fonts:
				print(f"Font: {reportFontName(thisFont)}")
				for thisMaster in self.mastersToProcess(thisFont):
					pairs = self.exceptionsToRemove(thisFont, thisMaster)
					print(f"\n🚫 Master ‘{thisMaster.name}’: removing {len(pairs)} exception{'' if len(pairs) == 1 else 's'}")
					for left, right, report in pairs:
						print(f"\t✅ {report}")
						thisFont.removeKerningForPair(thisMaster.id, left, right)
					totalCount += len(pairs)
				print()

			# Final report:
			Glyphs.showNotification(
				f"Removed {totalCount} exception{'' if totalCount == 1 else 's'}",
				f"Processed {len(fonts)} font{'' if len(fonts) == 1 else 's'}. Details in Macro Window.",
			)
			print("✅ Done.")
			self.updateUI()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Exception Cleaner Error: {e}")
			import traceback
			print(traceback.format_exc())


DeleteExceptionsTooCloseToGroupKerning()
