# MenuTitle: Steal Kerning Groups
__doc__ = """
Copies kerning groups from one font to another.
"""

import vanilla
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, reportFontName, fontFileName, UpdateButton


def menuForFonts(fonts):
	menu = []
	for i, font in enumerate(fonts):
		menu.append(f"{i + 1}. {font.familyName} ({fontFileName(font)})")
	return menu


class StealKerningGroupsfromFont(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"sourceFont": 0,
		"targetFont": 0,
		"allGroups": 1,
		"overwriteExisting": 1,
		"resetGroupsInTarget": 0,
		"verbose": 0,
	}

	currentFonts = Glyphs.fonts

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Steal Kerning Groups",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Copy kerning groups from Source Font to Target Font:", sizeStyle="small", selectable=True)

		self.w.sourceFontText = vanilla.TextBox("auto", "Source font:", sizeStyle="small", selectable=True)
		self.w.sourceFont = vanilla.PopUpButton("auto", (), sizeStyle="small", callback=self.SavePreferences)
		self.w.updateButton = UpdateButton("auto", callback=self.updateUI)
		self.w.updateButton.setToolTip("Will update all the menus and buttons of this window. Click here if you opened or closed a font since you invoked the script, or after you changed the source font.")
		tooltip = "The font from which the kerning groups are taken."
		self.w.sourceFont.setToolTip(tooltip)
		self.w.sourceFontText.setToolTip(tooltip)

		self.w.targetFontText = vanilla.TextBox("auto", "Target font:", sizeStyle="small", selectable=True)
		self.w.targetFont = vanilla.PopUpButton("auto", (), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font that receives the kerning groups."
		self.w.targetFont.setToolTip(tooltip)
		self.w.targetFontText.setToolTip(tooltip)

		self.w.allGroups = vanilla.CheckBox("auto", "Copy ⚠️ ALL groups (i.e., ignore selection in source font)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allGroups.setToolTip("If unchecked, will only transfer groups of glyphs selected in source font.")

		self.w.overwriteExisting = vanilla.CheckBox("auto", "Overwrite existing groups in target font", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwriteExisting.setToolTip("If unchecked, will keep existing groups in the target font, and only set groups when the glyph does not have any yet.")

		self.w.resetGroupsInTarget = vanilla.CheckBox("auto", "⚠️ Reset groups in target font before copying", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.resetGroupsInTarget.setToolTip("Will delete ALL kerning groups in target font prior to transfering the source font’s groups.")

		self.w.verbose = vanilla.CheckBox("auto", "Verbose reporting in Macro window (slow)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose.setToolTip("Will report progress per glyph in Window > Macro Panel. Useful for debugging.")

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Steal", callback=self.StealKerningGroupsfromFontMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned, hug their text and share one width:
		labelNames = ("sourceFontText", "targetFontText")
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[sourceFontText]-gap-[sourceFont]-gap-[updateButton]-inset-|",
				"H:|-inset-[targetFontText]-gap-[targetFont]-inset-|",
				"H:|-inset-[allGroups]-(>=inset)-|",
				"H:|-inset-[overwriteExisting]-(>=inset)-|",
				"H:|-inset-[resetGroupsInTarget]-(>=inset)-|",
				"H:|-inset-[verbose]-(>=inset)-|",
				"H:|-inset-[status]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[sourceFont]-row-[targetFont]-row-[allGroups]-checkRow-[overwriteExisting]-checkRow-[resetGroupsInTarget]-checkRow-[verbose]-inset-[runButton]-inset-|",
				{"view1": self.w.sourceFontText, "attribute1": "centerY", "view2": self.w.sourceFont, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.sourceFont, "attribute2": "centerY"},
				{"view1": self.w.targetFontText, "attribute1": "centerY", "view2": self.w.targetFont, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.sourceFontText, "attribute1": "width", "view2": self.w.targetFontText, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "headlineGap": 10, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.currentFonts = Glyphs.fonts
		menu = menuForFonts(self.currentFonts)
		if menu:
			self.w.sourceFont.setItems(menu)
			self.w.sourceFont.set(self.pref("sourceFont"))
			self.w.targetFont.setItems(menu)
			self.w.targetFont.set(self.pref("targetFont"))
		self.w.runButton.enable(self.pref("sourceFont") != self.pref("targetFont"))

	def StealKerningGroupsfromFontMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if len(self.currentFonts) < 2:
				Message(title="Not Enough Fonts", message="The script requires at least two fonts.", OKButton=None)
				return

			print("Steal Kerning Groups Report:")
			sourceFont = self.currentFonts[self.pref("sourceFont")]
			targetFont = self.currentFonts[self.pref("targetFont")]
			for font, sourceOrTarget in zip((sourceFont, targetFont), ("Source", "Target")):
				reportName = reportFontName(font)
				print(f"\n{sourceOrTarget}: {reportName}")
			print()

			verbose = self.prefBool("verbose")
			if self.pref("resetGroupsInTarget"):
				print("Deleting kerning groups in target font...")
				for glyph in targetFont.glyphs:
					self.w.status.set(f"🔠 {glyph.name}")
					if glyph.leftKerningGroup:
						glyph.leftKerningGroup = None
					if glyph.rightKerningGroup:
						glyph.rightKerningGroup = None
					if not verbose:
						continue
					print(f"  🧟 {glyph.name}")
				if verbose:
					print()

			if self.pref("allGroups"):
				glyphNames = [g.name for g in sourceFont.glyphs]
			else:
				glyphNames = [layer.parent.name for layer in sourceFont.selectedLayers]

			overwriteExisting = self.prefBool("overwriteExisting")
			print("Writing kerning groups in target font...")
			for glyphName in glyphNames:
				sourceGlyph = sourceFont.glyphs[glyphName]
				targetGlyph = targetFont.glyphs[glyphName]
				if not targetGlyph:
					if verbose:
						print(f"  🚫 Skipping {glyphName}, not in target font.")
					continue
				self.w.status.set(f"🔠 {glyphName}")
				if sourceGlyph.leftKerningGroup and overwriteExisting or not targetGlyph.leftKerningGroup:
					targetGlyph.leftKerningGroup = sourceGlyph.leftKerningGroup
				if sourceGlyph.rightKerningGroup and overwriteExisting or not targetGlyph.rightKerningGroup:
					targetGlyph.rightKerningGroup = sourceGlyph.rightKerningGroup
				if not verbose:
					continue
				print(
					f"  🔤 {glyphName}"
					f"  ◀️ {targetGlyph.leftKerningGroup if targetGlyph.leftKerningGroup else '🚫'}"
					f"  ▶️ {targetGlyph.rightKerningGroup if targetGlyph.rightKerningGroup else '🚫'}"
				)

			# self.w.close()  # delete if you want window to stay open
			self.w.status.set("✅ Done. Details in Macro Window.")
			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Steal Kerning Groups from Font Error: {e}")
			import traceback
			print(traceback.format_exc())


StealKerningGroupsfromFont()
