# MenuTitle: Set Transform Origin
__doc__ = """
Sets origin point for Rotate tool.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSPoint, NSClassFromString
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, SteppingEditText, decimalFormatter


class SetTransformOriginWindow(mekkaObject):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 360
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set Transform Origin",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		formatter = decimalFormatter(fractionDigits=3)

		self.w.text_1 = vanilla.TextBox("auto", "Origin")
		self.w.originX = SteppingEditText("auto", "0.0", formatter=formatter)
		self.w.originX.setToolTip("x coordinate of the transform origin.")
		self.w.originY = SteppingEditText("auto", "0.0", formatter=formatter)
		self.w.originY.setToolTip("y coordinate of the transform origin.")

		# Run Button:
		self.w.resetButton = vanilla.Button("auto", "Get", callback=self.GetTransformOrigin)
		self.w.resetButton.setToolTip("Reads the current origin of the Rotate tool into the fields.")
		self.w.runButton = vanilla.Button("auto", "Set", callback=self.SetTransformOriginMain)
		self.w.runButton.setToolTip("Sets the origin of the Rotate tool to the coordinates in the fields.")

		self.w.setDefaultButton(self.w.runButton)

		# with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the fields take the leftover width:
		self.w.text_1.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-gap-[originX(>=60)]-gap-[originY(==originX)]-gap-[resetButton(>=60)]-gap-[runButton(>=60)]-inset-|",
				"V:|-inset-[originX]-inset-|",
				{"view1": self.w.text_1, "attribute1": "centerY", "view2": self.w.originX, "attribute2": "centerY"},
				{"view1": self.w.originY, "attribute1": "centerY", "view2": self.w.originX, "attribute2": "centerY"},
				{"view1": self.w.resetButton, "attribute1": "centerY", "view2": self.w.originX, "attribute2": "centerY"},
				{"view1": self.w.runButton, "attribute1": "centerY", "view2": self.w.originX, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8},
		)

		# Load Settings:
		if not self.GetTransformOrigin(None):
			print("Note: 'Set Transform Origin' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def GetTransformOrigin(self, sender):
		try:
			myController = Glyphs.currentDocument.windowController()
			rotateToolClass = NSClassFromString("GlyphsToolRotate")
			myRotateTool = myController.toolForClass_(rotateToolClass)
			currentOrigin = myRotateTool.transformOrigin()

			self.w.originX.set(currentOrigin.x)
			self.w.originY.set(currentOrigin.y)
		except:
			return False

		return True

	def SetTransformOriginMain(self, sender):
		try:
			# the fields have a number formatter: get() returns a number, or None for an empty field
			newOriginX = float(self.w.originX.get() or 0)
			newOriginY = float(self.w.originY.get() or 0)
			newOriginPoint = NSPoint(newOriginX, newOriginY)

			myController = Glyphs.currentDocument.windowController()
			myController.graphicView().setNeedsDisplay_(False)

			rotateToolClass = NSClassFromString("GlyphsToolRotate")
			myRotateTool = myController.toolForClass_(rotateToolClass)
			myRotateTool.setTransformOrigin_(newOriginPoint)

			myController.graphicView().setNeedsDisplay_(True)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set Transform Origin Error: %s" % e)


SetTransformOriginWindow()
