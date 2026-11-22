# MenuTitle: Compress Glyph
__doc__ = """
Compresses the kerning of glyphs, i.e., replaces glyph-level kerning with group kerning (closes the lock). Glyph names are comma-separated patterns, * and ? are wildcards. Choose the masters and fonts to work in, and undo the last compression if you do not like it.
"""

import vanilla
from mekkablue import mekkaObject, match, reportFontName, UpdateButton, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
)

# sorted by escalation, from the least to the most masters that are affected:
scopes = (
	"this master",
	"all masters but this one",
	"⚠️ all masters",
	"⚠️ all masters in all open fonts",
)
allOtherMastersScope = 1
allMastersScope = 2
allFontsScope = 3

scopeTooltip = (
	"Where the kerning is compressed:\n"
	"• this master: the selected master of the frontmost font\n"
	"• all masters but this one: all other masters of the frontmost font\n"
	"• all masters: every master of the frontmost font\n"
	"• all masters in all open fonts\n\n"
	"⚠️ Mind the bigger scopes: they change kerning in many places with one click. You can undo the last compression, but consider saving first."
)

patternTooltip = "Glyph names, separated by commas. * stands for any number of characters, ? for exactly one. A pattern has to match the whole glyph name: use *.dnom* for ‘contains .dnom’."


def sidesToCompress(leftMatches, rightMatches, compressLeft, compressRight, compressOtherSide):
	"""
	For a kern pair in which the left and/or the right glyph matches the glyph names, returns which sides of the
	pair are compressed, as a tuple (compressLeftSide, compressRightSide).
	A matching glyph compresses its own side if it is on the side that is checked (compressLeft, compressRight).
	compressOtherSide additionally compresses the opposite side of the pair. If neither side is checked,
	the matching glyph can be on any side, and only the other side is compressed.
	"""
	neitherChecked = not compressLeft and not compressRight
	leftSide, rightSide = False, False
	if leftMatches:
		if compressLeft:
			leftSide = True
		if compressOtherSide and (compressLeft or neitherChecked):
			rightSide = True
	if rightMatches:
		if compressRight:
			rightSide = True
		if compressOtherSide and (compressRight or neitherChecked):
			leftSide = True
	return leftSide, rightSide


