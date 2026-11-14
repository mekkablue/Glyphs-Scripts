# MenuTitle: Auto Bumper
__doc__ = """
Specify a minimum distance, left and right glyphs, and Auto Bumper will add the minimum necessary kerning for the current master (or more masters and fonts, see Scope) and open a tab with the bumped pairs.
"""

import vanilla
from mekkablue import mekkaObject, reportTimeInNaturalLanguage
from timeit import default_timer as timer
from kernanalysis import intervalList, minDistanceBetweenTwoLayers, sortedIntervalsFromString, stringToListOfGlyphsForFont, effectiveKerning, distanceFromEntry, bubbleLayer
from AppKit import NSColor, NSTextAlignmentLeft, NSTextAlignmentRight, NSWindowStyleMaskResizable, NSSize, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message

defaultStrings = """

iíĭǐîïịìỉīįĩjĵ
ÍǏÎÏİÌỈĪĨ  # UPPERCASE
/iacute.sc/icaron.sc/icircumflex.sc/idieresis.sc/idotaccent.sc/igrave.sc/ihookabove.sc/imacron.sc/itilde.sc
FTKVWY  # TOP RIGHT
f
ÐĦðđħ/Lslash/lslash
bhlkþ
rtkvwxyz

ĄĘĮ  # OGONEK
gjpy  # DESCENDER

AKLRXZ  # BOTTOM RIGHT
sxz  # BOTTOM LEFT

abcdefghijklmnopqrstuvwxyzßð
ABCDEFGHIJKLMNOPQRSTUVWXYZẞÞ
/a.sc/b.sc/c.sc/d.sc/e.sc/f.sc/g.sc/h.sc/i.sc/j.sc/k.sc/l.sc/m.sc/n.sc/o.sc/p.sc/q.sc/r.sc/s.sc/t.sc/u.sc/v.sc/w.sc/x.sc/y.sc/z.sc/germandbls.sc/thorn.sc

({[„“”«»¿¡/slash
„“”]})*®?!»«/slash
/parenleft.sc/braceleft.sc/bracketleft.sc
/parenright.sc/braceright.sc/bracketright.sc

/Ohorn/Uhorn #VIETNAMESE
/ohorn/uhorn #VIETNAMESE
/ohorn.sc/uhorn.sc #VIETNAMESE
/i/iacute/idotbelow/igrave/ihookabove/itilde #VIETNAMESE
/i.sc/iacute.sc/idotbelow.sc/igrave.sc/ihookabove.sc/itilde.sc #VIETNAMESE

»«‹›/quotesinglbase/quotedblbase/quotedblleft/quotedblright/quoteleft/quoteright/quotedbl/quotesingle

/lcaron/dcaron/tcaron #CZECH AND SLOVAK
ňčěšäížůô #CZECH AND SLOVAK EXCEPTIONS
"“”]})*?!»« #CZECH AND SLOVAK GROUPS

/a.sc/aogonek.sc/ae.sc/b.sc/c.sc/d.sc/e.sc/f.sc/g.sc/h.sc/i.sc/j.sc/k.sc/l.sc/m.sc/n.sc/eng.sc/o.sc/oe.sc/p.sc/thorn.sc/q.sc/r.sc/s.sc/germandbls.sc/t.sc/u.sc/v.sc/w.sc/x.sc/y.sc/z.sc
/slash
/iacute.sc/icaron.sc/icircumflex.sc/idieresis.sc/idotaccent.sc/igrave.sc/imacron.sc/iogonek.sc/itilde.sc/icaron.sc

"""

scopeChoices = (
	"Current master",
	"⚠️ All masters of frontmost font",
	"⚠️ Current masters of all open fonts",
	"⚠️ All masters of all open fonts",
)


