# MenuTitle: Grid Switcher
__doc__ = """
Toggles grid between two gridstep values.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, SteppingEditText, integerFormatter, makeWindowResizable


class Gridswitch(mekkaObject):
	prefDict = {
		"grid1": 1,
		"grid2": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 190
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Grid Switcher",
			autosaveName=self.domain("mainwindow"),  # stores last window position and width
		)

		# UI elements:
		inset = 15

		formatter = integerFormatter(0)
		self.w.grid1 = SteppingEditText("auto", "1", callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		self.w.grid1.setToolTip("First grid step value.")
		self.w.grid2 = SteppingEditText("auto", "0", callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		self.w.grid2.setToolTip("Second grid step value.")
		self.w.currentGridStep = vanilla.TextBox("auto", self.gridStepReport(), sizeStyle='small')
		self.w.switchButton = vanilla.Button("auto", "Switch Grid", callback=self.GridOnOffMain)
		self.w.setDefaultButton(self.w.switchButton)

		# with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[grid1]-gap-[grid2(==grid1)]-inset-|",
				"H:|-inset-[currentGridStep]-inset-|",
				"H:|-inset-[switchButton]-inset-|",
				"V:|-inset-[grid1]-gap-[currentGridStep]-inset-[switchButton]-inset-|",
				{"view1": self.w.grid2, "attribute1": "centerY", "view2": self.w.grid1, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def gridStepReport(self, gridStep=None):
		if gridStep is None:
			font = Glyphs.font
			if not font:
				return "No font open."
			gridStep = font.grid
		return "Current Grid Step: %i" % gridStep

	def GridOnOffMain(self, sender):
		self.SavePreferences()

		font = Glyphs.font
		if not font:
			self.w.currentGridStep.set(self.gridStepReport())
			return

		gridStep1 = self.prefInt("grid1")
		gridStep2 = self.prefInt("grid2")

		if font.grid != gridStep1:
			newGridStep = gridStep1
		else:
			newGridStep = gridStep2

		font.grid = newGridStep
		self.w.currentGridStep.set(self.gridStepReport(newGridStep))


Gridswitch()
