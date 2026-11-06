# MenuTitle: Batch Insert Anchor
__doc__ = """
Insert an anchor in all selected glyphs, on all layers, and pick the approximate spot.
"""

import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
	NSWindowStyleMaskResizable,
)
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSAnchor
from mekkablue import mekkaObject

xPositions = ("Center of width", "LSB", "RSB", "Bbox left edge", "Bbox horizontal center", "Bbox right edge")
yPositions = ("Baseline", "x-height", "Smallcap height", "Cap height", "Ascender", "Shoulder height", "Descender", "Bbox top", "Bbox center", "Bbox bottom")


baseNames = ("top", "bottom", "topright", "center", "topleft", "ogonek")
anchorNames = baseNames + tuple(f"_{name}" for name in baseNames) + ("exit", "entry", "#exit", "#entry")


class BatchInsertAnchor(mekkaObject):
	prefDict = {
		"anchorName": "top",
		"xPos": 0,
		"yPos": 0,
		"replaceExisting": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 240
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Batch Insert Anchor",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "In selected glyphs, insert this anchor on all layers", sizeStyle="small", selectable=True)

		self.w.anchorNameText = vanilla.TextBox("auto", "Anchor name", sizeStyle="small", selectable=True)
		self.w.anchorName = vanilla.ComboBox("auto", anchorNames, completes=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.anchorName.getNSComboBox().setNumberOfVisibleItems_(len(anchorNames))
		tooltipText = "Name of the anchor that will be inserted."
		self.w.anchorNameText.setToolTip(tooltipText)
		self.w.anchorName.setToolTip(tooltipText)

		self.w.xPosText = vanilla.TextBox("auto", "H position", sizeStyle="small", selectable=True)
		self.w.xPos = vanilla.PopUpButton("auto", xPositions, sizeStyle="small", callback=self.SavePreferences)
		tooltipText = "The x coordinate of the anchor."
		self.w.xPosText.setToolTip(tooltipText)
		self.w.xPos.setToolTip(tooltipText)

		self.w.yPosText = vanilla.TextBox("auto", "V position", sizeStyle="small", selectable=True)
		self.w.yPos = vanilla.PopUpButton("auto", yPositions, sizeStyle="small", callback=self.SavePreferences)
		tooltipText = "The y coordinate of the anchor."
		self.w.yPosText.setToolTip(tooltipText)
		self.w.yPos.setToolTip(tooltipText)

		self.w.replaceExisting = vanilla.CheckBox("auto", "Also replace existing anchors", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.replaceExisting.setToolTip(
			"If enabled, will delete anchors that have the same name of the one you are adding, before it is added again at the specified spot. If disabled, the script will skip layers that already have an anchor of the same name."
		)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Insert", callback=self.BatchInsertAnchorMain)
		self.w.setDefaultButton(self.w.runButton)

		# labels: right-aligned, same width, hugging their text
		labelNames = ("anchorNameText", "xPosText", "yPosText")
		widestLabel = "anchorNameText"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]
		widthRules.append({"view1": self.w.yPos, "attribute1": "width", "view2": self.w.xPos, "attribute2": "width"})
		centerRules = [
			{"view1": self.w.anchorNameText, "attribute1": "centerY", "view2": self.w.anchorName, "attribute2": "centerY"},
			{"view1": self.w.xPosText, "attribute1": "centerY", "view2": self.w.xPos, "attribute2": "centerY"},
			{"view1": self.w.yPosText, "attribute1": "centerY", "view2": self.w.yPos, "attribute2": "centerY"},
		]
		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[anchorNameText]-gap-[anchorName]-inset-|",
				"H:|-inset-[xPosText]-gap-[xPos]-inset-|",
				"H:|-inset-[yPosText]-gap-[yPos]-inset-|",
				"H:|-inset-[replaceExisting]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[anchorName]-row-[xPos]-row-[yPos]-row-[replaceExisting]-inset-[runButton]-inset-|",
			] + widthRules + centerRules,
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# resizable horizontally only: content height stays fixed
		nsWindow = self.w.getNSWindow()
		contentHeight = nsWindow.contentRectForFrameRect_(nsWindow.frame()).size.height
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.setContentMinSize_((windowWidth, contentHeight))
		nsWindow.setContentMaxSize_((10000, contentHeight))

	def BatchInsertAnchorMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			print("Batch Insert Anchor Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()

			anchorName = self.pref("anchorName")
			xPos = self.pref("xPos")
			yPos = self.pref("yPos")
			replaceExisting = self.pref("replaceExisting")

			selectedLayers = thisFont.selectedLayers
			selectedGlyphNames = list(set([layer.parent.name for layer in selectedLayers if layer.parent]))

			print("Inserting anchor '%s' at %s and %s in %i glyphs...\n" % (
				anchorName,
				xPositions[xPos],
				yPositions[yPos],
				len(selectedGlyphNames),
			))

			for glyphName in selectedGlyphNames:
				print("🔠 %s" % glyphName)
				glyph = thisFont.glyphs[glyphName]
				if not glyph:
					print("⛔️ Error: could not find glyph %s. Skipping.\n" % glyphName)
				else:
					for thisLayer in glyph.layers:
						if replaceExisting or not thisLayer.anchors[anchorName]:
							if xPos == 0:
								x = thisLayer.width // 2
							elif xPos == 1:  # "LSB"
								x = 0.0
							elif xPos == 2:  # "RSB"
								x = thisLayer.width
							elif xPos == 3:  # "Bbox Left Edge"
								x = thisLayer.bounds.origin.x
							elif xPos == 4:  # "Bbox Horizontal Center"
								x = thisLayer.bounds.origin.x + thisLayer.bounds.size.width // 2
							elif xPos == 5:  # "Bbox Right Edge"
								x = thisLayer.bounds.origin.x + thisLayer.bounds.size.width

							if yPos == 0:  # "Baseline"
								y = 0.0
							if yPos == 1:  # "x-height"
								y = thisLayer.master.xHeight
							if yPos == 2:  # "Smallcap height"
								y = thisLayer.master.customParameters["smallCapHeight"]
								if not y:  # Fallback if not set:
									y = thisLayer.master.xHeight
							if yPos == 3:  # "Cap height"
								y = thisLayer.master.capHeight
							if yPos == 4:  # "Ascender"
								y = thisLayer.master.ascender
							if yPos == 5:  # "Shoulder height"
								y = thisLayer.master.customParameters["shoulderHeight"]
								if not y:  # Fallback if not set:
									y = thisLayer.master.capHeight
							if yPos == 6:  # "Descender"
								y = thisLayer.master.descender
							if yPos == 7:  # "Bbox Top"
								y = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
							if yPos == 8:  # "Bbox Center"
								y = thisLayer.bounds.origin.y + thisLayer.bounds.size.height // 2
							if yPos == 9:  # "Bbox Bottom"
								y = thisLayer.bounds.origin.y

							anchor = GSAnchor()
							anchor.name = anchorName
							anchor.position = NSPoint(x, y)
							thisLayer.anchors.append(anchor)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Batch Insert Anchor Error: {e}")
			import traceback
			print(traceback.format_exc())


BatchInsertAnchor()
