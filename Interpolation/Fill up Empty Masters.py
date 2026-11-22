# MenuTitle: Fill Up Empty Masters
__doc__ = """
Looks for empty master layers and adds shapes of a preferred master.
"""

import vanilla
from copy import copy as copy
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message, CORNER, SEGMENT, CAP
from mekkablue import mekkaObject, UpdateButton, reportFontName, makeWindowResizable


labelColors = (
	"🔴 Red",
	"🟠 Orange",
	"🟤 Brown",
	"🟡 Yellow",
	"💚 Light Green",
	"🟢 Dark Green",
	"🩵 Cyan",
	"🔵 Blue",
	"🟣 Purple",
	"🩷 Pink",
	"🩶 Light Gray",
	"🌑 Dark Gray",
)


class FillUpEmptyMasters(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"masterChoice": 0,
		"firstOneWithShapes": 1,
		"addMissingAnchors": 1,
		"copySidebearings": 0,
		"markWithColor": 0,
		"layerColor": 0,
		"overwriteExisting": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Fill Up Empty Masters",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 16

		self.w.descriptionText = vanilla.TextBox("auto", "Populate empty layers of selected glyphs:", sizeStyle="small", selectable=True)

		self.w.masterChoiceText = vanilla.TextBox("auto", "Use shapes from", sizeStyle="small", selectable=True)
		self.w.masterChoice = vanilla.PopUpButton("auto", (), sizeStyle="small", callback=self.SavePreferences)
		self.w.masterChoiceUpdate = UpdateButton("auto", callback=self.masterChoiceUpdateAction)

		self.w.firstOneWithShapes = vanilla.CheckBox("auto", "If empty, use first master with shapes", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.addMissingAnchors = vanilla.CheckBox("auto", "Add missing default anchors", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.copySidebearings = vanilla.CheckBox("auto", "Also copy sidebearings", value=False, callback=self.SavePreferences, sizeStyle="small")

		self.w.markWithColor = vanilla.CheckBox("auto", "Color-mark filled-up layers", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.layerColor = vanilla.PopUpButton("auto", labelColors, sizeStyle="small", callback=self.SavePreferences)

		self.w.overwriteExisting = vanilla.CheckBox("auto", "Overwrite Existing Outlines❗️", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Status:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Fill Up", callback=self.FillUpEmptyMastersMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the popup takes the leftover width:
		nsLabel = self.w.masterChoiceText.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# the checkbox hugs its text, the color popup behind it stretches:
		self.w.markWithColor.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.layerColor.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# the status text gives way to the button:
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[masterChoiceText]-gap-[masterChoice]-gap-[masterChoiceUpdate]-inset-|",
				"H:|-inset-[firstOneWithShapes]-(>=inset)-|",
				"H:|-inset-[addMissingAnchors]-(>=inset)-|",
				"H:|-inset-[copySidebearings]-(>=inset)-|",
				"H:|-inset-[markWithColor]-gap-[layerColor]-inset-|",
				"H:|-inset-[overwriteExisting]-(>=inset)-|",
				"H:|-inset-[status]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[masterChoice]-row-[firstOneWithShapes]-stackRow-[addMissingAnchors]-stackRow-[copySidebearings]-stackRow-[markWithColor]-stackRow-[overwriteExisting]-inset-[runButton]-inset-|",
				# one baseline per row:
				{"view1": self.w.masterChoiceText, "attribute1": "centerY", "view2": self.w.masterChoice, "attribute2": "centerY"},
				{"view1": self.w.masterChoiceUpdate, "attribute1": "centerY", "view2": self.w.masterChoice, "attribute2": "centerY"},
				{"view1": self.w.layerColor, "attribute1": "centerY", "view2": self.w.markWithColor, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "stackRow": 8, "headlineGap": 10},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def masterChoiceUpdateAction(self, sender):
		self.updateUI()

	def updateUI(self, sender=None):
		self.w.layerColor.enable(self.pref("markWithColor"))
		if Glyphs.font:
			masterNames = [m.name for m in Glyphs.font.masters]
			self.w.masterChoice.setItems(masterNames)
			if len(masterNames) < self.w.masterChoice.get() + 1:
				self.w.masterChoice.set(len(masterNames) - 1)
			else:
				self.w.masterChoice.set(self.pref("masterChoice"))
			self.w.runButton.enable(1)
		else:
			self.w.masterChoice.setItems([])
			self.w.runButton.enable(0)

	def FillUpEmptyMastersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				reportName = reportFontName(thisFont)
				print(f"Fill Up Empty Masters Report for {reportName}")
				print()
				sourceMaster = thisFont.masters[self.pref("masterChoice")]
				sourceID = sourceMaster.id
				selectedGlyphs = set([layer.parent for layer in thisFont.selectedLayers])
				layerCount = 0
				for thisGlyph in selectedGlyphs:
					self.w.status.set(f"🔠 {thisGlyph.name}")
					sourceLayer = thisGlyph.layers[sourceID]
					if not sourceLayer.shapes and self.pref("firstOneWithShapes"):
						sourceLayer = None
						for master in thisFont.masters:
							if thisGlyph.layers[master.id].shapes:
								sourceLayer = thisGlyph.layers[master.id]
								print(f"🔤 Filling up {thisGlyph.name} from layer {master.name}")
								break

					if not sourceLayer:
						print(f"⚠️ No shapes for filling up in: {thisGlyph.name}")
						self.w.status.set(f"⚠️ No shapes: {thisGlyph.name}")
						continue

					for targetLayer in thisGlyph.layers:
						if (targetLayer.isMasterLayer or targetLayer.isSpecialLayer) and targetLayer != sourceLayer and (not targetLayer.shapes or self.pref("overwriteExisting")):
							targetLayer.clear()
							layerCount += 1
							for sourceShape in sourceLayer.shapes:
								targetLayer.shapes.append(copy(sourceShape))
							for sourceAnchor in sourceLayer.anchors:
								targetLayer.anchors.append(copy(sourceAnchor))
							for sourceHint in sourceLayer.hints:
								if sourceHint.type in (CORNER, SEGMENT, CAP):
									targetLayer.hints.append(sourceHint.copy())

							if self.pref("copySidebearings"):
								targetLayer.LSB = sourceLayer.LSB
								targetLayer.RSB = sourceLayer.RSB

							if self.pref("addMissingAnchors"):
								targetLayer.addMissingAnchors()

							if self.pref("markWithColor"):
								targetLayer.color = self.pref("layerColor")

			finalMessage = f"✅ Done. Filled up {layerCount} layer{'' if layerCount == 1 else 's'} in {len(selectedGlyphs)} glyph{'' if len(selectedGlyphs) == 1 else 's'}."
			print(f"\n{finalMessage}")
			self.w.status.set(finalMessage)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Fill Up Empty Masters Error: {e}")
			import traceback
			print(traceback.format_exc())


FillUpEmptyMasters()
