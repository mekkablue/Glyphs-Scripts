# MenuTitle: Compress Glyph
__doc__ = """
Compresses all instances of a glyph to its respective group kerning.
"""

import vanilla
from mekkablue import mekkaObject, match, reportFontName, UpdateButton
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
)


class CompressGlyph(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"glyphName": "V",
		"compressLeft": 1,
		"compressRight": 1,
		"allMasters": 0,
		"verbose": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Compress Glyph",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "In frontmost font, compress kernings for this glyph:", sizeStyle="small", selectable=True)

		self.w.glyphName = vanilla.ComboBox("auto", (), callback=self.SavePreferences)
		self.w.glyphName.setToolTip("The name of the glyph you want to compress. Use * as wildcard for matching many glyphs.")
		self.w.updateButton = UpdateButton("auto", callback=self.update)
		self.w.updateButton.setToolTip("Reloads the glyph names of the frontmost font into the combo box.")

		self.w.compressText = vanilla.TextBox("auto", "Compress when glyph is", sizeStyle="small", selectable=True)
		self.w.compressLeft = vanilla.CheckBox("auto", "left side", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.compressRight = vanilla.CheckBox("auto", "right side of pair", value=False, callback=self.SavePreferences, sizeStyle="small")

		self.w.allMasters = vanilla.CheckBox("auto", "⚠️ ALL masters", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose = vanilla.CheckBox("auto", "Verbose report in Macro window", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Status line and Run Button:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton = vanilla.Button("auto", "Compress", callback=self.CompressGlyphMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[glyphName]-gap-[updateButton]-inset-|",
				"H:|-inset-[compressText]-gap-[compressLeft]-gap-[compressRight]-(>=inset)-|",
				"H:|-inset-[allMasters]-inset-[verbose]-(>=inset)-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[glyphName]-gap-[compressLeft]-checkRow-[allMasters]-inset-[runButton]-inset-|",
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.glyphName, "attribute2": "centerY"},
				{"view1": self.w.compressText, "attribute1": "centerY", "view2": self.w.compressLeft, "attribute2": "centerY"},
				{"view1": self.w.compressRight, "attribute1": "centerY", "view2": self.w.compressLeft, "attribute2": "centerY"},
				{"view1": self.w.verbose, "attribute1": "centerY", "view2": self.w.allMasters, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.update()
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		font = Glyphs.font
		if not font:
			self.w.glyphName.setItems(())
			return
		names = [g.name for g in font.glyphs]
		names.extend(sorted(set(f'*{g.name[g.name.find("."):]}' for g in font.glyphs if "." in g.name and not g.name.startswith("."))))
		self.w.glyphName.setItems(names)

	def CompressGlyphMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			glyphName = self.pref("glyphName")
			compressLeft = self.pref("compressLeft")
			compressRight = self.pref("compressRight")
			allMasters = self.pref("allMasters")
			verbose = self.pref("verbose")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				reportName = reportFontName(thisFont)
				print(f"Compress Glyph Report for {reportName}")
				print()

				fontKerning = thisFont.kerning
				if not fontKerning:
					Message(
						title="No kerning in font",
						message=f"The current font ({thisFont.familyName}) appears to have no kerning at all.",
						OKButton="Oops",
					)
					return

				glyphNames = []
				if "*" in glyphName:
					for g in thisFont.glyphs:
						if match(glyphName, g.name):
							glyphNames.append(g.name)
				else:
					glyphNames.append(glyphName)

				if not glyphNames:
					Message(
						title=f"No glyphs matching ‘{glyphName}’",
						message=f"In the current font ({thisFont.familyName}), there is no glyph like ‘{glyphName}’.",
						OKButton="Oops",
					)
					return

				totalCount = 0
				for glyphName in glyphNames:
					glyph = thisFont.glyphs[glyphName]
					if glyph is None:
						self.w.status.set(f"⚠️ No glyph ‘{glyphName}’ in font.")
						print(f"⚠️ No glyph named ‘{glyphName}’ in the font. Skipping.\n")
						continue
					self.w.status.set(f"🔠 {glyphName}")
					print(f"🗜️ Compressing {glyphName}...")

					gID = glyph.id
					deletePairs = []
					addPairs = []
					for m in thisFont.masters:
						if not allMasters and thisFont.selectedFontMaster != m:
							continue
						print(f"Ⓜ️ Scanning {m.name}...")
						kerning = fontKerning[m.id]
						for leftKey in kerning.keys():
							for rightKey in kerning[leftKey].keys():
								if compressLeft and leftKey == gID and glyph.rightKerningGroup:
									deletePairs.append((m.id, leftKey, rightKey))
									rightSide = None
									if rightKey.startswith("@"):
										rightSide = rightKey
									else:
										rightGlyph = thisFont.glyphForId_(rightKey)
										if rightGlyph:
											rightSide = rightGlyph.name
									if rightSide:
										value = kerning[leftKey][rightKey]
										addPairs.append((m.id, f"@MMK_L_{glyph.rightKerningGroup}", rightSide, value))

								if compressRight and rightKey == gID and glyph.leftKerningGroup:
									deletePairs.append((m.id, leftKey, rightKey))
									leftSide = None
									if leftKey.startswith("@"):
										leftSide = leftKey
									else:
										leftGlyph = thisFont.glyphForId_(leftKey)
										if leftGlyph:
											leftSide = leftGlyph.name
									if leftSide:
										value = kerning[leftKey][rightKey]
										addPairs.append((m.id, leftSide, f"@MMK_R_{glyph.leftKerningGroup}", value))

					for addPair in addPairs:
						try:
							masterID, left, right, value = addPair
							mName = thisFont.masters[masterID].name
							thisFont.setKerningForPair(masterID, left, right, value)
							if verbose:
								print(f"Ⓜ️ {mName} 👈 {left} 👉 {right}: {value}")
						except Exception as e:  # noqa: F841
							print(f"⚠️ could not add pair: {left} - {right} ({value}, MID: {masterID})")
							# raise e

					for deletePair in deletePairs:
						try:
							masterID, leftKey, rightKey = deletePair
							thisFont.removeKerningForPair(
								masterID,
								leftKey if leftKey.startswith("@") else thisFont.glyphForId_(leftKey).name,
								rightKey if rightKey.startswith("@") else thisFont.glyphForId_(rightKey).name,
							)
						except Exception as e:  # noqa: F841
							print(f"⚠️ could not delete pair: {leftKey} - {rightKey}, MID: {masterID}")
							# raise e

					compressCount = len(deletePairs)
					totalCount += compressCount
					self.w.status.set(f"✅ {compressCount} kerns: {glyphName}")
					print(f"✅ Compressed {compressCount} kern pairs with {glyphName} (L: {glyph.leftKerningGroup}, R: {glyph.rightKerningGroup}).\n")

				if len(glyphNames) > 1:
					self.w.status.set(f"✅ {totalCount} kerns for {len(glyphNames)} glyphs")
					print(f"Compressed {len(glyphNames)} glyphs: {', '.join(glyphNames)}.\n")

			print("Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Compress Glyph Error: {e}")
			import traceback
			print(traceback.format_exc())


CompressGlyph()
