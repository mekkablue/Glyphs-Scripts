# MenuTitle: Merge CPAL Layers into Master Layer
__doc__ = """
Takes all CPAL/COLR layers and puts copies of their shapes into the master layer.
"""

import vanilla
from mekkablue import mekkaObject, reportFontName, SteppingEditText, integerFormatter, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
)


allOptions = (
	"selected CPAL/COLR glyphs in current font",
	"⚠️ ALL CPAL/COLR glyphs in current font",
	"⚠️ ALL CPAL/COLR glyphs in ⚠️ ALL fonts",
)


class MergeCPALLayersIntoMasterLayer(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"overwrite": 1,
		"all": 0,
		"verbose": 0,
		"removeOverlap": 1,
		"removeSmallItems": 1,
		"removeSmallItemsThreshold": 400,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Merge CPAL Layers into Master Layer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Merge CPAL/COLR shapes into master layers", sizeStyle="small", selectable=True)

		self.w.allText = vanilla.TextBox("auto", "for:", sizeStyle="small", selectable=True)
		self.w.all = vanilla.PopUpButton("auto", allOptions, sizeStyle="small", callback=self.SavePreferences)
		tooltipText = "Choose which glyphs get their color layers merged: the selected glyphs, all color glyphs of the current font, or of all open fonts."
		self.w.allText.setToolTip(tooltipText)
		self.w.all.setToolTip(tooltipText)

		self.w.removeOverlap = vanilla.CheckBox("auto", "Remove overlap and tidy up paths", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.removeOverlap.setToolTip("Removes overlaps and cleans up the paths in the merged master layer.")

		self.w.removeSmallItems = vanilla.CheckBox("auto", "Remove items smaller than", value=False, callback=self.SavePreferences, sizeStyle="small")
		formatter = integerFormatter(0)
		self.w.removeSmallItemsThreshold = SteppingEditText("auto", "400", callback=self.SavePreferences, sizeStyle="small", formatter=formatter)
		self.w.removeSmallItemsText = vanilla.TextBox("auto", "square units", sizeStyle="small")
		tooltipText = "Deletes merged shapes with an area below this threshold, in square units."
		self.w.removeSmallItems.setToolTip(tooltipText)
		self.w.removeSmallItemsThreshold.setToolTip(tooltipText)
		self.w.removeSmallItemsText.setToolTip(tooltipText)

		self.w.overwrite = vanilla.CheckBox("auto", "Overwrite existing master layers", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwrite.setToolTip("If checked, replaces the existing shapes of the master layer. Otherwise adds the color shapes to them.")

		self.w.verbose = vanilla.CheckBox("auto", "Verbose reporting in Macro window (slow)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose.setToolTip("Prints a line for every glyph and master, including skipped ones. Can be slow in large fonts.")

		# Status line and Run Button:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.runButton = vanilla.Button("auto", "Merge", callback=self.MergeCPALLayersIntoMasterLayerMain)
		self.w.runButton.setToolTip("Merges the color layers into the master layers.")
		self.w.setDefaultButton(self.w.runButton)

		# the status line takes the leftover width, the button stays as wide as its title needs:
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the popup takes the leftover width:
		self.w.allText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[allText]-gap-[all]-inset-|",
				"H:|-inset-[removeOverlap]-(>=inset)-|",
				"H:|-inset-[removeSmallItems]-gap-[removeSmallItemsThreshold(50)]-gap-[removeSmallItemsText]-(>=inset)-|",
				"H:|-inset-[overwrite]-(>=inset)-|",
				"H:|-inset-[verbose]-(>=inset)-|",
				"H:|-inset-[status]-gap-[runButton(>=90)]-inset-|",
				# the stack has one checkbox with a field behind it, so all rows take the wider gap:
				"V:|-gap-[descriptionText]-row-[all]-stackRow-[removeOverlap]-stackRow-[removeSmallItems]-stackRow-[overwrite]-stackRow-[verbose]-inset-[runButton]-inset-|",
				{"view1": self.w.allText, "attribute1": "centerY", "view2": self.w.all, "attribute2": "centerY"},
				{"view1": self.w.removeSmallItemsThreshold, "attribute1": "centerY", "view2": self.w.removeSmallItems, "attribute2": "centerY"},
				{"view1": self.w.removeSmallItemsText, "attribute1": "centerY", "view2": self.w.removeSmallItems, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "stackRow": 8},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.removeSmallItemsThreshold.enable(bool(self.w.removeSmallItems.get()))

	def MergeCPALLayersIntoMasterLayerMain(self, sender=None):
		currentItemName = None
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if not Glyphs.font:
				self.setStatus("⚠️ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				self.setStatus("🛠️ Processing…")
				countGlyphs = 0
				if self.pref("all") > 1:  # 0, 1 = current font; 2 = all fonts
					theseFonts = Glyphs.fonts
				else:
					theseFonts = (Glyphs.font, )

				for thisFont in theseFonts:
					reportName = reportFontName(thisFont)
					print(f"Merge CPAL Layers into Master Layer Report for {reportName}")
					print()

					if self.pref("all") == 0:
						theseGlyphs = [layer.parent for layer in thisFont.selectedLayers]
					else:
						theseGlyphs = thisFont.glyphs

					for thisGlyph in theseGlyphs:
						for m in thisFont.masters:
							currentItemName = f"{thisGlyph.name} ({m.name})"
							self.setStatus(f"🔠 {currentItemName}")
							# collect shapes from color layers
							collectedShapes = []
							for colorLayer in thisGlyph.layers:
								if not colorLayer.isColorPaletteLayer():
									continue
								if colorLayer.associatedMasterId != m.id:
									continue
								if colorLayer.attributeForKey_("colorPalette") is None:
									continue
								for shape in colorLayer.shapes:
									collectedShapes.append(shape.copy())

							# add to master layer
							if not collectedShapes:
								if self.pref("verbose"):
									print(f"🚫 {thisGlyph.name} Ⓜ️ {m.name}: no color layers, skipping.")
								continue
							masterLayer = thisGlyph.layers[m.id]
							if self.pref("overwrite"):
								masterLayer.shapes = None
							for shape in collectedShapes:
								masterLayer.shapes.append(shape)
							masterLayer.decomposeComponents()
							if self.pref("removeOverlap"):
								masterLayer.removeOverlap()
								masterLayer.cleanUpPaths()
							if self.pref("removeSmallItems"):
								threshold = self.prefFloat("removeSmallItemsThreshold")
								for i in range(len(masterLayer.shapes) - 1, -1, -1):
									shape = masterLayer.shapes[i]
									if abs(shape.area()) < threshold:
										del masterLayer.shapes[i]

							print(f"🌈 {thisGlyph.name}: merged color shapes into Ⓜ️ {m.name}")
							countGlyphs += 1
					print()

				self.setStatus(f"✅ Merged {countGlyphs} glyph{'' if countGlyphs == 1 else 's'}." if countGlyphs else "⚠️ No color layers found to merge.")
				print(f"✅ Done. Merged {countGlyphs} glyph{'' if countGlyphs == 1 else 's'} in {len(theseFonts)} font{'' if len(theseFonts) == 1 else 's'}.")

		except Exception as e:
			self.setStatus(f"❌ Error at {currentItemName}. Details in Macro Window." if currentItemName else "❌ Error. Details in Macro Window.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Merge CPAL Layers into Master Layer Error: {e}")
			import traceback
			print(traceback.format_exc())


MergeCPALLayersIntoMasterLayer()
