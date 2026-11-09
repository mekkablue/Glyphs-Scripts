# MenuTitle: Offset Pixel Rows
__doc__ = """
Offsets each row of pixels by a percentage. Rhythm of 2 = every other line offset by half of a pixel’s width; rhythm of 3 = every second line by a third, every third line by two thirds; and so on. Useful for offsetting hexagon-shaped pixels, etc.
"""

import objc
import vanilla
from mekkablue import mekkaObject, UpdateButton, match, reportFontName
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


class OffsetPixelRows(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"allMasters": True,
		"allGlyphs": False,
		"pixelWidth": 100,
		"pixelName": "*pix*",
		"rhythm": 2,
		"shouldResetGrid": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 290
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Offset Pixel Rows",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		tooltipText = "Will increasingly offset every n lines, first line not at all, each following line by 1/n pixel more. Use negative number for moving to the left."
		self.w.rhythmText = vanilla.TextBox("auto", "Line rhythm", sizeStyle="small", selectable=True)
		rhythmFormatter = NSNumberFormatter.alloc().init()
		rhythmFormatter.setAllowsFloats_(False)  # negative values move to the left
		self.w.rhythm = SteppingEditText("auto", "2", callback=self.SavePreferences, sizeStyle="small", formatter=rhythmFormatter)
		self.w.rhythmText.setToolTip(tooltipText)
		self.w.rhythm.setToolTip(tooltipText)

		tooltipText = "Only components matching this name will be moved. You can use ? and * as wildcards. Leave empty for all components."
		self.w.pixelNameText = vanilla.TextBox("auto", "Pixel name", sizeStyle="small", selectable=True)
		self.w.pixelName = vanilla.EditText("auto", "*pix*", callback=self.SavePreferences, sizeStyle="small")
		self.w.pixelNameText.setToolTip(tooltipText)
		self.w.pixelName.setToolTip(tooltipText)

		tooltipText = "Pixel size. All offsets are calculated based on this"
		self.w.pixelWidthText = vanilla.TextBox("auto", "Pixel width", sizeStyle="small", selectable=True)
		pixelWidthFormatter = NSNumberFormatter.alloc().init()
		pixelWidthFormatter.setAllowsFloats_(False)
		pixelWidthFormatter.setMinimum_(1)
		self.w.pixelWidth = SteppingEditText("auto", "100", callback=self.SavePreferences, sizeStyle="small", formatter=pixelWidthFormatter)
		self.w.pixelWidthText.setToolTip(tooltipText)
		self.w.pixelWidth.setToolTip(tooltipText)
		self.w.pixelWidthUpdate = UpdateButton("auto", callback=self.updateUI)
		self.w.pixelWidthUpdate.setToolTip("Take the pixel width from the grid of the frontmost font.")

		self.w.allGlyphs = vanilla.CheckBox("auto", "All glyphs (ignore selection)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters = vanilla.CheckBox("auto", "Include all masters", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.shouldResetGrid = vanilla.CheckBox("auto", "Reset grid to pixel width ÷ rhythm", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Offset", callback=self.OffsetPixelRowsMain)
		self.w.setDefaultButton(self.w.runButton)

		# labels in front of fields: right-aligned, one shared width
		labelNames = ("rhythmText", "pixelNameText", "pixelWidthText")
		widestLabel = "pixelNameText"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[rhythmText]-gap-[rhythm(60)]-(>=inset)-|",
				"H:|-inset-[pixelNameText]-gap-[pixelName]-inset-|",
				"H:|-inset-[pixelWidthText]-gap-[pixelWidth(60)]-gap-[pixelWidthUpdate(20)]-(>=inset)-|",
				"H:|-inset-[allGlyphs]-(>=inset)-|",
				"H:|-inset-[allMasters]-(>=inset)-|",
				"H:|-inset-[shouldResetGrid]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[rhythm]-row-[pixelName]-row-[pixelWidth]-inset-[allGlyphs]-checkRow-[allMasters]-checkRow-[shouldResetGrid]-inset-[runButton]-inset-|",
				{"view1": self.w.rhythmText, "attribute1": "centerY", "view2": self.w.rhythm, "attribute2": "centerY"},
				{"view1": self.w.pixelNameText, "attribute1": "centerY", "view2": self.w.pixelName, "attribute2": "centerY"},
				{"view1": self.w.pixelWidthText, "attribute1": "centerY", "view2": self.w.pixelWidth, "attribute2": "centerY"},
				{"view1": self.w.pixelWidthUpdate, "attribute1": "centerY", "view2": self.w.pixelWidth, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Offset Pixel Rows’ could not load preferences. Will resort to defaults.")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		font = Glyphs.font
		if not font:
			return

		if sender is self.w.pixelWidthUpdate:
			self.setPref("pixelWidth", int(font.gridLength))
			self.LoadPreferences()

	def OffsetPixelRowsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Offset Pixel Rows’ could not write preferences.")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				reportName = reportFontName(thisFont)
				print(f"Offset Pixel Rows Report for {reportName}")
				print()

				allMasters = self.pref("allMasters")
				allGlyphs = self.pref("allGlyphs")
				pixelWidth = self.prefInt("pixelWidth")
				pixelName = self.pref("pixelName")
				rhythm = self.prefInt("rhythm")
				shouldResetGrid = self.pref("shouldResetGrid")
				currentMasterID = thisFont.selectedFontMaster.id

				if shouldResetGrid:
					thisFont.grid = abs(int(pixelWidth))
					thisFont.gridSubDivisions = abs(int(rhythm))

				if allGlyphs:
					glyphs = thisFont.glyphs
				else:
					glyphs = [l.parent for l in thisFont.selectedLayers]

				for glyph in glyphs:
					print(f"🔤 {glyph.name}")
					for layer in glyph.layers:
						if not layer.components:
							continue

						if not layer.isMasterLayer or layer.isSpecialLayer:
							continue

						if not (allMasters or layer.associatedMasterId == currentMasterID):
							continue

						for component in layer.components:
							if pixelName and not match(pixelName, component.componentName):
								continue

							verticalPosition = component.y
							offsetFactor = int(verticalPosition / pixelWidth) % rhythm
							if offsetFactor:
								component.x += (rhythm / abs(rhythm)) * offsetFactor * pixelWidth / rhythm

				if thisFont.currentTab:
					thisFont.currentTab.redraw()
					thisFont.currentTab.reflow()
				else:
					thisFont.fontView.redraw()

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Offset Pixel Rows Error: {e}")
			import traceback
			print(traceback.format_exc())


OffsetPixelRows()
