# MenuTitle: BlueFuzzer
__doc__ = """
Extends all alignment zones (except for the baseline zone that should stay at 0).
"""

import objc
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
)
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


class BlueFuzzer(mekkaObject):
	prefDict = {
		"fuzzValue": 1,
		"allMasters": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 270
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"BlueFuzzer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		tooltipText = "Amount (in units) by which each alignment zone is extended on both sides. Negative values shrink the zones."
		self.w.fuzzValueText = vanilla.TextBox("auto", "Extend zones by", sizeStyle="small", selectable=True)
		fuzzFormatter = NSNumberFormatter.alloc().init()
		fuzzFormatter.setAllowsFloats_(False)  # whole numbers, negative values allowed
		self.w.fuzzValue = SteppingEditText("auto", "1", callback=self.SavePreferences, sizeStyle="small", formatter=fuzzFormatter)
		self.w.fuzzValueText.setToolTip(tooltipText)
		self.w.fuzzValue.setToolTip(tooltipText)

		self.w.allMasters = vanilla.CheckBox("auto", "Apply to all masters", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.setToolTip("Fuzz the alignment zones in all masters. If off, only the current master is changed.")

		self.w.runButton = vanilla.Button("auto", "Fuzz", callback=self.BlueFuzzerMain)
		self.w.runButton.setToolTip("Extend the alignment zones and open Font Info > Masters.")
		self.w.setDefaultButton(self.w.runButton)

		nsLabel = self.w.fuzzValueText.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# hug vertically so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[fuzzValueText]-gap-[fuzzValue(60)]-(>=inset)-|",
				"H:|-inset-[allMasters]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[fuzzValue]-row-[allMasters]-inset-[runButton]-inset-|",
				{"view1": self.w.fuzzValueText, "attribute1": "centerY", "view2": self.w.fuzzValue, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 12, "row": 6},
		)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def BlueFuzzerMain(self, sender):
		try:
			Font = Glyphs.font

			self.SavePreferences()
			fuzzValue = self.prefInt("fuzzValue")
			allMasters = self.prefBool("allMasters")

			if allMasters:
				masterList = Font.masters
			else:
				masterList = [Font.selectedFontMaster]

			for m in masterList:
				numOfZones = len(m.alignmentZones)
				for i in range(numOfZones):
					thisZone = m.alignmentZones[i]
					factor = 1
					if thisZone.size < 0:  # negative zone
						factor = -1
					if thisZone.position == 0 and factor == -1:  # baseline zone must stay where it is
						thisZone.setSize_(thisZone.size + fuzzValue * factor)
					else:
						thisZone.setPosition_(thisZone.position - fuzzValue * factor)
						thisZone.setSize_(thisZone.size + (fuzzValue * 2) * factor)

			self.w.close()
			Font.parent.windowController().showFontInfoWindowWithTabSelected_(1)  # master tab index
		except Exception as e:
			raise e


BlueFuzzer()
