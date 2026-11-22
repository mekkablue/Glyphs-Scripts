# MenuTitle: Change Metrics by Percentage
__doc__ = """
Changes the sidebearings of the glyphs in the chosen scope by a percentage value. Layers with auto-aligned components are always skipped, and optionally the glyphs that consist only of components.
"""

import vanilla
from mekkablue import mekkaObject, SteppingEditText, decimalFormatter, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)

scopeOptions = (
	"selected glyphs",
	"all masters of selected glyphs",
	"⚠️ complete current master",
	"⚠️ complete font",
	"⚠️ all open fonts",
)


class ChangeMetricsbyPercentage(mekkaObject):
	prefDict = {
		"LSB": True,
		"RSB": True,
		"changeValue": 10,
		"scope": 0,
		"onlyPathBased": False,
	}

	def __init__(self):
		windowWidth = 420
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Change Metrics by Percentage",
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		inset = 15
		formatter = decimalFormatter(fractionDigits=2)
		self.w.text_1 = vanilla.TextBox("auto", "Increase")
		self.w.LSB = vanilla.CheckBox("auto", "LSB", value=True, callback=self.SavePreferences)
		self.w.LSB.setToolTip("If enabled, changes the left sidebearings.")
		self.w.RSB = vanilla.CheckBox("auto", "RSB by", value=True, callback=self.SavePreferences)
		self.w.RSB.setToolTip("If enabled, changes the right sidebearings.")
		self.w.changeValue = SteppingEditText("auto", "10", callback=self.SavePreferences, formatter=formatter)
		self.w.changeValue.setToolTip("Percentage by which the sidebearings are changed. Negative values decrease them.")
		self.w.text_3 = vanilla.TextBox("auto", "%")

		self.w.scopeLabel = vanilla.TextBox("auto", "Change in:")
		self.w.scope = vanilla.PopUpButton("auto", scopeOptions, callback=self.SavePreferences)
		scopeTooltip = (
			"Determines which glyphs and layers are affected:\n"
			"• Selected glyphs – current master layer of each selected glyph.\n"
			"• All masters of selected glyphs – all layers of each selected glyph.\n"
			"• ⚠️ Complete current master – all glyphs in the font, current master only.\n"
			"• ⚠️ Complete font – all glyphs in the font, all masters.\n"
			"• ⚠️ All open fonts – all glyphs in every open font, all masters."
		)
		self.w.scopeLabel.setToolTip(scopeTooltip)
		self.w.scope.setToolTip(scopeTooltip)

		self.w.onlyPathBased = vanilla.CheckBox("auto", "Only change path-based glyphs", value=False, callback=self.SavePreferences)
		self.w.onlyPathBased.setToolTip("Skips glyphs without paths of their own, i.e., glyphs that consist only of components. Layers with auto-aligned components are always skipped.")

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.revertButton = vanilla.Button("auto", "Reverse", callback=self.ChangeMetricsbyPercentageMain)
		self.w.revertButton.setToolTip("Reverses a previous change by the same percentage, i.e., divides the sidebearings by the factor.")
		self.w.runButton = vanilla.Button("auto", "Change", callback=self.ChangeMetricsbyPercentageMain)
		self.w.runButton.setToolTip("Changes the sidebearings by the percentage.")
		self.w.setDefaultButton(self.w.runButton)

		# the status line takes the leftover width, the buttons stay as wide as their titles need:
		nsStatus = self.w.status.getNSTextField()
		nsStatus.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		nsStatus.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		for button in (self.w.revertButton, self.w.runButton):
			nsButton = button.getNSButton()
			nsButton.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsButton.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# the labels are right-aligned and hug their text:
		for label in (self.w.text_1, self.w.scopeLabel):
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		rowViews = (self.w.text_1, self.w.LSB, self.w.RSB, self.w.text_3)
		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-gap-[LSB]-gap-[RSB]-gap-[changeValue(55)]-3-[text_3]-(>=inset)-|",
				"H:|-inset-[scopeLabel]-gap-[scope]-inset-|",
				"H:[onlyPathBased]-(>=inset)-|",
				"H:|-inset-[status]-gap-[revertButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[changeValue]-row-[scope]-checkRow-[onlyPathBased]-inset-[runButton]-inset-|",
				{"view1": self.w.scopeLabel, "attribute1": "width", "view2": self.w.text_1, "attribute2": "width"},
				{"view1": self.w.scopeLabel, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				{"view1": self.w.onlyPathBased, "attribute1": "left", "view2": self.w.LSB, "attribute2": "left"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.revertButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			] + [
				{"view1": view, "attribute1": "centerY", "view2": self.w.changeValue, "attribute2": "centerY"}
				for view in rowViews
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "checkRow": 5},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()

	def scopeFonts(self):
		"""The fonts the scope applies to."""
		if self.prefInt("scope") == 4:
			return list(Glyphs.fonts)
		return [Glyphs.font] if Glyphs.font else []

	def glyphsAndLayerScope(self, font):
		"""Returns (glyphs, layerScope) for a font, where layerScope is a master ID or 'all'."""
		scope = self.prefInt("scope")
		masterId = font.selectedFontMaster.id
		if scope in (0, 1):
			glyphs = list(dict.fromkeys(layer.parent for layer in font.selectedLayers if layer.parent))
			return glyphs, (masterId if scope == 0 else "all")
		elif scope == 2:
			return list(font.glyphs), masterId
		return list(font.glyphs), "all"  # complete font and all open fonts

	def layersForGlyph(self, glyph, layerScope):
		"""Returns the master and special layers of a glyph that are in the layer scope (no backup layers)."""
		layers = [layer for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]
		if layerScope == "all":
			return layers
		return [layer for layer in layers if layer.associatedMasterId == layerScope]

	def findGlyphsThatReferenceGlyphAsComponent(self, font, glyph):
		glyphs = []
		for g in font.glyphs:
			if g != glyph and glyph.name in [c.componentName for c in g.layers[0].components]:
				glyphs.append(g)
		return glyphs

	def ChangeMetricsbyPercentageMain(self, sender):
		thisGlyph = None
		try:
			fonts = self.scopeFonts()  # frontmost font, or all open fonts
			if not fonts:
				self.setStatus("⚠️ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			# update settings to the latest user input:
			self.SavePreferences()

			changeLSB = self.w.LSB.get()
			changeRSB = self.w.RSB.get()
			onlyPathBased = self.prefBool("onlyPathBased")
			change = (100.0 + self.prefFloat("changeValue")) / 100.0

			if sender == self.w.revertButton:
				if change == 0:
					self.setStatus("⚠️ Cannot reverse a change of −100%.")
					Message(title="Cannot Reverse", message="A change of −100% sets the sidebearings to zero and cannot be reversed.", OKButton=None)
					return
				change = 1.0 / change

			self.setStatus("🛠️ Processing…")
			changedCount = 0
			alignedCount = 0
			for font in fonts:
				glyphs, layerScope = self.glyphsAndLayerScope(font)
				for thisGlyph in glyphs:
					self.setStatus(f"🔠 {thisGlyph.name}")
					for thisLayer in self.layersForGlyph(thisGlyph, layerScope):
						if thisLayer.isAligned:
							# auto-aligned glyphs get their metrics from their components, never change them
							alignedCount += 1
							continue
						if onlyPathBased:
							if len(thisLayer.paths) == 0:
								continue
						elif len(thisLayer.paths) == 0 and len(thisLayer.components) == 0:
							continue

						changedCount += 1
						layer_id = thisLayer.layerId
						if changeLSB:

							LSB_change = (thisLayer.LSB * change) - thisLayer.LSB

							thisLayer.LSB *= change

							# counteract movement in glyphs that reference this glyph as a component:
							for g in self.findGlyphsThatReferenceGlyphAsComponent(font, thisLayer.parent):
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

			alignedText = f" Skipped {alignedCount} auto-aligned." if alignedCount else ""
			if changedCount:
				self.setStatus(f"✅ Changed {changedCount} layer{'' if changedCount == 1 else 's'}.{alignedText}")
			else:
				self.setStatus(f"⚠️ No layers to change.{alignedText}")
		except Exception as e:
			lastName = thisGlyph.name if thisGlyph is not None else "start"
			self.setStatus(f"❌ Error at {lastName}. Details in Macro Window.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Change Metrics by Percentage Error: %s" % e)


ChangeMetricsbyPercentage()
