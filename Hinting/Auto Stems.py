# MenuTitle: Auto Stems
__doc__ = """
Derive one H and one V stem value for all your masters by measuring certain shapes in your font.
"""

import vanilla
from mekkablue import mekkaObject, UpdateButton, reportFontName, makeWindowResizable
from GlyphsApp import Glyphs, GSMetric, Message
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from Foundation import NSPoint

whichMeasure = (
	"bounds",
	"diameter",
)

whichShape = (
	"first shape",
	"second shape",
	"last shape",
	"smallest shape",
	"largest shape",
)


class AutoStems(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"hMeasure": 0,
		"hShape": 3,
		"hStemGlyph": "f",
		"vMeasure": 1,
		"vShape": 0,
		"vStemGlyph": "idotaccent",
		"overwriteExisting": 1,
		"allFonts": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 460
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Auto Stems",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15
		glyphNames = self.glyphNames()
		self.w.descriptionText = vanilla.TextBox("auto", "Measure shapes in the font and derive stem entries", sizeStyle="small", selectable=True)

		self.w.vText1 = vanilla.TextBox("auto", "V Stem", sizeStyle="small", selectable=True)
		self.w.vMeasure = vanilla.PopUpButton("auto", whichMeasure, sizeStyle="small", callback=self.SavePreferences)
		self.w.vMeasure.setToolTip("Bounds: the width of the enclosing rectangle for the selected shape.\n\nDiameter: the distance between the outermost points of the shape when cut horizontally in the center.")
		self.w.vText2 = vanilla.TextBox("auto", "of", sizeStyle="small", selectable=True)
		self.w.vShape = vanilla.PopUpButton("auto", whichShape, sizeStyle="small", callback=self.SavePreferences)
		self.w.vShape.setToolTip("Which shape in the glyph to measure for the vertical stem.")
		self.w.vText3 = vanilla.TextBox("auto", "of", sizeStyle="small", selectable=True)
		self.w.vStemGlyph = vanilla.ComboBox("auto", glyphNames, sizeStyle="small", callback=self.SavePreferences)
		self.w.vStemGlyph.setToolTip("Pick a glyph to measure for the vertical stem.")
		self.w.vReset = UpdateButton("auto", callback=self.update)
		resetToolTip = "Reload the glyph list of the frontmost font."
		self.w.vReset.setToolTip(resetToolTip)

		self.w.hText1 = vanilla.TextBox("auto", "H Stem", sizeStyle="small", selectable=True)
		self.w.hMeasure = vanilla.PopUpButton("auto", whichMeasure, sizeStyle="small", callback=self.SavePreferences)
		self.w.hMeasure.setToolTip("Bounds: the height of the enclosing rectangle for the selected shape.\n\nDiameter: the distance between the outermost points of the shape when cut vertically in the center.")
		self.w.hText2 = vanilla.TextBox("auto", "of", sizeStyle="small", selectable=True)
		self.w.hShape = vanilla.PopUpButton("auto", whichShape, sizeStyle="small", callback=self.SavePreferences)
		self.w.hShape.setToolTip("Which shape in the glyph to measure for the horizontal stem.")
		self.w.hText3 = vanilla.TextBox("auto", "of", sizeStyle="small", selectable=True)
		self.w.hStemGlyph = vanilla.ComboBox("auto", glyphNames, sizeStyle="small", callback=self.SavePreferences)
		self.w.hStemGlyph.setToolTip("Pick a glyph to measure for the horizontal stem.")
		self.w.hReset = UpdateButton("auto", callback=self.update)
		self.w.hReset.setToolTip(resetToolTip)

		self.w.overwriteExisting = vanilla.CheckBox("auto", "⚠️ Overwrite existing stems", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwriteExisting.setToolTip("If checked, will delete existing stem values before adding its measurements. Be careful.")

		self.w.allFonts = vanilla.CheckBox("auto", "Process ⚠️ ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.setToolTip("If checked, will process all fonts currently opened in Glyphs. Otherwise just the frontmost font.")

		# Status line and Run Button:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.runButton = vanilla.Button("auto", "Add Stems", callback=self.AutoStemsMain)
		self.w.runButton.setToolTip("Measures the chosen glyphs and adds the stem values to the font masters.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels hug their text, so the combo boxes take the leftover width:
		for labelName in ("vText1", "hText1", "vText2", "hText2", "vText3", "hText3"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		for label in (self.w.vText1, self.w.hText1):
			label.getNSTextField().setAlignment_(NSTextAlignmentRight)
		for popup in (self.w.vMeasure, self.w.hMeasure, self.w.vShape, self.w.hShape):
			popup.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		rules = [
			"H:|-inset-[descriptionText]-inset-|",
			"H:|-inset-[vText1]-gap-[vMeasure]-gap-[vText2]-gap-[vShape]-gap-[vText3]-gap-[vStemGlyph(>=100)]-gap-[vReset]-inset-|",
			"H:|-inset-[hText1]-gap-[hMeasure]-gap-[hText2]-gap-[hShape]-gap-[hText3]-gap-[hStemGlyph(>=100)]-gap-[hReset]-inset-|",
			"H:|-inset-[overwriteExisting]-(>=inset)-|",
			"H:|-inset-[allFonts]-(>=gap)-[runButton(>=70)]-inset-|",
			"H:|-inset-[status]-inset-|",
			"V:|-gap-[descriptionText]-row-[vStemGlyph]-row-[hStemGlyph]-row-[overwriteExisting]-row-[status]-gap-[runButton]-inset-|",
			{"view1": self.w.allFonts, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			{"view1": self.w.hText1, "attribute1": "width", "view2": self.w.vText1, "attribute2": "width"},
			{"view1": self.w.hMeasure, "attribute1": "width", "view2": self.w.vMeasure, "attribute2": "width"},
			{"view1": self.w.hShape, "attribute1": "width", "view2": self.w.vShape, "attribute2": "width"},
		]
		# one baseline per row:
		for direction in "vh":
			combo = getattr(self.w, f"{direction}StemGlyph")
			for suffix in ("Text1", "Measure", "Text2", "Shape", "Text3", "Reset"):
				rules.append({"view1": getattr(self.w, direction + suffix), "attribute1": "centerY", "view2": combo, "attribute2": "centerY"})
		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "row": 6})

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def glyphNames(self):
		font = Glyphs.font
		if not font:
			return []
		return [g.name for g in font.glyphs]

	def update(self, sender=None):
		glyphNames = self.glyphNames()
		if sender == self.w.hReset:
			self.w.hStemGlyph.setItems(glyphNames)
		if sender == self.w.vReset:
			self.w.vStemGlyph.setItems(glyphNames)

	def measureLayer(self, layer, measure, shape, v=True):
		layerCopy = layer.copyDecomposedLayer()
		layerCopy.parent = layer.parent

		if shape == 1 and len(layerCopy.shapes) < 2:  # second
			raise ValueError(f"{layer.parent.name} has fewer than two shapes, cannot measure its second shape")

		if shape == 0:  # first
			s = layerCopy.shapes[0]
		elif shape == 1:  # second
			s = layerCopy.shapes[1]
		elif shape == 2:  # last
			s = layerCopy.shapes[-1]
		elif shape == 3:  # smallest
			s = sorted(layerCopy.shapes, key=lambda thisShape: thisShape.bounds.size.height * thisShape.bounds.size.width)[0]
		elif shape == 4:  # largest
			s = sorted(layerCopy.shapes, key=lambda thisShape: thisShape.bounds.size.height * thisShape.bounds.size.width * -1)[0]

		# reduce layer to just the shape we want to measure
		# l.setShapes_([s])
		for i in range(len(layerCopy.shapes) - 1, -1, -1):
			if layerCopy.shapes[i] != s:
				del layerCopy.shapes[i]

		bounds = layerCopy.bounds
		if v:
			if measure == 0:  # bounds
				return bounds.size.width
			elif measure == 1:  # diameter
				midY = bounds.origin.y + 0.5 * bounds.size.height
				x1 = bounds.origin.x - 50
				x2 = bounds.origin.x + bounds.size.width + 50
				cuts = layerCopy.intersectionsBetweenPoints(NSPoint(x1, midY), NSPoint(x2, midY), components=True)
				stemMeasurement = float(round(cuts[-2].x - cuts[1].x))
				return abs(stemMeasurement)
		else:  # h
			if measure == 0:  # bounds
				return bounds.size.height
			elif measure == 1:  # diameter
				midX = bounds.origin.x + 0.5 * bounds.size.width
				y1 = bounds.origin.y - 50
				y2 = bounds.origin.y + bounds.size.height + 50
				cuts = layerCopy.intersectionsBetweenPoints(NSPoint(midX, y1), NSPoint(midX, y2), components=True)
				stemMeasurement = float(round(cuts[-2].y - cuts[1].y))
				return abs(stemMeasurement)

	def AutoStemsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			hMeasure = self.pref("hMeasure")
			hShape = self.pref("hShape")
			hStemGlyph = self.pref("hStemGlyph")
			vMeasure = self.pref("vMeasure")
			vShape = self.pref("vShape")
			vStemGlyph = self.pref("vStemGlyph")
			overwriteExisting = self.pref("overwriteExisting")
			allFonts = self.pref("allFonts")

			if allFonts:
				fonts = Glyphs.fonts
			else:
				fonts = (Glyphs.font, ) if Glyphs.font else ()

			if not fonts:
				self.setStatus("⚠️ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			self.setStatus(f"🛠️ Processing {len(fonts)} font(s)…")
			currentItem = None
			measuredCount = 0
			for f in fonts:
				reportName = reportFontName(f)
				print(f"Auto Stems Report for {reportName}")
				print()

				# check for the glyphs first, before the stems of the font are touched:
				missingGlyphNames = [glyphName for glyphName in (vStemGlyph, hStemGlyph) if not f.glyphs[glyphName]]
				if missingGlyphNames:
					self.setStatus(f"⚠️ Missing in {f.familyName}: {', '.join(missingGlyphNames)}.")
					print(f"❌ Missing in this font, cannot measure: {', '.join(missingGlyphNames)}. Skipping font.\n")
					Message(title="Auto Stems: Glyph Missing", message=f"Cannot measure stems in {f.familyName}, because the font has no glyph named {' or '.join(missingGlyphNames)}.", OKButton=None)
					continue

				if overwriteExisting:
					f.setStems_(())

				stem = GSMetric()
				stem.name = "V"
				stem.horizontal = False
				stem.type = 0
				f.stems.append(stem)
				vID = stem.id

				stem = GSMetric()
				stem.name = "H"
				stem.horizontal = True
				stem.type = 0
				f.stems.append(stem)
				hID = stem.id

				vGlyph = f.glyphs[vStemGlyph]  # idotless
				hGlyph = f.glyphs[hStemGlyph]  # f

				for m in f.masters:
					mID = m.id
					currentItem = m.name
					self.setStatus(f"🔠 {m.name}")

					# measure idotless
					vStem = self.measureLayer(vGlyph.layers[mID], vMeasure, vShape, v=True)

					# measure f
					hStem = self.measureLayer(hGlyph.layers[mID], hMeasure, hShape, v=False)

					# set stems:
					print(f"V {vStem} H {hStem}: {m.name}")
					m.stems[vID] = vStem
					m.stems[hID] = hStem
					measuredCount += 1

				print()

			if measuredCount:
				self.setStatus(f"✅ Set stems in {measuredCount} master(s).")
			else:
				self.setStatus("⚠️ No stems set.")

			if not allFonts and f is not None:
				f.parent.windowController().showFontInfoWindowWithTabSelected_(1) # master tab index

			self.w.close()  # delete if you want window to stay open
			print("\nDone.")

		except Exception as e:
			self.setStatus(f"❌ Error at {currentItem or 'start'}. Details in Macro Window.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Auto Stems Error: {e}")
			import traceback
			print(traceback.format_exc())


AutoStems()
