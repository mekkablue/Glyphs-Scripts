# MenuTitle: BlueFuzzer
__doc__ = """
Extends all alignment zones (except for the baseline zone that should stay at 0).
"""

import vanilla
from mekkablue import mekkaObject, SteppingEditText, integerFormatter, makeWindowResizable
from GlyphsApp import Glyphs
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
	"current master of current font",
	"⚠️ ALL masters of current font",
	"⚠️ current masters of ALL open fonts",
	"⚠️ ALL masters of ALL open fonts",
)


class BlueFuzzer(mekkaObject):
	prefDict = {
		"fuzzValue": 1,
		"scope": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"BlueFuzzer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		tooltipText = "Amount (in units) by which each alignment zone is extended on both sides. Negative values shrink the zones."
		self.w.fuzzValueText = vanilla.TextBox("auto", "Extend zones by", sizeStyle="small", selectable=True)
		fuzzFormatter = integerFormatter()
		self.w.fuzzValue = SteppingEditText("auto", "1", callback=self.SavePreferences, sizeStyle="small", formatter=fuzzFormatter)
		self.w.fuzzValueText.setToolTip(tooltipText)
		self.w.fuzzValue.setToolTip(tooltipText)

		scopeTooltip = (
			"Determines which masters get their alignment zones changed:\n"
			"• current master of current font – the selected master of the frontmost font.\n"
			"• ⚠️ ALL masters of current font – every master of the frontmost font.\n"
			"• ⚠️ current masters of ALL open fonts – the selected master of every open font.\n"
			"• ⚠️ ALL masters of ALL open fonts – every master of every open font."
		)
		self.w.scopeLabel = vanilla.TextBox("auto", "Apply to:", sizeStyle="small", selectable=True)
		self.w.scope = vanilla.PopUpButton("auto", scopeOptions, callback=self.SavePreferences, sizeStyle="small")
		self.w.scopeLabel.setToolTip(scopeTooltip)
		self.w.scope.setToolTip(scopeTooltip)

		self.w.runButton = vanilla.Button("auto", "Fuzz", callback=self.BlueFuzzerMain)
		self.w.runButton.setToolTip("Extend the alignment zones and open Font Info > Masters.")
		self.w.setDefaultButton(self.w.runButton)

		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")

		nsStatus = self.w.status.getNSTextField()
		nsStatus.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		nsStatus.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		nsRunButton = self.w.runButton.getNSButton()
		nsRunButton.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsRunButton.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		for label in (self.w.fuzzValueText, self.w.scopeLabel):
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# hug vertically so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[fuzzValueText]-gap-[fuzzValue(>=50)]-inset-|",
				"H:|-inset-[scopeLabel]-gap-[scope]-inset-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[fuzzValue]-row-[scope]-inset-[runButton]-inset-|",
				{"view1": self.w.fuzzValueText, "attribute1": "centerY", "view2": self.w.fuzzValue, "attribute2": "centerY"},
				{"view1": self.w.scopeLabel, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				{"view1": self.w.scopeLabel, "attribute1": "width", "view2": self.w.fuzzValueText, "attribute2": "width"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 12, "row": 6},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def BlueFuzzerMain(self, sender):
		masterName = "start"
		try:
			frontFont = Glyphs.font
			if frontFont is None:
				self.setStatus("⚠️ No font open.")
				return

			self.SavePreferences()
			fuzzValue = self.prefInt("fuzzValue")
			scope = self.prefInt("scope")

			# collect (font, master) pairs in the chosen scope:
			targets = []
			if scope == 0:
				targets = [(frontFont, frontFont.selectedFontMaster)]
			elif scope == 1:
				targets = [(frontFont, master) for master in frontFont.masters]
			elif scope == 2:
				targets = [(font, font.selectedFontMaster) for font in Glyphs.fonts]
			else:
				targets = [(font, master) for font in Glyphs.fonts for master in font.masters]
			multipleFonts = len(set(id(font) for font, master in targets)) > 1

			self.setStatus(f"🛠️ Processing {len(targets)} master{'' if len(targets) == 1 else 's'}…")
			for font, master in targets:
				masterName = f"{font.familyName} – {master.name}" if multipleFonts else master.name
				self.setStatus(f"🔠 {masterName}")
				numOfZones = len(master.alignmentZones)
				for i in range(numOfZones):
					thisZone = master.alignmentZones[i]
					factor = 1
					if thisZone.size < 0:  # negative zone
						factor = -1
					if thisZone.position == 0 and factor == -1:  # baseline zone must stay where it is
						thisZone.setSize_(thisZone.size + fuzzValue * factor)
					else:
						thisZone.setPosition_(thisZone.position - fuzzValue * factor)
						thisZone.setSize_(thisZone.size + (fuzzValue * 2) * factor)

			self.setStatus(f"✅ Fuzzed the zones of {len(targets)} master{'' if len(targets) == 1 else 's'}.")
			self.w.close()
			frontFont.parent.windowController().showFontInfoWindowWithTabSelected_(1)  # master tab index
		except Exception as e:
			self.setStatus(f"❌ Error at {masterName}. Details in Macro Window.")
			raise e


BlueFuzzer()