class Bumper(mekkaObject):
	prefDict = {
		"popupScope": 0,
		"leftGlyphs": "TVWY",
		"leftIsGroups": 1,
		"rightGlyphs": "iíĭǐîïịìỉīįĩjĵ",
		"rightIsGroups": 0,
		"suffix": "",
		"speedPopup": 2,
		"minDistance": 50,
		"maxDistance": 200,
		"roundFactor": 10,
		"bubbleOffset": "",
		"ignoreIntervals": "",
		"keepExistingKerning": 1,
		"resetExceptionsForGroups": 1,
		"excludeNonExporting": 1,
		"avoidZeroKerning": 1,
		"reportInMacroWindow": 0,
		"reuseCurrentTab": 1,
		"kernStrings": defaultStrings,
	}

	def __init__(self):
		# state for Undo (None as long as there is nothing to undo; otherwise a list of the pairs we touched):
		self.undoSteps = None

		# Window 'self.w':
		windowWidth = 520
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Auto Bumper",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Add kerning for glyph pairs in the chosen scope, and open a tab with the bumped pairs", sizeStyle='small')

		self.w.textScope = vanilla.TextBox("auto", "Scope", sizeStyle='small')
		self.w.popupScope = vanilla.PopUpButton("auto", scopeChoices, callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "Which masters to add kerning to. Whatever you choose, each font gets at most one tab with the bumped pairs (opened, or reused, if ‘Reuse current tab’ is on)."
		self.w.textScope.setToolTip(tooltipText)
		self.w.popupScope.setToolTip(tooltipText)

		glyphsTooltip = "You can type the character ‘é’ or the slash-escaped glyph name ‘/eacute’. Or specify a category after an at sign ‘@Letter’, add a subcategory after a colon ‘@Letter:Lowercase’.\nAdd default strings in the text box at the bottom of the window. Expand the window at the bottom to access it."

		self.w.text_left = vanilla.TextBox("auto", "Left glyphs", sizeStyle='small')
		self.w.leftGlyphs = vanilla.ComboBox("auto", self.kernStringList(self), callback=self.sideGlyphsAction, sizeStyle='small')
		tooltipText = "Measures the specified glyphs from their right side to the following glyph. " + glyphsTooltip
		self.w.text_left.setToolTip(tooltipText)
		self.w.leftGlyphs.setToolTip(tooltipText)
		self.w.leftIsGroups = vanilla.CheckBox("auto", "As groups", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.leftIsGroups.setToolTip("If on, will measure only the specified glyph, but set the calculated kerning for the whole right group of the glyph (i.e., add group kerning). If off, will set the kerning for the glyph only (i.e., add an exception).")
		self.w.swapButton = vanilla.SquareButton("auto", "⇅", callback=self.swap, sizeStyle='small')
		self.w.swapButton.setToolTip("Swaps the left and right glyphs, including their ‘As groups’ settings.")

		self.w.text_right = vanilla.TextBox("auto", "Right glyphs", sizeStyle='small')
		self.w.rightGlyphs = vanilla.ComboBox("auto", self.kernStringList(self), callback=self.sideGlyphsAction, sizeStyle='small')
		tooltipText = "Measures from the previous glyphs to the specified glyphs to their left side. " + glyphsTooltip
		self.w.text_right.setToolTip(tooltipText)
		self.w.rightGlyphs.setToolTip(tooltipText)
		self.w.rightIsGroups = vanilla.CheckBox("auto", "As groups", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.rightIsGroups.setToolTip("If on, will measure only the specified glyph, but set the calculated kerning for the whole left group of the glyph (i.e., add group kerning). If off, will set the kerning for the glyph only (i.e., add an exception).")

		self.w.suffixText = vanilla.TextBox("auto", "Add suffix", sizeStyle='small', selectable=True)
		self.w.suffix = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "Looks for the suffixed version of the listed glyphs, with this suffix added to the name. Useful with .sc for smallcaps. Enter WITH the leading dot for dot suffixes. Can also be used with 'superior' for figures."
		self.w.suffixText.setToolTip(tooltipText)
		self.w.suffix.setToolTip(tooltipText)

		self.w.text_speed = vanilla.TextBox("auto", "Speed", sizeStyle='small')
		self.w.speedPopup = vanilla.PopUpButton("auto", ("very slow", "slow", "medium", "fast", "very fast"), callback=self.SavePreferences, sizeStyle='small')
		self.w.text_speedExplanation = vanilla.TextBox("auto", "", sizeStyle='small')
		tooltipText = "Specifies the number of measurements. Measuring is processor-intensive and can take a while. Slow: many measurements, fast: few measurements."
		self.w.text_speed.setToolTip(tooltipText)
		self.w.speedPopup.setToolTip(tooltipText)
		self.w.text_speedExplanation.setToolTip(tooltipText)

		self.w.text_minDistance = vanilla.TextBox("auto", "Min dist", sizeStyle='small')
		self.w.minDistance = vanilla.EditText("auto", "50", sizeStyle='small', callback=self.SavePreferences)
		self.w.minDistance.getNSTextField().setPlaceholderString_("50")
		tooltipText = "Adds kerning if the shortest distance between two glyphs is shorter than specified value. You can also type ‘vw’ for the distance between v and w, and ‘vw+10’ for that distance plus 10 units. Leave blank or set to zero to ignore."
		self.w.text_minDistance.setToolTip(tooltipText)
		self.w.minDistance.setToolTip(tooltipText)
		self.w.text_maxDistance = vanilla.TextBox("auto", "Max dist", sizeStyle='small')
		self.w.maxDistance = vanilla.EditText("auto", "200", sizeStyle='small', callback=self.SavePreferences)
		self.w.maxDistance.getNSTextField().setPlaceholderString_("200")
		tooltipText = "Adds kerning if the shortest distance between two glyphs is larger than specified value. You can also type ‘AV’ for the distance between A and V, and ‘AV-10’ for that distance minus 10 units. Leave blank or set to zero to ignore."
		self.w.text_maxDistance.setToolTip(tooltipText)
		self.w.maxDistance.setToolTip(tooltipText)
		self.w.text_roundFactor = vanilla.TextBox("auto", "Round by", sizeStyle='small')
		self.w.roundFactor = vanilla.EditText("auto", "10", sizeStyle='small', callback=self.SavePreferences)
		self.w.roundFactor.getNSTextField().setPlaceholderString_("10")
		tooltipText = "Rounds calculated kerning. Leave blank or set to zero to ignore."
		self.w.text_roundFactor.setToolTip(tooltipText)
		self.w.roundFactor.setToolTip(tooltipText)
		self.w.text_bubble = vanilla.TextBox("auto", "Bubble", sizeStyle='small')
		self.w.bubbleOffset = vanilla.EditText("auto", "", sizeStyle='small', callback=self.SavePreferences)
		self.w.bubbleOffset.getNSTextField().setPlaceholderString_("none")
		tooltipText = "If set to a number (0 is valid), uses convex-hull bubble shapes instead of actual glyph outlines for measuring distances. The value is an outward offset in units: 0 = exact convex hull, positive values expand the hull outward."
		self.w.text_bubble.setToolTip(tooltipText)
		self.w.bubbleOffset.setToolTip(tooltipText)

		self.w.text_ignoreIntervals = vanilla.TextBox("auto", "Skip heights", sizeStyle='small')
		self.w.ignoreIntervals = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreIntervals.getNSTextField().setPlaceholderString_("200:300, 400:370, -200:-150")
		tooltipText = "Ignore height intervals: does not measure on y coordinates in intervals specified as y1:y2. Separate multiple intervals with commas. You can also specify glyph names, e.g. x:o (from bottom of x to top of o)."
		self.w.text_ignoreIntervals.setToolTip(tooltipText)
		self.w.ignoreIntervals.setToolTip(tooltipText)

		self.w.keepExistingKerning = vanilla.CheckBox("auto", "Keep (don’t overwrite) existing kerning", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.keepExistingKerning.setToolTip("If the kern pair already exists in the font, it will not be overwritten.")
		self.w.resetExceptionsForGroups = vanilla.CheckBox("auto", "Delete exceptions when group-kerning", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.resetExceptionsForGroups.setToolTip("When Auto Bumper is supposed to add group kerning (when you have one or both of the ‘As groups’ checkboxes on), and a group kern is overridden by a kerning exception, then delete that kerning exception. Does nothing if no ‘As groups’ checkboxes are selected.")
		self.w.excludeNonExporting = vanilla.CheckBox("auto", "Exclude non-exporting glyphs", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.excludeNonExporting.setToolTip("If one of the specified glyphs is not set to export, Auto Bumper will skip it.")
		self.w.avoidZeroKerning = vanilla.CheckBox("auto", "Avoid zero kerns", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.avoidZeroKerning.setToolTip("If the calculated (and rounded) kerning value is 0, it will not be added to the font.")
		self.w.reportInMacroWindow = vanilla.CheckBox("auto", "Report in Macro Window", value=False, sizeStyle='small', callback=self.SavePreferences)
		self.w.reportInMacroWindow.setToolTip("Outputs a detailed report in the Macro Window. A few seconds slower.")
		self.w.reuseCurrentTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseCurrentTab.setToolTip("If enabled, will not open a new tab with newly added kern pairs, but reuse the current Edit tab of each font. Will open an Edit tab if none is open.")

		# Progress Bar:
		self.w.bar = vanilla.ProgressBar("auto")

		# Status line, with the prediction:
		self.w.status = vanilla.TextBox("auto", "Ready.", sizeStyle="small", selectable=True)
		self.w.status.setToolTip("Before you run: how many glyph pairs will be bumped at most with the current settings, across all masters and fonts of the chosen scope. Afterwards: how many kern pairs were added.")
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# (Hidden) Preferences Kern Strings:
		self.w.kernStrings = vanilla.TextEditor("auto", "", callback=self.SavePreferences)
		self.w.kernStrings.setToolTip("Add your default kern strings here. They will show up in the left/right dropdowns at the top. Everything after a hashtag (#) is ignored. Use blank lines for structuring.")

		self.w.text_kernStrings = vanilla.TextBox("auto", "Expand window below to access default strings.", sizeStyle='small')
		self.w.text_kernStrings.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())

		# Buttons:
		self.w.nextButton = vanilla.Button("auto", "Next Master", callback=self.masterSwitch)
		self.w.nextButton.setToolTip("Switches the frontmost font to its next master.")

		self.w.undoButton = vanilla.Button("auto", "Undo", callback=self.undo)
		self.w.undoButton.setToolTip("Restores the kerning as it was before the last time you pressed Bump Kern. Available only after kerning was added.")
		self.w.undoButton.enable(False)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Bump Kern", callback=self.BumperMain)
		self.w.runButton.setToolTip("Adds the kerning needed to reach the minimum (or maximum) distance, and opens a tab with the bumped pairs.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content. Only the hidden editor takes up extra height:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		self.w.kernStrings.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)

		# labels hug their text, and resist compression, so the fields take the leftover width:
		labelNames = (
			"textScope",
			"text_left",
			"text_right",
			"suffixText",
			"text_speed",
			"text_minDistance",
			"text_ignoreIntervals",
		)
		extraLabelNames = ("text_maxDistance", "text_roundFactor", "text_bubble")
		for labelName in labelNames + extraLabelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		for comboName in ("leftGlyphs", "rightGlyphs"):
			getattr(self.w, comboName).getNSComboBox().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setAlignment_(NSTextAlignmentLeft)

		# all leading labels share the width of the widest one, so the fields line up:
		widestLabel = "text_ignoreIntervals"
		widthRules = [
			{
				"view1": getattr(self.w, labelName),
				"attribute1": "width",
				"view2": getattr(self.w, widestLabel),
				"attribute2": "width",
			} for labelName in labelNames if labelName != widestLabel
		]
		# the four numeric fields share one width:
		widthRules += [
			{
				"view1": getattr(self.w, fieldName),
				"attribute1": "width",
				"view2": self.w.minDistance,
				"attribute2": "width",
			} for fieldName in ("maxDistance", "roundFactor", "bubbleOffset")
		]
		# right row lines up with the left row:
		widthRules += [
			{"view1": self.w.rightGlyphs, "attribute1": "width", "view2": self.w.leftGlyphs, "attribute2": "width"},
			{"view1": self.w.rightIsGroups, "attribute1": "width", "view2": self.w.leftIsGroups, "attribute2": "width"},
			{"view1": self.w.keepExistingKerning, "attribute1": "width", "view2": self.w.excludeNonExporting, "attribute2": "width"},
			{"view1": self.w.reportInMacroWindow, "attribute1": "width", "view2": self.w.keepExistingKerning, "attribute2": "width"},
		]

		def baseline(viewName, referenceName):
			return {"view1": getattr(self.w, viewName), "attribute1": "centerY", "view2": getattr(self.w, referenceName), "attribute2": "centerY"}

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[textScope]-gap-[popupScope]-inset-|",
				"H:|-inset-[text_left]-gap-[leftGlyphs(>=150)]-gap-[leftIsGroups]-gap-[swapButton(>=30)]-inset-|",
				"H:|-inset-[text_right]-gap-[rightGlyphs]-gap-[rightIsGroups]-(>=inset)-|",
				"H:|-inset-[suffixText]-gap-[suffix(120)]-(>=inset)-|",
				"H:|-inset-[text_speed]-gap-[speedPopup(>=110)]-gap-[text_speedExplanation]-(>=inset)-|",
				"H:|-inset-[text_minDistance]-gap-[minDistance(>=46)]-gap-[text_maxDistance]-gap-[maxDistance]-gap-[text_roundFactor]-gap-[roundFactor]-gap-[text_bubble]-gap-[bubbleOffset]-inset-|",
				"H:|-inset-[text_ignoreIntervals]-gap-[ignoreIntervals]-inset-|",
				"H:|-inset-[keepExistingKerning]-gap-[resetExceptionsForGroups]-(>=inset)-|",
				"H:|-inset-[excludeNonExporting]-gap-[avoidZeroKerning]-(>=inset)-|",
				"H:|-inset-[reportInMacroWindow]-gap-[reuseCurrentTab]-(>=inset)-|",
				"H:|-inset-[bar]-inset-|",
				"H:|-inset-[status]-inset-|",
				"H:|-1-[kernStrings]-1-|",
				"H:|-inset-[text_kernStrings]-inset-|",
				"H:|-inset-[undoButton(>=70)]-(>=gap)-[nextButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[popupScope]-row-[leftGlyphs]-row-[rightGlyphs]-row-[suffix]-row-[speedPopup]-row-[minDistance]-row-[ignoreIntervals]-checkGap-[keepExistingKerning]-checkRow-[excludeNonExporting]-checkRow-[reportInMacroWindow]-barGap-[bar(16)]-gap-[status]-gap-[kernStrings]-gap-[text_kernStrings]-gap-[undoButton]-inset-|",
				"V:[nextButton]-inset-|",
				"V:[runButton]-inset-|",
				# one baseline per row:
				baseline("textScope", "popupScope"),
				baseline("text_left", "leftGlyphs"),
				baseline("leftIsGroups", "leftGlyphs"),
				# the swap button spans the left and the right row:
				{"view1": self.w.swapButton, "attribute1": "top", "view2": self.w.leftGlyphs, "attribute2": "top"},
				{"view1": self.w.swapButton, "attribute1": "bottom", "view2": self.w.rightGlyphs, "attribute2": "bottom"},
				baseline("text_right", "rightGlyphs"),
				baseline("rightIsGroups", "rightGlyphs"),
				baseline("suffixText", "suffix"),
				baseline("text_speed", "speedPopup"),
				baseline("text_speedExplanation", "speedPopup"),
				baseline("text_minDistance", "minDistance"),
				baseline("text_maxDistance", "minDistance"),
				baseline("maxDistance", "minDistance"),
				baseline("text_roundFactor", "minDistance"),
				baseline("roundFactor", "minDistance"),
				baseline("text_bubble", "minDistance"),
				baseline("bubbleOffset", "minDistance"),
				baseline("text_ignoreIntervals", "ignoreIntervals"),
				baseline("resetExceptionsForGroups", "keepExistingKerning"),
				baseline("avoidZeroKerning", "excludeNonExporting"),
				baseline("reuseCurrentTab", "reportInMacroWindow"),
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "headlineGap": 12, "checkGap": 10, "checkRow": 5, "barGap": 14},
		)

		# Load Settings (this also triggers the prediction in the status line):
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# make the window resizable, but not smaller than the size Auto Layout determined.
		# (Content sizes set directly on the NSWindow, so the title bar is not counted twice.)
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()  # make sure the content has its final size before we read it
		contentSize = nsWindow.contentView().frame().size
		nsWindow.setContentMinSize_(NSSize(contentSize.width, contentSize.height))
		nsWindow.setContentMaxSize_(NSSize(contentSize.width + 1000, contentSize.height + 1000))

	def masterSwitch(self, sender=None):
		if sender is self.w.nextButton and Glyphs.font:
			Glyphs.font.masterIndex += 1
			self.updateUI()

	def kernStringList(self, sender):
		kernStrings = self.pref("kernStrings").splitlines()
		if kernStrings:
			return kernStrings
		else:
			return defaultStrings.splitlines()

	def swap(self, sender=None):
		rightEntry = self.w.rightGlyphs.get()
		rightGroupEntry = self.w.rightIsGroups.get()
		leftEntry = self.w.leftGlyphs.get()
		leftGroupEntry = self.w.leftIsGroups.get()

		self.w.rightGlyphs.set(leftEntry)
		self.w.rightIsGroups.set(leftGroupEntry)
		self.w.leftGlyphs.set(rightEntry)
		self.w.leftIsGroups.set(rightGroupEntry)

		self.SavePreferences(sender)

	def sideGlyphsAction(self, sender):
		kernStrings = self.pref("kernStrings").splitlines()
		for thisItem in sender.getItems():
			if thisItem not in kernStrings:
				kernStrings = self.pref("kernStrings") + "\n%s" % thisItem
				self.setPref("kernStrings", kernStrings)
		self.SavePreferences()

	def updateUI(self, sender=None):
		# speed explanation:
		intervalIndex = self.pref("speedPopup")
		if intervalIndex is None:
			intervalIndex = 0
		self.w.text_speedExplanation.set("Measuring every %i units." % intervalList[intervalIndex])

		# prediction in the status line:
		pairCount = self.predictedPairCount()
		if pairCount is None:
			self.w.status.set("Ready.")
		else:
			self.w.status.set(f"🔮 Will bump up to {pairCount:,} pair{'' if pairCount == 1 else 's'}.")

	def setStatus(self, text):
		"""Sets the status line and redraws it right away, so it shows while the script is busy."""
		self.w.status.set(text)
		self.w.status.getNSTextField().display()

	def cleanedSuffix(self):
		suffix = (self.pref("suffix") or "").strip()
		cleaned = "".join(letter for letter in suffix if letter in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
		return suffix, cleaned

	def targets(self):
		"""Returns (font, masters) tuples according to the scope."""
		scope = self.prefInt("popupScope")
		if scope in (0, 1):
			fonts = [Glyphs.font] if Glyphs.font else []
		else:
			fonts = list(Glyphs.fonts)
		targets = []
		for thisFont in fonts:
			if scope in (1, 3):
				masters = list(thisFont.masters)
			else:
				masters = [thisFont.selectedFontMaster]
			targets.append((thisFont, masters))
		return targets

	def glyphListsForFont(self, thisFont, suffix, report=False):
		"""Returns the glyphs for the left and for the right side, according to the current settings."""
		excludeNonExporting = self.prefBool("excludeNonExporting")
		firstList = stringToListOfGlyphsForFont(self.pref("leftGlyphs"), thisFont, report=report, excludeNonExporting=excludeNonExporting, suffix=suffix)
		secondList = stringToListOfGlyphsForFont(self.pref("rightGlyphs"), thisFont, report=report, excludeNonExporting=excludeNonExporting, suffix=suffix)
		return firstList, secondList

	def predictedPairCount(self):
		"""How many glyph pairs will be bumped at most (measured), in total. None without a font."""
		targets = self.targets()
		if not targets:
			return None
		suffix = self.cleanedSuffix()[1]
		pairCount = 0
		for thisFont, masters in targets:
			firstList, secondList = self.glyphListsForFont(thisFont, suffix)
			pairCount += len(firstList) * len(secondList) * len(masters)
		return pairCount

	def addMissingKerning(self, thisFont, thisMasterID, leftSide, rightSide, minMaxDistance, distanceBetweenShapes, existingKerning=0):
		# query user settings:
		shouldReportInMacroWindow = self.pref("reportInMacroWindow")
		shouldKeepExistingKerning = self.prefBool("keepExistingKerning")
		avoidZeroKerning = self.pref("avoidZeroKerning")
		try:
			roundValue = self.prefFloat("roundFactor")
		except:
			roundValue = 1.0
		roundValue = max(roundValue, 1.0)

		# check for existing kerning:
		kerningExists = existingKerning < 1000000  # NSNotDefined constant
		if not kerningExists:
			existingKerning = 0
		newKernValue = round((minMaxDistance - distanceBetweenShapes + existingKerning) / roundValue, 0) * roundValue

		# add only if it is OK:
		if newKernValue == 0.0 and avoidZeroKerning:
			if shouldReportInMacroWindow:
				print("\t- %s %s: zero kerning, not added." % (leftSide, rightSide))
			return False  # do not increase kern count
		else:
			if kerningExists and shouldKeepExistingKerning:
				if shouldReportInMacroWindow:
					print("\t- %s %s: keeps existing %i (instead of new %i)." % (leftSide, rightSide, existingKerning, newKernValue))
				return False  # do not increase kern count
			else:
				self.rememberPair(thisFont, thisMasterID, leftSide, rightSide)
				thisFont.setKerningForPair(thisMasterID, leftSide, rightSide, newKernValue)
				if shouldReportInMacroWindow:
					print("\t- %s %s: %i" % (leftSide, rightSide, newKernValue))
				return True  # increase kern count

	def rememberPair(self, font, masterID, leftKey, rightKey):
		# Records the current value of a kern pair (or None if there is none), before we change it.
		# Undo replays these in reverse order. Assigning a saved copy of font.kerning back to the font
		# does not work: Glyphs then fails in setKerningForPair() (sortUsingFunction:context:).
		if self.undoSteps is None:
			return
		previous = font.kerningForPair(masterID, leftKey, rightKey)
		if previous is None or previous >= 1000000:  # None (Glyphs 3) or NSNotFound (Glyphs 2): no such pair
			previous = None
		self.undoSteps.append((font, masterID, leftKey, rightKey, previous))

	def undo(self, sender=None):
		if self.undoSteps is None:
			return
		for font, masterID, leftKey, rightKey, previous in reversed(self.undoSteps):
			if previous is None:
				font.removeKerningForPair(masterID, leftKey, rightKey)
			else:
				font.setKerningForPair(masterID, leftKey, rightKey, previous)
		self.undoSteps = None
		self.w.undoButton.enable(False)
		self.setStatus("↩️ Kerning restored.")

	def BumperMain(self, sender):
		try:
			# save prefs
			self.SavePreferences()

			targets = self.targets()
			if not targets:
				Message(title="No Font Open", message="Auto Bumper requires a font. Open a font and run the script again.", OKButton=None)
				return

			# validate suffix:
			suffix, cleanedSuffix = self.cleanedSuffix()
			if cleanedSuffix != suffix:
				Message(
					title="Invalid Suffix Error",
					message="The suffix you entered ('%s') is invalid. The script suggests '%s' instead. Please verify and try again." % (suffix, cleanedSuffix),
					OKButton=None
				)
				self.w.suffix.set(cleanedSuffix)
				self.SavePreferences()
				return

			# start reporting to macro window:
			shouldReportInMacroWindow = self.pref("reportInMacroWindow")
			if shouldReportInMacroWindow:
				Glyphs.clearLog()
				print("Auto Bumper Report\n")

			# reset progress bar:
			self.w.bar.set(0)
			# start taking time:
			start = timer()

			# query user input:
			step = intervalList[self.pref("speedPopup")]
			resetExceptionsForGroups = self.prefBool("resetExceptionsForGroups")
			leftIsGroups = self.prefBool("leftIsGroups")
			rightIsGroups = self.prefBool("rightIsGroups")

			roundFactor = self.pref("roundFactor")
			try:
				roundFactor = float(roundFactor)
			except:
				roundFactor = None
				self.w.roundFactor.set("")
				self.SavePreferences()

			bubbleRaw = str(self.pref("bubbleOffset") or "").strip()
			useBubble = False
			bubbleOffsetValue = 0.0
			if bubbleRaw != "":
				try:
					bubbleOffsetValue = float(bubbleRaw)
					useBubble = True
				except:
					pass

			totalPairs = self.predictedPairCount()
			if totalPairs:
				self.setStatus(f"🛠️ Bumping up to {totalPairs:,} pair{'' if totalPairs == 1 else 's'}…")

			# remember the prior state for Undo:
			self.undoSteps = []
			self.w.undoButton.enable(True)

			measuredPairs = 0
			kernCount = 0
			for thisFont, masters in targets:
				firstGlyphList, secondGlyphList = self.glyphListsForFont(thisFont, suffix, report=bool(shouldReportInMacroWindow))
				if not firstGlyphList or not secondGlyphList:
					print(
						"⚠️ %s: no pairs to bump. With the current settings, there are %i glyphs for the left side and %i glyphs for the right side. Skipping this font." % (
							thisFont.familyName,
							len(firstGlyphList),
							len(secondGlyphList),
						)
					)
					continue

				bumpedPairs = {}  # left glyph name -> right glyph names (each only once, even if bumped in more than one master)
				for thisMaster in masters:
					thisMasterID = thisMaster.id
					if shouldReportInMacroWindow:
						print("%s, master %s:\n" % (thisFont.familyName, thisMaster.name))

					# COLLECTING THE DATA WE NEED:
					ignoreIntervals = sortedIntervalsFromString(self.pref("ignoreIntervals"), font=thisFont, mID=thisMasterID)
					minDistance = distanceFromEntry(self.pref("minDistance"), thisFont, thisMasterID)
					maxDistance = distanceFromEntry(self.pref("maxDistance"), thisFont, thisMasterID)

					# report key values for kerning:
					if shouldReportInMacroWindow:
						if minDistance is not None:
							print("Minimum Distance: %i" % minDistance)
						if maxDistance is not None:
							print("Maximum Distance: %i" % maxDistance)
						if roundFactor is not None:
							print("Rounding: %i" % roundFactor)
						if useBubble:
							print("Bubble offset: %g" % bubbleOffsetValue)
						print()
						print("⬅️ L glyphs:\n%s\n" % ", ".join([g.name for g in firstGlyphList]))
						print("➡️ R glyphs:\n%s\n" % ", ".join([g.name for g in secondGlyphList]))

					# precompute bubble layers if requested (avoids recomputing per pair):
					if useBubble:
						leftBubbleLayers = {g.name: bubbleLayer(g.layers[thisMasterID], offset=bubbleOffsetValue) for g in firstGlyphList}
						rightBubbleLayers = {g.name: bubbleLayer(g.layers[thisMasterID], offset=bubbleOffsetValue) for g in secondGlyphList}

					# CREATE KERNING DATA:
					for leftGlyph in firstGlyphList:
						# update progress bar:
						self.w.bar.set(int(100 * (float(measuredPairs) / max(totalPairs, 1))))
						measuredPairs += len(secondGlyphList)

						# determine left glyph:
						leftLayer = leftGlyph.layers[thisMasterID]
						leftGroup = leftGlyph.rightKerningGroup
						if leftIsGroups:
							if leftGroup:
								leftSide = "@MMK_L_%s" % leftGroup
							else:
								print("⚠️ Left glyph %s has no kerning group. Cannot apply group kerning." % leftGlyph.name)
								leftSide = None
						else:
							leftSide = leftGlyph.name

						# only continue if we could establish a left side:
						if not leftSide:
							continue

						# cycle through right glyphs:
						for rightGlyph in secondGlyphList:
							rightLayer = rightGlyph.layers[thisMasterID]
							rightGroup = rightGlyph.leftKerningGroup
							if rightIsGroups:
								if rightGroup:
									rightSide = "@MMK_R_%s" % rightGroup
								else:
									print("⚠️ Right glyph %s has no kerning group. Cannot apply group kerning." % rightGlyph.name)
									rightSide = None
							else:
								rightSide = rightGlyph.name

							# only continue if we could establish a right side:
							if not rightSide:
								continue

							if resetExceptionsForGroups:
								if leftIsGroups and thisFont.kerningForPair(thisMasterID, leftGlyph.name, rightSide) is not None:
									self.rememberPair(thisFont, thisMasterID, leftGlyph.name, rightSide)
									thisFont.removeKerningForPair(thisMasterID, leftGlyph.name, rightSide)
								if rightIsGroups and thisFont.kerningForPair(thisMasterID, leftSide, rightGlyph.name) is not None:
									self.rememberPair(thisFont, thisMasterID, leftSide, rightGlyph.name)
									thisFont.removeKerningForPair(thisMasterID, leftSide, rightGlyph.name)
								if (leftIsGroups and rightIsGroups) and thisFont.kerningForPair(thisMasterID, leftGlyph.name, rightGlyph.name) is not None:
									self.rememberPair(thisFont, thisMasterID, leftGlyph.name, rightGlyph.name)
									thisFont.removeKerningForPair(thisMasterID, leftGlyph.name, rightGlyph.name)

							kerning = effectiveKerning(leftGlyph.name, rightGlyph.name, thisFont, thisMasterID)
							measureLeft = leftBubbleLayers[leftGlyph.name] if useBubble else leftLayer
							measureRight = rightBubbleLayers[rightGlyph.name] if useBubble else rightLayer
							distanceBetweenShapes = minDistanceBetweenTwoLayers(
								measureLeft, measureRight, interval=step, kerning=kerning, report=False, ignoreIntervals=ignoreIntervals
							)
							if distanceBetweenShapes is None:
								continue

							# positive kerning (if desired):
							if minDistance and distanceBetweenShapes < minDistance:
								if self.addMissingKerning(thisFont, thisMasterID, leftSide, rightSide, minDistance, distanceBetweenShapes, existingKerning=kerning):
									kernCount += 1
									bumpedPairs.setdefault(leftGlyph.name, {})[rightGlyph.name] = None

							# negative kerning (if desired):
							if maxDistance and distanceBetweenShapes > maxDistance:
								if self.addMissingKerning(thisFont, thisMasterID, leftSide, rightSide, maxDistance, distanceBetweenShapes, existingKerning=kerning):
									kernCount += 1
									bumpedPairs.setdefault(leftGlyph.name, {})[rightGlyph.name] = None

				# one tab per font, with the bumped pairs of all its masters:
				if bumpedPairs:
					tabString = "\n".join("/space".join("/%s/%s" % (left, right) for right in rights) for left, rights in bumpedPairs.items())
					if self.pref("reuseCurrentTab") and thisFont.currentTab:
						thisFont.currentTab.text = tabString
					else:
						thisFont.newTab(tabString)

			# FINISH UP AND REPORT:
			self.w.bar.set(100)
			timereport = reportTimeInNaturalLanguage(timer() - start)

			if kernCount:
				report = f'Added {kernCount} kern pair{"s" if kernCount != 1 else ""} in {timereport}.'
			else:
				report = f'No kerning added ({timereport}).'
			self.setStatus(f"✅ {report}")

			# Report in Macro Window:
			if shouldReportInMacroWindow:
				print()
				print(report)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			self.setStatus("❌ Error. Details in Macro Window.")
			print("Auto Bumper Error: %s" % e)
			import traceback
			print(traceback.format_exc())


Bumper()
