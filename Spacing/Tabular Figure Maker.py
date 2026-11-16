# MenuTitle: Tabular Figure Maker
__doc__ = """
Takes existing .tf figures and spaces them tabularly, or creates them from existing default figures.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight
from GlyphsApp import Glyphs, GSComponent, Message
from mekkablue import mekkaObject, newGlyphWithName, UpdateButton, reportFontName


class TabularFigureSpacer(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"target": "one.tf",
		"suffix": ".tf",
		"createFromDefaultFigs": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Tabular Figure Spacer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Fit default figures in tabular spaces", sizeStyle="small", selectable=True)

		self.w.targetText = vanilla.TextBox("auto", "Reference glyph", sizeStyle="small", selectable=True)
		self.w.target = vanilla.ComboBox("auto", [], sizeStyle="small", callback=self.SavePreferences)
		self.w.updateButton = UpdateButton("auto", callback=self.update)

		self.w.suffixText = vanilla.TextBox("auto", "Tabular suffix", sizeStyle="small", selectable=True)
		self.w.suffix = vanilla.EditText("auto", ".tf", callback=self.SavePreferences, sizeStyle="small")

		self.w.createFromDefaultFigs = vanilla.CheckBox("auto", "Create glyphs if they are missing", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.createFromDefaultFigs.setToolTip("Creates glyphs for tab figures with default figures as components. Otherwise will just reset existing tab figures.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Tab", callback=self.TabularFigureSpacerMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels: right-aligned, one shared width
		labelNames = ("targetText", "suffixText")
		widestLabel = "targetText"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[targetText]-gap-[target]-gap-[updateButton]-inset-|",
				"H:|-inset-[suffixText]-gap-[suffix]-inset-|",
				"H:|-inset-[createFromDefaultFigs]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-headlineGap-[target]-row-[suffix]-headlineGap-[createFromDefaultFigs]-inset-[runButton]-inset-|",
				{"view1": self.w.targetText, "attribute1": "centerY", "view2": self.w.target, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.target, "attribute2": "centerY"},
				{"view1": self.w.suffixText, "attribute1": "centerY", "view2": self.w.suffix, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "headlineGap": 10},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.update()
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		if Glyphs.font:
			self.w.target.setItems([g.name for g in Glyphs.font.glyphs if ".tf" in g.name or ".tosf" in g.name])


	def TabularFigureSpacerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			font = Glyphs.font  # frontmost font
			if font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				reportName = reportFontName(font)
				print(f"Tabular Figure Spacer Report for {reportName}")
				print()

				if self.pref("createFromDefaultFigs"):
					figs = "0123456789"
					for fig in figs:
						niceName = Glyphs.niceGlyphName(fig)
						figName = f"{niceName}.{self.pref('suffix').lstrip('.')}"
						if not font.glyphs[figName]:
							newGlyph = newGlyphWithName(figName)
							font.glyphs.append(newGlyph)
							for layer in newGlyph.layers:
								layer.shapes.append(GSComponent(niceName))

				targetGlyph = font.glyphs[self.pref("target")]
				tabFigs = [g for g in font.glyphs if g.name.endswith(self.pref("suffix"))]
				if targetGlyph:
					for thisGlyph in tabFigs:
						for master in font.masters:
							mID = master.id
							targetLayer = targetGlyph.layers[mID]
							layer = thisGlyph.layers[mID]
							for thisComponent in layer.components:
								thisComponent.alignment = -1 # can be freely positioned

							if targetGlyph == thisGlyph:
								continue

							widthDiff = targetLayer.width - layer.width
							sidebearings = layer.LSB + layer.RSB
							leftPercentage = layer.LSB / sidebearings if sidebearings else 0.5
							layer.LSB += round(widthDiff * leftPercentage)
							layer.width = targetLayer.width
						if thisGlyph != targetGlyph:  # a glyph must not refer to itself
							thisGlyph.widthMetricsKey = f"={self.pref('target')}"

				names = [g.name for g in tabFigs]
				font.newTab("/" + "/".join(names))

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Tabular Figure Spacer Error: {e}")
			import traceback
			print(traceback.format_exc())


TabularFigureSpacer()
