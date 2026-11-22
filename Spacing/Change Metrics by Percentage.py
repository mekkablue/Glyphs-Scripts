# MenuTitle: Change Metrics by Percentage
__doc__ = """
Increase sidebearings of selected glyphs by a percentage value.
"""

import vanilla
from mekkablue import mekkaObject, SteppingEditText, decimalFormatter
from GlyphsApp import Glyphs, Message
from AppKit import NSColor, NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut


class ChangeMetricsbyPercentage(mekkaObject):
	prefDict = {
		"LSB": True,
		"RSB": True,
		"changeValue": 10,
	}

	def __init__(self):
		windowWidth = 450
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Change Metrics of Selected Glyphs by Percentage",
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		inset = 15
		formatter = decimalFormatter(fractionDigits=2)
		self.w.text_1 = vanilla.TextBox("auto", "Increase", sizeStyle='small')
		self.w.LSB = vanilla.CheckBox("auto", "LSB", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.LSB.setToolTip("If enabled, changes the left sidebearings of the selected glyphs.")
		self.w.RSB = vanilla.CheckBox("auto", "RSB by", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.RSB.setToolTip("If enabled, changes the right sidebearings of the selected glyphs.")
		self.w.changeValue = SteppingEditText("auto", "10", sizeStyle='small', callback=self.SavePreferences, formatter=formatter)
		self.w.changeValue.setToolTip("Percentage by which the sidebearings are changed. Negative values decrease them.")
		self.w.text_3 = vanilla.TextBox("auto", "%", sizeStyle='small')
		self.w.revertButton = vanilla.Button("auto", "⟲ Revert", sizeStyle='small', callback=self.ChangeMetricsbyPercentageMain)
		self.w.revertButton.setToolTip("Reverses a previous change by the same percentage, i.e., divides the sidebearings by the factor.")
		self.w.runButton = vanilla.Button("auto", "Change", sizeStyle='small', callback=self.ChangeMetricsbyPercentageMain)
		self.w.runButton.setToolTip("Changes the sidebearings of the selected glyphs by the percentage.")

		self.w.setDefaultButton(self.w.runButton)

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		rowViews = (self.w.text_1, self.w.LSB, self.w.RSB, self.w.text_3, self.w.revertButton, self.w.runButton)
		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-gap-[LSB]-gap-[RSB]-gap-[changeValue(55)]-3-[text_3]-(>=gap)-[revertButton(>=60)]-gap-[runButton(>=60)]-inset-|",
				"H:|-inset-[status]-inset-|",
				"V:|-inset-[changeValue]-gap-[status]-inset-|",
			] + [
				{"view1": view, "attribute1": "centerY", "view2": self.w.changeValue, "attribute2": "centerY"}
				for view in rowViews
			],
			metrics={"inset": inset, "gap": 8},
		)

		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()

	def findGlyphsThatReferenceGlyphAsComponent(self, glyph):
		Font = Glyphs.font
		glyphs = []
		for g in Font.glyphs:
			if g != glyph and glyph.name in [c.componentName for c in g.layers[0].components]:
				glyphs.append(g)
		return glyphs

	def ChangeMetricsbyPercentageMain(self, sender):
		thisLayer = None
		try:
			Font = Glyphs.font
			if Font is None:
				self.setStatus("⚠️ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			selectedLayers = Font.selectedLayers

			# update settings to the latest user input:
			self.SavePreferences()

			changeLSB = self.w.LSB.get()
			changeRSB = self.w.RSB.get()
			change = (100.0 + self.prefFloat("changeValue")) / 100.0

			if sender == self.w.revertButton:
				if change == 0:
					self.setStatus("⚠️ Cannot revert a change of −100%.")
					Message(title="Cannot Revert", message="A change of −100% sets the sidebearings to zero and cannot be reverted.", OKButton=None)
					return
				change = 1.0 / change

			self.setStatus(f"🛠️ Processing {len(selectedLayers)} layers…")
			changedCount = 0
			for thisLayer in selectedLayers:
				self.setStatus(f"🔠 {thisLayer.parent.name}")

				layer_id = thisLayer.layerId
				if len(thisLayer.paths) > 0 or len(thisLayer.components) > 0:
					changedCount += 1
					if changeLSB:

						LSB_change = (thisLayer.LSB * change) - thisLayer.LSB

						thisLayer.LSB *= change

						# counteract movement in glyphs that reference this glyph as a component:
						for g in self.findGlyphsThatReferenceGlyphAsComponent(thisLayer.parent):
							referencingLayer = g.layers[layer_id]
							if referencingLayer is None:
								continue  # e.g. a special layer that only exists in the selected glyph
							for c in referencingLayer.components:
								if c.componentName == thisLayer.parent.name:

									# if component is rotated or mirrored, we need to reverse the LSB change
									if c.transform[0] < 0 or c.transform[3] < 0:
										c.position = (c.position[0] + LSB_change, c.position[1])

									# otherwise, we can just offset the LSB change directly
									else:
										c.position = (c.position[0] - LSB_change, c.position[1])


					if changeRSB:
						thisLayer.RSB *= change

			if changedCount:
				self.setStatus(f"✅ Changed {changedCount} layers.")
			else:
				self.setStatus("⚠️ No selected layers with outlines or components.")
			# self.w.close()
		except Exception as e:
			lastName = thisLayer.parent.name if thisLayer is not None else "start"
			self.setStatus(f"❌ Error at {lastName}. Details in Macro Window.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Change Metrics by Percentage Error: %s" % e)


ChangeMetricsbyPercentage()
