# MenuTitle: Remove Small Kerning Pairs
__doc__ = """
Specify a kerning value, and every kerning in the current master smaller than that will be removed.
"""

import objc
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def nameForID(font, ID):
	"""Return the name of a group or glyph for a given kerning ID."""
	if ID.startswith("@"):  # is a group
		return ID
	return font.glyphForId_(ID).name


class DeleteSmallKerningPairs(mekkaObject):
	prefDict = {
		"howMuch": 10,
		"positive": True,
		"zero": False,
		"negative": True,
		"glyphToGlyph": True,
		"glyphToClass": True,
		"classToClass": True,
		"countPairs": True,
		"removeOnMasters": 0,
	}

	def __init__(self):
		windowWidth = 350
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Remove Small Kerning Pairs",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.textHowMuch = vanilla.TextBox("auto", "Delete pairs smaller than:")
		formatter = NSNumberFormatter.alloc().init()
		formatter.setAllowsFloats_(False)
		formatter.setMinimum_(1)
		self.w.howMuch = SteppingEditText("auto", "10", callback=self.SavePreferences, formatter=formatter)
		tooltip = "Kerning pairs with an absolute value smaller than this will be removed."
		self.w.textHowMuch.setToolTip(tooltip)
		self.w.howMuch.setToolTip(tooltip)

		self.w.textScope = vanilla.TextBox("auto", "Scope:", sizeStyle="small")
		self.w.textScope.setToolTip("Which kinds of pairs may be removed.")
		self.w.positive = vanilla.CheckBox("auto", "Positive,", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.positive.setToolTip("Remove positive pairs smaller than the value.")
		self.w.zero = vanilla.CheckBox("auto", "zero, and", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.zero.setToolTip("Remove pairs with a value of zero.")
		self.w.negative = vanilla.CheckBox("auto", "negative pairs", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.negative.setToolTip("Remove negative pairs smaller (in absolute value) than the value.")
		self.w.glyphToGlyph = vanilla.CheckBox("auto", "Glyph-glyph", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.glyphToGlyph.setToolTip("Include pairs between two glyphs.")
		self.w.glyphToClass = vanilla.CheckBox("auto", "Glyph-group", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.glyphToClass.setToolTip("Include pairs between a glyph and a group.")
		self.w.classToClass = vanilla.CheckBox("auto", "Group-group", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.classToClass.setToolTip("Include pairs between two groups.")

		tooltip = "Where to remove the pairs."
		self.w.removeOnMastersText = vanilla.TextBox("auto", "Remove on:", sizeStyle="small", selectable=True)
		self.w.removeOnMasters = vanilla.PopUpButton(
			"auto",
			("current master", "⚠️ all masters of current font", "⚠️ all masters of ⚠️ all open fonts"),
			sizeStyle="small",
			callback=self.SavePreferences,
		)
		self.w.removeOnMastersText.setToolTip(tooltip)
		self.w.removeOnMasters.setToolTip(tooltip)

		tooltip = "Count the affected pairs (may be slow in large fonts)."
		self.w.countPairs = vanilla.CheckBox("auto", "Will remove:", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.statusText = vanilla.TextBox("auto", "–", sizeStyle="small")
		self.w.countPairs.setToolTip(tooltip)
		self.w.statusText.setToolTip("Number of pairs the Remove button would delete right now.")

		self.w.nextMasterButton = vanilla.Button("auto", "Next Master", callback=self.selectNextMaster)
		self.w.nextMasterButton.setToolTip("Switch the frontmost font to its next master.")
		self.w.runButton = vanilla.Button("auto", "Remove", callback=self.DeleteSmallKerningPairsMain)
		self.w.runButton.setToolTip("Remove the matching pairs.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hugging makes the window as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels hug their text, the fields take the leftover width
		for labelName in ("textHowMuch", "removeOnMastersText"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(750, NSLayoutConstraintOrientationHorizontal)
		self.w.countPairs.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.removeOnMasters.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		columnRules = [
			{"view1": self.w.glyphToGlyph, "attribute1": "width", "view2": self.w.positive, "attribute2": "width"},
			{"view1": self.w.glyphToClass, "attribute1": "width", "view2": self.w.zero, "attribute2": "width"},
			{"view1": self.w.classToClass, "attribute1": "width", "view2": self.w.negative, "attribute2": "width"},
		]
		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[textHowMuch]-gap-[howMuch(60)]-(>=inset)-|",
				"H:|-inset-[textScope]-(>=inset)-|",
				"H:|-inset-[positive]-gap-[zero]-gap-[negative]-(>=inset)-|",
				"H:|-inset-[glyphToGlyph]-gap-[glyphToClass]-gap-[classToClass]-(>=inset)-|",
				"H:|-inset-[countPairs]-gap-[statusText]-(>=inset)-|",
				"H:|-inset-[removeOnMastersText]-gap-[removeOnMasters]-inset-|",
				"H:|-inset-[nextMasterButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[howMuch]-row-[textScope]-row-[positive]-stackRow-[glyphToGlyph]-row-[removeOnMasters]-row-[countPairs]-inset-[runButton]-inset-|",
				"V:[nextMasterButton]-inset-|",
				{"view1": self.w.textHowMuch, "attribute1": "centerY", "view2": self.w.howMuch, "attribute2": "centerY"},
				{"view1": self.w.zero, "attribute1": "centerY", "view2": self.w.positive, "attribute2": "centerY"},
				{"view1": self.w.negative, "attribute1": "centerY", "view2": self.w.positive, "attribute2": "centerY"},
				{"view1": self.w.glyphToClass, "attribute1": "centerY", "view2": self.w.glyphToGlyph, "attribute2": "centerY"},
				{"view1": self.w.classToClass, "attribute1": "centerY", "view2": self.w.glyphToGlyph, "attribute2": "centerY"},
				{"view1": self.w.statusText, "attribute1": "centerY", "view2": self.w.countPairs, "attribute2": "centerY"},
				{"view1": self.w.removeOnMastersText, "attribute1": "centerY", "view2": self.w.removeOnMasters, "attribute2": "centerY"},
			] + columnRules,
			metrics={"inset": inset, "gap": 8, "row": 8, "stackRow": 5},
		)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		anyValue = self.prefBool("positive") or self.prefBool("zero") or self.prefBool("negative")
		anyKind = self.prefBool("glyphToGlyph") or self.prefBool("glyphToClass") or self.prefBool("classToClass")
		self.w.runButton.enable(anyValue and anyKind)

		countEnabled = self.prefBool("countPairs")
		self.w.statusText.getNSTextField().setEnabled_(countEnabled)
		if countEnabled and anyValue and anyKind:
			total = sum(len(self.pairsToRemove(font, master)[0]) for font, master in self.fontsAndMasters())
			self.w.statusText.set("%i pair%s" % (total, "" if total == 1 else "s"))
		else:
			self.w.statusText.set("–")

	def fontsAndMasters(self):
		"""Yield (font, master) tuples according to the ‘Remove on’ popup."""
		removeOn = self.prefInt("removeOnMasters")
		if removeOn == 2:
			fonts = tuple(Glyphs.fonts)
		else:
			fonts = (Glyphs.font, ) if Glyphs.font else ()
		for font in fonts:
			for master in font.masters:
				if removeOn > 0 or master == font.selectedFontMaster:
					yield font, master

	def pairsToRemove(self, font, master):
		"""Return ((leftName, rightName) pairs, negativeCount, zeroCount, positiveCount) for a master."""
		removePositive = self.prefBool("positive")
		removeZero = self.prefBool("zero")
		removeNegative = self.prefBool("negative")
		removeGlyphToGlyph = self.prefBool("glyphToGlyph")
		removeGlyphToClass = self.prefBool("glyphToClass")
		removeClassToClass = self.prefBool("classToClass")
		maxKernValue = abs(self.prefInt("howMuch"))

		pairs = []
		countZero = countPositive = countNegative = 0
		kernDict = font.kerning[master.id]
		if not kernDict:
			return pairs, countNegative, countZero, countPositive
		for leftID in kernDict.keys():
			for rightID in kernDict[leftID].keys():
				countClasses = int(leftID.startswith("@")) + int(rightID.startswith("@"))
				if (removeGlyphToGlyph and countClasses == 0) or \
					(removeGlyphToClass and countClasses == 1) or \
					(removeClassToClass and countClasses == 2):
					kerningValue = kernDict[leftID][rightID]
					if removeZero and kerningValue == 0.0:
						countZero += 1
					elif removePositive and 0.0 < kerningValue < maxKernValue:
						countPositive += 1
					elif removeNegative and 0.0 > kerningValue > -maxKernValue:
						countNegative += 1
					else:
						continue
					pairs.append((nameForID(font, leftID), nameForID(font, rightID)))
		return pairs, countNegative, countZero, countPositive

	def selectNextMaster(self, sender=None):
		try:
			thisFont = Glyphs.font
			if not thisFont:
				print("Next Master: No font open.")
				return
			masterCount = len(thisFont.masters)
			if masterCount < 2:
				print("Next Master: %s has only one master." % thisFont.familyName)
				return
			nextIndex = (thisFont.masterIndex + 1) % masterCount
			thisFont.masterIndex = nextIndex
			print("Switched to master: %s" % thisFont.masters[nextIndex].name)
			self.updateUI()
		except Exception as e:
			Glyphs.showMacroWindow()
			print("Next Master Error: %s" % e)

	def DeleteSmallKerningPairsMain(self, sender):
		try:
			self.SavePreferences()
			Glyphs.showMacroWindow()

			maxKernValue = abs(self.prefInt("howMuch"))
			removeZeroOnly = self.prefBool("zero") and not self.prefBool("negative") and not self.prefBool("positive")
			willRemove = "zero kernings" if removeZeroOnly else "kernings smaller than %i" % maxKernValue

			fontsAndMasters = tuple(self.fontsAndMasters())
			if not fontsAndMasters:
				print("Note: No font open.")
			for thisFont, thisFontMaster in fontsAndMasters:
				print("Deleting %s in %s %s..." % (willRemove, thisFont.familyName, thisFontMaster.name))
				pairs, countNegative, countZero, countPositive = self.pairsToRemove(thisFont, thisFontMaster)
				thisFont.disableUpdateInterface()
				try:
					for leftSide, rightSide in pairs:
						thisFont.removeKerningForPair(thisFontMaster.id, leftSide, rightSide)
				finally:
					thisFont.enableUpdateInterface()
				print("   Removed %i kerning pairs:" % len(pairs))
				print("   %i negative pairs" % countNegative)
				print("   %i zero pairs" % countZero)
				print("   %i positive pairs" % countPositive)
			print("Done.")
			Glyphs.showNotification("Remove Small Kerning Pairs", "Done. Details in Macro Window.")
			self.updateUI()
		except Exception as e:
			Glyphs.showMacroWindow()
			print("Delete Small Kerning Pairs Error: %s" % e)


# clear macro window log:
Glyphs.clearLog()

# execute GUI:
DeleteSmallKerningPairs()
