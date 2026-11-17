# MenuTitle: Remove TT Hints
__doc__ = """
Deletes a user-specified set of TT instructions in the selected glyphs, a master, the complete font or all open fonts. Can also delete detached hints and the zero deltas (deltas with an offset of zero) in TT delta hints.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, TTSTEM, TTANCHOR, TTALIGN, TTINTERPOLATE, TTDIAGONAL, TTDELTA, Message
from mekkablue import mekkaObject, fontFileName
from hintscopes import scopes, scopeTooltip, detachedTooltip, isDetached, fontsForScope, glyphsAndLayers


class RemoveTTHints(mekkaObject):
	prefDict = {
		"scope": 0,
		"detachedHints": 0,
		"zeroDeltas": 0,

		"hStems": 0,
		"hAnchors": 0,
		"hAlign": 0,
		"hInterpolate": 0,
		"hDiagonal": 0,
		"hDelta": 0,

		"vStems": 0,
		"vAnchors": 0,
		"vAlign": 0,
		"vInterpolate": 0,
		"vDiagonal": 0,
		"vDelta": 0,
	}

	# (type, name of the pref without the h or v) in the order of the rows:
	hintTypes = (
		(TTSTEM, "Stems"),
		(TTANCHOR, "Anchors"),
		(TTALIGN, "Align"),
		(TTINTERPOLATE, "Interpolate"),
		(TTDIAGONAL, "Diagonal"),
		(TTDELTA, "Delta"),
	)
	hintTooltips = {
		"Stems": "Stem hints: control the thickness of a stem, i.e. the distance between two edges of a stem",
		"Anchors": "Snap (Anchor) hints: snap a node to the pixel grid",
		"Align": "Shift (Align) hints: align a node with another node or with an alignment zone",
		"Interpolate": "Interpolate hints: place a node between two other nodes, in proportion to their original distances",
		"Diagonal": "Diagonal hints: control the thickness of a diagonal stem",
		"Delta": "Delta hints: move nodes by a number of pixels at specific ppm sizes. Removes the complete delta hints, with all their deltas",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 450
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove TT Hints",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Remove the following hints in", sizeStyle='small', selectable=True)
		self.w.scope = vanilla.PopUpButton("auto", scopes, sizeStyle='small', callback=self.SavePreferences)
		self.w.scope.setToolTip(scopeTooltip)
		self.w.descriptionText.setToolTip(scopeTooltip)

		titles = {"Stems": "H Stem", "Anchors": "H Snap (Anchor)", "Align": "H Shift (Align)", "Interpolate": "H Interpolate", "Diagonal": "H Diagonal", "Delta": "H Delta"}
		for hintType, name in self.hintTypes:
			hTitle = titles[name]
			vTitle = hTitle.replace("H ", "V ", 1)
			for prefix, arrow, title, direction in (("h", "⬍", hTitle, "Horizontal"), ("v", "⬌", vTitle, "Vertical")):
				checkBox = vanilla.CheckBox("auto", f"{arrow} {title}", value=False, callback=self.SavePreferences, sizeStyle='small')
				checkBox.setToolTip(f"{direction} {self.hintTooltips[name]}.")
				setattr(self.w, f"{prefix}{name}", checkBox)

		self.w.detachedHints = vanilla.CheckBox("auto", "Detached Hints", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.detachedHints.setToolTip(f"Removes all TT hints of any type that are {detachedTooltip}.")

		self.w.zeroDeltas = vanilla.CheckBox("auto", "Zero Deltas", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.zeroDeltas.setToolTip(
			"Removes the deltas with an offset of zero from all TT delta hints, because they have no effect. "
			"A delta hint that has no deltas left is removed. "
			"Delta hints that are removed completely with ⬍ H Delta or ⬌ V Delta are not counted."
		)

		self.w.hON = vanilla.SquareButton("auto", "H on", sizeStyle='small', callback=self.update)
		self.w.hOFF = vanilla.SquareButton("auto", "H off", sizeStyle='small', callback=self.update)
		self.w.hON.setToolTip("Checks all horizontal (⬍) hint types.")
		self.w.hOFF.setToolTip("Unchecks all horizontal (⬍) hint types.")

		self.w.vON = vanilla.SquareButton("auto", "V on", sizeStyle='small', callback=self.update)
		self.w.vOFF = vanilla.SquareButton("auto", "V off", sizeStyle='small', callback=self.update)
		self.w.vON.setToolTip("Checks all vertical (⬌) hint types.")
		self.w.vOFF.setToolTip("Unchecks all vertical (⬌) hint types.")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove", callback=self.RemoveTTHintsMain)
		self.w.runButton.setToolTip("Removes the checked hint types in the chosen scope.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes and square buttons stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.descriptionText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		# two columns of checkboxes, one shared width, and Detached Hints and Zero Deltas as a third column in the Diagonal and Delta rows:
		rowNames = [name for _, name in self.hintTypes]
		hNames = [f"h{name}" for name in rowNames]
		vNames = [f"v{name}" for name in rowNames]
		columnRules = [
			{"view1": getattr(self.w, name), "attribute1": "width", "view2": self.w.hStems, "attribute2": "width"}
			for name in hNames[1:] + vNames
		]
		rowRules = [
			{"view1": getattr(self.w, vName), "attribute1": "centerY", "view2": getattr(self.w, hName), "attribute2": "centerY"}
			for hName, vName in zip(hNames, vNames)
		]
		rowRules.append({"view1": self.w.detachedHints, "attribute1": "centerY", "view2": self.w.hDiagonal, "attribute2": "centerY"})
		rowRules.append({"view1": self.w.zeroDeltas, "attribute1": "centerY", "view2": self.w.hDelta, "attribute2": "centerY"})
		# the third column starts at one position:
		rowRules.append({"view1": self.w.detachedHints, "attribute1": "left", "view2": self.w.zeroDeltas, "attribute2": "left"})
		rules = ["H:|-inset-[descriptionText]-gap-[scope]-inset-|"]
		for hName, vName in zip(hNames, vNames):
			if hName == "hDiagonal":
				rules.append(f"H:|-inset-[{hName}]-gap-[{vName}]-gap-[detachedHints]-(>=inset)-|")
			elif hName == "hDelta":
				rules.append(f"H:|-inset-[{hName}]-gap-[{vName}]-gap-[zeroDeltas]-(>=inset)-|")
			else:
				rules.append(f"H:|-inset-[{hName}]-gap-[{vName}]-(>=inset)-|")
		rules += [
			"H:|-inset-[hON(>=40)]-4-[hOFF(>=40)]-(>=gap)-[vON(>=40)]-4-[vOFF(>=40)]-(>=inset)-|",
			"H:|-inset-[progress]-inset-|",
			"H:|-inset-[status]-(>=gap)-[runButton(>=70)]-inset-|",
			"V:|-gap-[scope]-headlineGap-" + "-stackRow-".join(f"[{hName}]" for hName in hNames) + "-headlineGap-[hON]-headlineGap-[progress(16)]-inset-[runButton]-inset-|",
			{"view1": self.w.descriptionText, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
			{"view1": self.w.hOFF, "attribute1": "centerY", "view2": self.w.hON, "attribute2": "centerY"},
			{"view1": self.w.vON, "attribute1": "centerY", "view2": self.w.hON, "attribute2": "centerY"},
			{"view1": self.w.vOFF, "attribute1": "centerY", "view2": self.w.hON, "attribute2": "centerY"},
			{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			# the V buttons start in the column of the V checkboxes:
			{"view1": self.w.vON, "attribute1": "left", "view2": self.w.vStems, "attribute2": "left"},
		]
		self.w.addAutoPosSizeRules(
			rules + columnRules + rowRules,
			metrics={"inset": inset, "gap": 8, "headlineGap": 10, "stackRow": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		self.update()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def hintCheckBoxNames(self, prefix):
		return [f"{prefix}{name}" for _, name in self.hintTypes]

	def update(self, sender=None, savePrefs=True):
		if sender:  # any button
			onOff = 1 if sender in (self.w.hON, self.w.vON) else 0
			if sender in (self.w.hON, self.w.hOFF):
				for name in self.hintCheckBoxNames("h"):
					getattr(self.w, name).set(onOff)
			if sender in (self.w.vON, self.w.vOFF):
				for name in self.hintCheckBoxNames("v"):
					getattr(self.w, name).set(onOff)

		self.updateUI()

		if savePrefs:
			self.SavePreferences()

	def checkedTypeCount(self):
		checkBoxNames = self.hintCheckBoxNames("h") + self.hintCheckBoxNames("v") + ["detachedHints", "zeroDeltas"]
		return sum(1 for name in checkBoxNames if getattr(self.w, name).get())

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.checkedTypeCount() > 0)
		self.w.status.set("🤖 Ready.")

	def setProgress(self, percent, text):
		"""Sets progress bar and status line, and redraws them right away, so they show while the script is busy."""
		self.w.progress.set(percent)
		self.w.status.set(text)
		self.w.getNSWindow().displayIfNeeded()

	def removeZeroDeltasFromHint(self, layer, index, hint):
		"""Deletes the deltas with an offset of zero in a TT delta hint, and the hint if nothing is left. Returns the number of deleted deltas."""
		count = 0
		elementDict = hint.elementDict()
		if "settings" in elementDict:
			settings = elementDict["settings"]
			if settings:
				for deltaType in ("deltaH", "deltaV"):
					if deltaType in settings:
						for transformType in list(settings[deltaType].keys()):
							deltas = settings[deltaType][transformType]
							for ppmSize in list(deltas.keys()):
								if deltas[ppmSize] == 0:
									del deltas[ppmSize]
									count += 1

							# clean up delta PPMs:
							if len(settings[deltaType][transformType]) == 0:
								del settings[deltaType][transformType]

						# clean up delta directions:
						if len(settings[deltaType]) == 0:
							del settings[deltaType]

			# clean up hints:
			if not elementDict["settings"]:
				del layer.hints[index]
		return count

	def removeHintsFromLayer(self, layer, removals, removeZeroDeltas, removeDetached=False):
		"""Returns the number of deleted hints and the number of deleted zero deltas."""
		hintCount = 0
		zeroDeltaCount = 0
		for i in reversed(range(len(layer.hints))):
			hint = layer.hints[i]
			if not hint.isTrueType:
				continue
			if (hint.type, bool(hint.horizontal)) in removals or (removeDetached and isDetached(hint)):
				del layer.hints[i]
				hintCount += 1
			elif removeZeroDeltas and hint.type == TTDELTA:
				zeroDeltaCount += self.removeZeroDeltasFromHint(layer, i, hint)

		if hintCount or zeroDeltaCount:
			parts = []
			if hintCount:
				parts.append(f"{hintCount} instruction{'' if hintCount == 1 else 's'}")
			if zeroDeltaCount:
				parts.append(f"{zeroDeltaCount} zero delta{'' if zeroDeltaCount == 1 else 's'}")
			print(f"  - Removed {' and '.join(parts)} from {layer.parent.name}, layer ‘{layer.name}’")
		return hintCount, zeroDeltaCount

	def RemoveTTHintsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if Glyphs.font is None:
				self.setProgress(0, "⚠️ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			scope = self.prefInt("scope")
			removeZeroDeltas = self.prefBool("zeroDeltas")
			removeDetached = self.prefBool("detachedHints")
			removals = set()
			for hintType, name in self.hintTypes:
				if self.prefBool(f"h{name}"):
					removals.add((hintType, True))
				if self.prefBool(f"v{name}"):
					removals.add((hintType, False))

			# collect what is to be done:
			theseFonts = fontsForScope(scope)
			jobs = [(thisFont, glyphsAndLayers(thisFont, scope)) for thisFont in theseFonts]
			totalGlyphs = sum(len(pairs) for _, pairs in jobs)
			if totalGlyphs == 0:
				self.setProgress(0, "⚠️ Nothing selected." if scope < 2 else "⚠️ No layers.")
				return

			print("Remove TT Hints Report")
			self.setProgress(0, "🛠️ Removing hints…")
			processedGlyphs = 0
			totalHints = 0
			totalZeroDeltas = 0
			for thisFont, pairs in jobs:
				print(f"\n📄 {fontFileName(thisFont, fullPath=True)}")
				for glyph, layers in pairs:
					self.setProgress(100 * processedGlyphs // totalGlyphs, f"🔠 {glyph.name}")
					for layer in layers:
						hintCount, zeroDeltaCount = self.removeHintsFromLayer(layer, removals, removeZeroDeltas, removeDetached)
						totalHints += hintCount
						totalZeroDeltas += zeroDeltaCount
					processedGlyphs += 1

			# final report:
			parts = [f"{totalHints:,} hint{'' if totalHints == 1 else 's'}"]
			if removeZeroDeltas:
				parts.append(f"{totalZeroDeltas:,} zero delta{'' if totalZeroDeltas == 1 else 's'}")
			summary = f"Removed {' and '.join(parts)}"
			self.setProgress(100, f"✅ {summary}.")
			Glyphs.showNotification(summary, f"Font: {Glyphs.font.familyName}" if len(theseFonts) == 1 else f"{len(theseFonts)} fonts")
			print(f"\nTOTAL: {summary}.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			self.w.status.set("❌ Error, see Macro Window.")
			print(f"Remove TT Hints Error: {e}")
			import traceback
			print(traceback.format_exc())


RemoveTTHints()
