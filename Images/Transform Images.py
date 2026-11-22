# MenuTitle: Transform Images
__doc__ = """
Batch scale and move images in selected layers.
"""

import vanilla
from AppKit import NSAffineTransform, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight
from Foundation import NSNumberFormatter, NSNumberFormatterDecimalStyle
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, SteppingEditText


def getScale(scaleString, factor):
	if factor == 1:
		return (100.0 + float(scaleString)) / 100.0
	else:
		return 100.0 / (100.0 + float(scaleString))


class TransformImages(mekkaObject):
	prefDict = {
		"scaleX": 100,
		"scaleY": 100,
		"moveX": 0,
		"moveY": 0,
	}

	def __init__(self):
		windowWidth = 270
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Transform Images",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		inset = 15

		# decimals allowed; scaling by -100% or less would make the image vanish, and divides by zero when undoing
		scaleFormatter = NSNumberFormatter.alloc().init()
		scaleFormatter.setNumberStyle_(NSNumberFormatterDecimalStyle)
		scaleFormatter.setUsesGroupingSeparator_(False)
		scaleFormatter.setMaximumFractionDigits_(3)
		scaleFormatter.setMinimum_(-99.9)
		moveFormatter = NSNumberFormatter.alloc().init()
		moveFormatter.setNumberStyle_(NSNumberFormatterDecimalStyle)
		moveFormatter.setUsesGroupingSeparator_(False)
		moveFormatter.setMaximumFractionDigits_(3)

		scaleTooltip = "Relative change of the image size in percent, horizontal and vertical. Positive values enlarge, negative values shrink."
		self.w.scale_text1 = vanilla.TextBox("auto", "Scale x/y:", sizeStyle='small')
		self.w.scaleX = SteppingEditText("auto", "+10.5", callback=self.SavePreferences, sizeStyle='small', formatter=scaleFormatter)
		self.w.scaleX.setToolTip(scaleTooltip)
		self.w.scaleY = SteppingEditText("auto", "-11.0", callback=self.SavePreferences, sizeStyle='small', formatter=scaleFormatter)
		self.w.scaleY.setToolTip(scaleTooltip)
		self.w.scale_text2 = vanilla.TextBox("auto", "%", sizeStyle='small')
		self.w.scale_text1.setToolTip(scaleTooltip)
		self.w.scale_text2.setToolTip(scaleTooltip)

		moveTooltip = "Distance in units to shift the image, horizontal and vertical."
		self.w.move_text1 = vanilla.TextBox("auto", "Move x/y:", sizeStyle='small')
		self.w.moveX = SteppingEditText("auto", "10", callback=self.SavePreferences, sizeStyle='small', formatter=moveFormatter)
		self.w.moveX.setToolTip(moveTooltip)
		self.w.moveY = SteppingEditText("auto", "10", callback=self.SavePreferences, sizeStyle='small', formatter=moveFormatter)
		self.w.moveY.setToolTip(moveTooltip)
		self.w.move_text2 = vanilla.TextBox("auto", "units", sizeStyle='small')
		self.w.move_text1.setToolTip(moveTooltip)
		self.w.move_text2.setToolTip(moveTooltip)

		self.w.backButton = vanilla.Button("auto", "Back", callback=self.TransformImagesMain)
		self.w.backButton.setToolTip("Reverses the scaling and moving, i.e. undoes a previous Go with the same values.")
		self.w.runButton = vanilla.Button("auto", "Go", callback=self.TransformImagesMain)
		self.w.runButton.setToolTip("Scales and moves the images in the selected layers by the given values.")
		self.w.setDefaultButton(self.w.runButton)

		# every control hugs vertically, so the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels: right-aligned, one shared width
		labelNames = ("scale_text1", "move_text1")
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[scale_text1]-gap-[scaleX(55)]-gap-[scaleY(55)]-gap-[scale_text2]-(>=inset)-|",
				"H:|-inset-[move_text1]-gap-[moveX(55)]-gap-[moveY(55)]-gap-[move_text2]-(>=inset)-|",
				"H:|-(>=inset)-[backButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[scaleX]-row-[moveX]-inset-[runButton]-inset-|",
				"V:[backButton]-inset-|",
				{"view1": self.w.scale_text1, "attribute1": "centerY", "view2": self.w.scaleX, "attribute2": "centerY"},
				{"view1": self.w.scaleY, "attribute1": "centerY", "view2": self.w.scaleX, "attribute2": "centerY"},
				{"view1": self.w.scale_text2, "attribute1": "centerY", "view2": self.w.scaleX, "attribute2": "centerY"},
				{"view1": self.w.move_text1, "attribute1": "centerY", "view2": self.w.moveX, "attribute2": "centerY"},
				{"view1": self.w.moveY, "attribute1": "centerY", "view2": self.w.moveX, "attribute2": "centerY"},
				{"view1": self.w.move_text2, "attribute1": "centerY", "view2": self.w.moveX, "attribute2": "centerY"},
				{"view1": self.w.move_text1, "attribute1": "width", "view2": self.w.scale_text1, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()

	def TransformImagesMain(self, sender):
		try:
			Font = Glyphs.font
			if not Font:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			self.SavePreferences()
			selectedLayers = Font.selectedLayers
			if sender == self.w.backButton:
				factor = -1.0
			else:
				factor = 1.0

			# an empty field is stored as nothing, and counts as 0:
			moveX, moveY = self.prefFloat("moveX") * factor, self.prefFloat("moveY") * factor
			scaleX, scaleY = getScale(self.prefFloat("scaleX"), factor), getScale(self.prefFloat("scaleY"), factor)

			for thisLayer in selectedLayers:
				thisImage = thisLayer.backgroundImage
				if thisImage:
					ScaleAndMoveTransform = NSAffineTransform.transform()
					ScaleAndMoveTransform.setTransformStruct_(thisImage.transformStruct())
					ScaleAndMoveTransform.scaleXBy_yBy_(scaleX, scaleY)
					ScaleAndMoveTransform.translateXBy_yBy_(moveX, moveY)
					thisImage.setTransformStruct_(ScaleAndMoveTransform.transformStruct())
			if Font.currentTab:
				Font.currentTab.redraw()

		except Exception as e:
			raise e


TransformImages()
