# MenuTitle: Remove PS Hints
__doc__ = """
Removes PS Hints, selectively or completely, in the selected glyphs, a master, the complete font or all open fonts.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message, STEM, BOTTOMGHOST, TOPGHOST
from mekkablue import mekkaObject, fontFileName, makeWindowResizable
from hintscopes import scopes, scopeTooltip, detachedTooltip, isDetached, fontsForScope, glyphsAndLayers


class RemovePSHints(mekkaObject):
	prefDict = {
		"horizontalStemHints": 1,
		"verticalStemHints": 1,
		"ghostHints": 1,
		"scope": 2,
		"onlyDetached": 0,
		"includeBackgrounds": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 410
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove PS Hints",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Remove the following hints in", sizeStyle='small', selectable=True)
		self.w.scope = vanilla.PopUpButton("auto", scopes, sizeStyle='small', callback=self.SavePreferences)
		self.w.scope.setToolTip(scopeTooltip)
		self.w.descriptionText.setToolTip(scopeTooltip)

		self.w.horizontalStemHints = vanilla.CheckBox("auto", "Horizontal stem hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.horizontalStemHints.setToolTip("Removes the PostScript stem hints that control horizontal stems, i.e. hints in the y direction.")
		self.w.verticalStemHints = vanilla.CheckBox("auto", "Vertical stem hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.verticalStemHints.setToolTip("Removes the PostScript stem hints that control vertical stems, i.e. hints in the x direction.")
		self.w.ghostHints = vanilla.CheckBox("auto", "Ghost hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.ghostHints.setToolTip("Removes the top and bottom ghost hints, which hint edges that are not part of a stem.")
		self.w.onlyDetached = vanilla.CheckBox("auto", "Only remove detached hints", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.onlyDetached.setToolTip(f"Of the checked hint types, only removes the {detachedTooltip}. Hints that are still attached are kept.")
		self.w.includeBackgrounds = vanilla.CheckBox("auto", "Include backgrounds", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeBackgrounds.setToolTip("Also removes the hints in the background of each affected layer.")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove Hints", callback=self.RemovePSHintsMain)
		self.w.runButton.setToolTip("Removes the checked hint types in the chosen scope.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.descriptionText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-gap-[scope]-inset-|",
				"H:|-inset-[horizontalStemHints]-(>=inset)-|",
				"H:|-inset-[verticalStemHints]-gap-[onlyDetached]-(>=inset)-|",
				"H:|-inset-[ghostHints]-gap-[includeBackgrounds]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-inset-[status]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[scope]-headlineGap-[horizontalStemHints]-checkRow-[verticalStemHints]-checkRow-[ghostHints]-barGap-[progress(16)]-inset-[runButton]-inset-|",
				{"view1": self.w.descriptionText, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				{"view1": self.w.includeBackgrounds, "attribute1": "centerY", "view2": self.w.ghostHints, "attribute2": "centerY"},
				{"view1": self.w.onlyDetached, "attribute1": "centerY", "view2": self.w.verticalStemHints, "attribute2": "centerY"},
				# the stem and ghost checkboxes share one width, so the new column starts at one position, bottom-aligned with the ghost hints:
				{"view1": self.w.verticalStemHints, "attribute1": "width", "view2": self.w.horizontalStemHints, "attribute2": "width"},
				{"view1": self.w.ghostHints, "attribute1": "width", "view2": self.w.horizontalStemHints, "attribute2": "width"},
				{"view1": self.w.onlyDetached, "attribute1": "left", "view2": self.w.includeBackgrounds, "attribute2": "left"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "headlineGap": 10, "checkRow": 5, "barGap": 12},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def checkedTypeCount(self):
		checkBoxNames = ("horizontalStemHints", "verticalStemHints", "ghostHints")
		return sum(1 for name in checkBoxNames if getattr(self.w, name).get())

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.checkedTypeCount() > 0)
		self.w.status.set("🤖 Ready.")

	def setProgress(self, percent, text):
		"""Sets progress bar and status line, and redraws them right away, so they show while the script is busy."""
		self.w.progress.set(percent)
		self.w.status.set(text)
		self.w.getNSWindow().displayIfNeeded()

	def removeHintsFromLayer(self, primaryLayer, horizontalStemHints, verticalStemHints, ghostHints, includeBackgrounds, onlyDetached=False):
		delCount = 0

		layers = [primaryLayer]
		if includeBackgrounds:
			layers.append(primaryLayer.background)

		for layer in layers:
			for i in reversed(range(len(layer.hints))):
				hint = layer.hints[i]
				if hint.isPostScript and (not onlyDetached or isDetached(hint)):
					if horizontalStemHints and hint.horizontal and hint.type == STEM:
						del layer.hints[i]
						delCount += 1
					elif verticalStemHints and not hint.horizontal and hint.type == STEM:
						del layer.hints[i]
						delCount += 1
					elif ghostHints and hint.type in (BOTTOMGHOST, TOPGHOST):
						del layer.hints[i]
						delCount += 1
		return delCount

	def RemovePSHintsMain(self, sender):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			horizontalStemHints = self.prefBool("horizontalStemHints")
			verticalStemHints = self.prefBool("verticalStemHints")
			ghostHints = self.prefBool("ghostHints")
			includeBackgrounds = self.prefBool("includeBackgrounds")
			onlyDetached = self.prefBool("onlyDetached")
			scope = self.prefInt("scope")

			theseFonts = fontsForScope(scope)
			if not theseFonts:
				self.setProgress(0, "⚠️ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			# collect what is to be done:
			jobs = [(thisFont, glyphsAndLayers(thisFont, scope)) for thisFont in theseFonts]
			totalGlyphs = sum(len(pairs) for _, pairs in jobs)
			if totalGlyphs == 0:
				self.setProgress(0, "⚠️ Nothing selected." if scope < 2 else "⚠️ No layers.")
				return

			print("Remove PS Hints Report")
			self.setProgress(0, "🛠️ Removing hints…")
			processedGlyphs = 0
			deletedHintsCount = 0
			for thisFont, pairs in jobs:
				print(f"\n📄 {fontFileName(thisFont, fullPath=True)}")
				for glyph, layers in pairs:
					self.setProgress(100 * processedGlyphs // totalGlyphs, f"🔠 {glyph.name}")
					glyphCount = 0
					for layer in layers:
						glyphCount += self.removeHintsFromLayer(layer, horizontalStemHints, verticalStemHints, ghostHints, includeBackgrounds, onlyDetached)
					if glyphCount:
						print(f"  - Removed {glyphCount} hint{'' if glyphCount == 1 else 's'} from {glyph.name}")
					deletedHintsCount += glyphCount
					processedGlyphs += 1

			# final report:
			summary = f"Removed {deletedHintsCount:,} hint{'' if deletedHintsCount == 1 else 's'}"
			self.setProgress(100, f"✅ {summary}.")
			Glyphs.showNotification("Remove PS Hints", f"{summary}. Details in Macro Window.")
			print(f"\nTOTAL: {summary}.")
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			self.w.status.set("❌ Error, see Macro Window.")
			print(f"Remove PS Hints Error: {e}")
			import traceback
			print(traceback.format_exc())


RemovePSHints()