class CompressGlyph(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"glyphName": "V",
		"compressLeft": 1,
		"compressRight": 1,
		"compressOtherSide": 0,
		"scope": 0,
		"openTab": 0,
		"verbose": 0,
	}

	def __init__(self):
		# state for Undo (None as long as there is nothing to undo; otherwise a list of the pairs we touched):
		self.undoSteps = None

		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Compress Glyph",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Compress kerning (i.e., close locks) of glyphs with these names:", sizeStyle="small", selectable=True)
		self.w.descriptionText.setToolTip(patternTooltip)

		self.w.glyphName = vanilla.ComboBox("auto", (), callback=self.SavePreferences, sizeStyle="small")
		self.w.glyphName.setToolTip(patternTooltip)
		self.w.updateButton = UpdateButton("auto", callback=self.update)
		self.w.updateButton.setToolTip("Reloads the glyph names of the frontmost font into the combo box.")

		self.w.compressText = vanilla.TextBox("auto", "Compress when glyph is", sizeStyle="small", selectable=True)
		self.w.compressLeft = vanilla.CheckBox("auto", "left side", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.compressRight = vanilla.CheckBox("auto", "right side of pair", value=True, callback=self.SavePreferences, sizeStyle="small")

		self.w.compressOtherSide = vanilla.CheckBox("auto", "Also compress the other side of the pair", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.compressOtherSide.setToolTip(
			"Turns a matching pair into group-to-group kerning on both sides. Off: only the matching glyph’s own side is compressed, "
			"the other side stays as it is. If neither ‘left side’ nor ‘right side’ is checked, only the other side of the pair is compressed. "
			"Pairs are left alone if a side that is to be compressed has no kerning group."
		)

		self.w.divider = vanilla.HorizontalLine("auto")

		self.w.scopeText = vanilla.TextBox("auto", "Compress in:", sizeStyle="small", selectable=True)
		self.w.scope = vanilla.PopUpButton("auto", scopes, callback=self.SavePreferences, sizeStyle="small")
		self.w.scopeText.setToolTip(scopeTooltip)
		self.w.scope.setToolTip(scopeTooltip)

		self.w.openTab = vanilla.CheckBox("auto", "Open tab with affected pairs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.openTab.setToolTip("Opens a tab with the affected kern pairs, with a space in between. One tab per font.")
		self.w.verbose = vanilla.CheckBox("auto", "Verbose report in Macro window", value=False, callback=self.SavePreferences, sizeStyle="small")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)

		# Buttons:
		self.w.undoButton = vanilla.Button("auto", "Undo", callback=self.undo)
		self.w.undoButton.setToolTip("Restores the kerning as it was before the last time you pressed Compress. Available only after kerning was compressed.")
		self.w.undoButton.enable(False)
		self.w.runButton = vanilla.Button("auto", "Compress", callback=self.CompressGlyphMain)
		self.w.runButton.setToolTip("Compresses the kerning of the glyphs in the chosen scope.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, the popup takes the leftover width:
		nsLabel = self.w.scopeText.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[glyphName]-gap-[updateButton]-inset-|",
				"H:|-inset-[compressText]-gap-[compressLeft]-gap-[compressRight]-(>=inset)-|",
				"H:|-inset-[compressOtherSide]-(>=inset)-|",
				"H:|-inset-[divider]-inset-|",
				"H:|-inset-[scopeText]-gap-[scope]-inset-|",
				"H:|-inset-[openTab]-(>=inset)-|",
				"H:|-inset-[verbose]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-inset-[status]-inset-|",
				"H:|-inset-[undoButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-row-[glyphName]-gap-[compressLeft]-checkRow-[compressOtherSide]-section-[divider(1)]-section-[scope]-gap-[openTab]-checkRow-[verbose]-barGap-[progress(16)]-gap-[status]-section-[runButton]-inset-|",
				"V:[undoButton]-inset-|",
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.glyphName, "attribute2": "centerY"},
				{"view1": self.w.compressText, "attribute1": "centerY", "view2": self.w.compressLeft, "attribute2": "centerY"},
				{"view1": self.w.compressRight, "attribute1": "centerY", "view2": self.w.compressLeft, "attribute2": "centerY"},
				{"view1": self.w.scopeText, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "barGap": 12, "section": 10},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.update()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		neitherSide = not self.w.compressLeft.get() and not self.w.compressRight.get()
		self.w.compressOtherSide.setTitle("Only compress the other side of the pair" if neitherSide else "Also compress the other side of the pair")
		self.w.runButton.enable(not neitherSide or bool(self.w.compressOtherSide.get()))
		self.w.status.set("🤖 Ready.")

	def update(self, sender=None):
		font = Glyphs.font
		if not font:
			self.w.glyphName.setItems(())
			return
		names = [g.name for g in font.glyphs]
		names.extend(sorted(set(f'*{g.name[g.name.find("."):]}' for g in font.glyphs if "." in g.name and not g.name.startswith("."))))
		self.w.glyphName.setItems(names)

	def setProgress(self, percent, text):
		"""Sets progress bar and status line, and redraws them right away, so they show while the script is busy."""
		self.w.progress.set(percent)
		self.w.status.set(text)
		self.w.getNSWindow().displayIfNeeded()

	def kernValue(self, font, masterID, leftKey, rightKey):
		"""The value of a kern pair, or None if there is no such pair."""
		value = font.kerningForPair(masterID, leftKey, rightKey)
		if value is None or value >= 1000000:  # None (Glyphs 3): no such pair, or NSNotFound (Glyphs 2)
			return None
		return value

	def rememberPair(self, font, masterID, leftKey, rightKey):
		# Records the current value of a kern pair (or None if there is none), before we change it.
		# Undo replays these in reverse order. Assigning a saved copy of font.kerning back to the font
		# does not work: Glyphs then fails in setKerningForPair() (sortUsingFunction:context:).
		self.undoSteps.append((font, masterID, leftKey, rightKey, self.kernValue(font, masterID, leftKey, rightKey)))

	def undo(self, sender=None):
		if self.undoSteps is None:
			return
		openFonts = list(Glyphs.fonts)
		for font, masterID, leftKey, rightKey, previous in reversed(self.undoSteps):
			if font not in openFonts:
				continue  # the font was closed in the meantime
			if previous is None:
				font.removeKerningForPair(masterID, leftKey, rightKey)
			else:
				font.setKerningForPair(masterID, leftKey, rightKey, previous)
		self.undoSteps = None
		self.w.undoButton.enable(False)
		self.w.progress.set(0)
		self.w.status.set("↩️ Kerning restored.")

	def jobsForScope(self, scope):
		"""Returns pairs of (font, masters) for the scope."""
		if scope == allFontsScope:
			return [(font, list(font.masters)) for font in Glyphs.fonts]
		font = Glyphs.font
		if scope == allOtherMastersScope:
			return [(font, [master for master in font.masters if master != font.selectedFontMaster])]
		if scope == allMastersScope:
			return [(font, list(font.masters))]
		return [(font, [font.selectedFontMaster])]

	def compressFont(self, font, masters, patterns, compressLeft, compressRight, compressOtherSide, verbose=False, progress=None):
		"""
		Compresses the kerning of the glyphs matching the patterns in these masters of the font, in a single pass.
		Returns (compressedCount, affectedPairs, skippedCount), with affectedPairs a list of (leftName, rightName).
		"""
		glyphsByID = {glyph.id: glyph for glyph in font.glyphs}
		matchedIDs = {glyph.id for glyph in font.glyphs if any(match(pattern, glyph.name) for pattern in patterns)}
		if not matchedIDs:
			print(f"  ⚠️ No glyphs matching {', '.join(patterns)}")
			return 0, [], 0

		compressedCount = 0
		skippedCount = 0
		affectedPairs = []
		seenPairs = set()
		for masterIndex, master in enumerate(masters):
			if progress:
				progress(masterIndex, master)
			print(f"  Ⓜ️ {master.name}")
			if master.id not in font.kerning:
				print("  ⚠️ This master has no kerning.")
				continue
			kerning = font.kerning[master.id]
			plan = {}  # new pair -> value
			planSources = {}  # new pair -> old value from which it was made
			removals = []  # old pairs, as (left, right)
			for leftKey in list(kerning.keys()):
				for rightKey in list(kerning[leftKey].keys()):
					leftKeyString, rightKeyString = str(leftKey), str(rightKey)
					leftIsGroup, rightIsGroup = leftKeyString.startswith("@"), rightKeyString.startswith("@")
					leftGlyph = None if leftIsGroup else glyphsByID.get(leftKeyString)
					rightGlyph = None if rightIsGroup else glyphsByID.get(rightKeyString)
					if (leftGlyph is None and not leftIsGroup) or (rightGlyph is None and not rightIsGroup):
						continue  # stale glyph ID
					leftMatches = leftGlyph is not None and leftGlyph.id in matchedIDs
					rightMatches = rightGlyph is not None and rightGlyph.id in matchedIDs
					if not leftMatches and not rightMatches:
						continue

					compressLeftSide, compressRightSide = sidesToCompress(leftMatches, rightMatches, compressLeft, compressRight, compressOtherSide)
					oldLeft = leftKeyString if leftIsGroup else leftGlyph.name
					oldRight = rightKeyString if rightIsGroup else rightGlyph.name
					newLeft, newRight = oldLeft, oldRight
					cannotCompress = False
					if compressLeftSide and leftGlyph is not None:
						if leftGlyph.rightKerningGroup:
							newLeft = f"@MMK_L_{leftGlyph.rightKerningGroup}"
						else:
							cannotCompress = True
					if compressRightSide and rightGlyph is not None:
						if rightGlyph.leftKerningGroup:
							newRight = f"@MMK_R_{rightGlyph.leftKerningGroup}"
						else:
							cannotCompress = True
					if cannotCompress:
						skippedCount += 1
						if verbose:
							print(f"\t⚠️ {oldLeft} {oldRight}: a side to compress has no kerning group, skipped")
						continue
					if (newLeft, newRight) == (oldLeft, oldRight):
						continue  # nothing to compress: these sides are groups already

					value = kerning[leftKey][rightKey]
					if (newLeft, newRight) in plan and plan[(newLeft, newRight)] != value:
						print(f"\t⚠️ {newLeft} {newRight}: {oldLeft} {oldRight} ({value}) conflicts with {planSources[(newLeft, newRight)]} ({plan[(newLeft, newRight)]}), the last one wins")
					plan[(newLeft, newRight)] = value
					planSources[(newLeft, newRight)] = f"{oldLeft} {oldRight}"
					removals.append((oldLeft, oldRight))
					if verbose:
						print(f"\t🗜️ {oldLeft} {oldRight} → {newLeft} {newRight}: {value}")
					if (oldLeft, oldRight) not in seenPairs:
						seenPairs.add((oldLeft, oldRight))
						affectedPairs.append((oldLeft, oldRight))

			# remove the old pairs first and add the new ones afterwards: a new pair
			# may be the same as an old pair of another glyph, and would be removed otherwise.
			removedPairs = set(removals)
			for newPair, value in plan.items():
				if newPair not in removedPairs:
					existing = self.kernValue(font, master.id, newPair[0], newPair[1])
					if existing is not None and existing != value:
						print(f"\t⚠️ {newPair[0]} {newPair[1]}: existing value {existing} is replaced by {value}")
			for oldLeft, oldRight in removals:
				self.rememberPair(font, master.id, oldLeft, oldRight)
				font.removeKerningForPair(master.id, oldLeft, oldRight)
			for (newLeft, newRight), value in plan.items():
				self.rememberPair(font, master.id, newLeft, newRight)
				font.setKerningForPair(master.id, newLeft, newRight, value)

			print(f"  ✅ Compressed {len(removals)} kern pair{'' if len(removals) == 1 else 's'}")
			compressedCount += len(removals)

		return compressedCount, affectedPairs, skippedCount

	def tabText(self, font, pairs):
		"""The text for a tab with these kern pairs, separated by spaces. Group keys are shown with a glyph of the group."""
		leftGroupGlyphs, rightGroupGlyphs = {}, {}
		for glyph in font.glyphs:
			if glyph.rightKerningGroup:
				leftGroupGlyphs.setdefault(f"@MMK_L_{glyph.rightKerningGroup}", glyph.name)
			if glyph.leftKerningGroup:
				rightGroupGlyphs.setdefault(f"@MMK_R_{glyph.leftKerningGroup}", glyph.name)
		words = []
		for left, right in pairs:
			if left.startswith("@"):
				left = leftGroupGlyphs.get(left)
			if right.startswith("@"):
				right = rightGroupGlyphs.get(right)
			if left and right:
				words.append(f"/{left}/{right}")
		return " ".join(words)

	def CompressGlyphMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			patterns = [pattern.strip() for pattern in str(self.pref("glyphName")).split(",") if pattern.strip()]
			compressLeft = self.prefBool("compressLeft")
			compressRight = self.prefBool("compressRight")
			compressOtherSide = self.prefBool("compressOtherSide")
			scope = self.prefInt("scope")
			openTab = self.prefBool("openTab")
			verbose = self.prefBool("verbose")

			if Glyphs.font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			if not patterns:
				self.setProgress(0, "⚠️ No glyph names given.")
				return

			jobs = [(font, masters) for font, masters in self.jobsForScope(scope) if masters]
			if not jobs:
				self.setProgress(0, "⚠️ No masters in this scope.")
				return

			print("Compress Glyph Report")
			print(f"Glyphs: {', '.join(patterns)}\n")

			self.undoSteps = []  # from now on, the pairs we touch are remembered
			totalMasters = sum(len(masters) for font, masters in jobs)
			doneMasters = 0
			totalCount = 0
			totalSkipped = 0
			for font, masters in jobs:
				print(f"📄 {reportFontName(font)}")
				if not font.kerning:
					print("  ⚠️ This font has no kerning.\n")
					doneMasters += len(masters)
					continue

				def progress(masterIndex, master, font=font, doneMasters=doneMasters):
					self.setProgress(100 * (doneMasters + masterIndex) // totalMasters, f"🛠️ {font.familyName}, {master.name}…")

				compressedCount, affectedPairs, skippedCount = self.compressFont(font, masters, patterns, compressLeft, compressRight, compressOtherSide, verbose, progress)
				doneMasters += len(masters)
				totalCount += compressedCount
				totalSkipped += skippedCount
				if openTab and affectedPairs:
					text = self.tabText(font, affectedPairs)
					if text:
						font.newTab(text)
				print()

			if self.undoSteps:
				self.w.undoButton.enable(True)
			else:
				self.undoSteps = None
				self.w.undoButton.enable(False)

			summary = f"Compressed {totalCount:,} kern pair{'' if totalCount == 1 else 's'}"
			if totalSkipped:
				summary += f", skipped {totalSkipped:,} without group"
			if totalCount:
				self.setProgress(100, f"✅ {summary}.")
			else:
				self.setProgress(0, "⚠️ Nothing to compress." if not totalSkipped else f"⚠️ {summary}.")
			print(f"{summary}.")
			Glyphs.showNotification("Compress Glyph", f"{summary}. Details in Macro Window.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			self.w.status.set("❌ Error, see Macro Window.")
			print(f"Compress Glyph Error: {e}")
			import traceback
			print(traceback.format_exc())


CompressGlyph()
