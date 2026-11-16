# MenuTitle: Zero Kerner
__doc__ = """
Add group kernings with value zero for pairs that are missing in one master but present in others. Helps preserve interpolatable kerning in OTVar exports.
"""

from vanilla import FloatingWindow, Button, TextBox, CheckBox, ProgressBar  # type: ignore
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSNotFound  # type: ignore
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject
from typing import Any


class ZeroKerner(mekkaObject):
	prefDict = {
		"limitToCurrentMaster": 0,
		"reportInMacroWindow": 0,
	}

	def __init__(self) -> None:
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Zero Kerner",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = TextBox("auto", "Add zero-value group-to-group kernings for pairs that are missing in one master but present in others. Helps preserve interpolatable kerning in OTVars.", sizeStyle='small', selectable=True)
		# the text wraps: it takes the width it is given, and has a fixed height in the rules
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.limitToCurrentMaster = CheckBox("auto", "Limit to current master only (otherwise, all masters)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.limitToCurrentMaster.setToolTip("Will apply zero kernings only to the currently selected master. Uncheck if all masters should be zero-kerned.")

		self.w.reportInMacroWindow = CheckBox("auto", "Detailed report in Macro Window", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportInMacroWindow.setToolTip("If checked, will write a progress report in the Macro Window (Cmd-Opt-M).")

		self.w.progress = ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		self.w.status = TextBox("auto", "🤖 Ready.", sizeStyle='small', selectable=True)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.removeButton = Button("auto", "Remove", callback=self.ZeroKernerMain)
		self.w.removeButton.setToolTip("Removes group-to-group kerning pairs with value zero.")

		self.w.addButton = Button("auto", "Add", callback=self.ZeroKernerMain)
		self.w.addButton.setToolTip("Adds zero-value group-to-group kerning pairs where they are missing in a master.")
		self.w.setDefaultButton(self.w.addButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[limitToCurrentMaster]-(>=inset)-|",
				"H:|-inset-[reportInMacroWindow]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-inset-[status]-(>=gap)-[removeButton(>=70)]-gap-[addButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText(42)]-row-[limitToCurrentMaster]-checkRow-[reportInMacroWindow]-sectionGap-[progress(16)]-inset-[addButton]-inset-|",
				"V:[removeButton]-inset-|",
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.addButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "checkRow": 5, "sectionGap": 14},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def report(self, statusMessage: str, reportInMacroWindow: bool = False, emptyLine: bool = False) -> None:
		statusMessage = statusMessage.strip()
		if reportInMacroWindow:
			print("  %s" % statusMessage)
			if emptyLine:
				print()
		self.w.status.set("🛠️ " + statusMessage)

	def ZeroKernerMain(self, sender: Any = None) -> None:
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				self.w.status.set("❌ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			limitToCurrentMaster = self.pref("limitToCurrentMaster")
			reportInMacroWindow = self.pref("reportInMacroWindow")
			self.w.progress.set(0)  # set progress indicator to zero

			shouldRemoveZeroKerns = sender == self.w.removeButton

			if reportInMacroWindow:
				Glyphs.clearLog()
				Glyphs.showMacroWindow()
				print("Zero Kerner Report for %s" % thisFont.familyName)
				print(thisFont.filepath)
				print()

			if len(thisFont.masters) < 2:
				Message(title="Zero Kerner Error", message="Zero Kerner only makes sense if there is more than one master in the font.", OKButton="Ooops")
			else:
				if limitToCurrentMaster:
					masters = (thisFont.selectedFontMaster, )
				else:
					masters = thisFont.masters

				masterCountPart = 100.0 / len(thisFont.masters)

				if shouldRemoveZeroKerns:
					# REMOVE ZERO KERNS
					for i, thisMaster in enumerate(masters):
						if thisMaster.id not in thisFont.kerning.keys():
							self.report("%s: no kerning at all in this master. Skipping." % (thisMaster.name), reportInMacroWindow=reportInMacroWindow, emptyLine=True)
							continue

						masterCount = masterCountPart * i
						kerningLength = len(thisFont.kerning[thisMaster.id])

						self.w.progress.set(masterCount)
						pairsToBeRemoved = []

						for j, leftSide in enumerate(thisFont.kerning[thisMaster.id].keys()):
							kernCount = j * masterCountPart / kerningLength
							self.w.progress.set(masterCount + kernCount)

							if leftSide.startswith("@"):
								for rightSide in thisFont.kerning[thisMaster.id][leftSide].keys():

									if rightSide.startswith("@") and thisFont.kerning[thisMaster.id][leftSide][rightSide] == 0:
										pairsToBeRemoved.append((leftSide, rightSide))
										self.report(
											"%s: will remove @%s-@%s" % (thisMaster.name, leftSide[7:], rightSide[7:]),
											reportInMacroWindow,
										)

						self.report(
							"%s: removing %i zero kerns" % (thisMaster.name, len(pairsToBeRemoved)),
							reportInMacroWindow,
							emptyLine=True,
						)
						for pair in pairsToBeRemoved:
							LeftKey, RightKey = pair
							thisFont.removeKerningForPair(thisMaster.id, LeftKey, RightKey)

				else:
					# ADD ZERO KERNS
					for i, otherMaster in enumerate(thisFont.masters):
						masterCount = masterCountPart * i
						self.w.progress.set(masterCount)

						theseMasters = [m for m in masters if m is not otherMaster]
						if otherMaster.id not in thisFont.kerning.keys():
							continue
						otherMasterKerning = thisFont.kerning[otherMaster.id]
						kerningLength = len(otherMasterKerning)

						for j, leftGroup in enumerate(otherMasterKerning.keys()):
							kernCount = j * masterCountPart / kerningLength
							self.w.progress.set(masterCount + kernCount)

							if leftGroup.startswith("@"):
								for rightGroup in list(otherMasterKerning[leftGroup].keys()):
									if rightGroup.startswith("@"):
										if otherMasterKerning[leftGroup][rightGroup] != 0:
											for thisMaster in theseMasters:

												self.report(
													"Verifying @%s-@%s" % (leftGroup[7:], rightGroup[7:]),
													reportInMacroWindow=False,
												)

												if not thisFont.kerningForPair(thisMaster.id, leftGroup, rightGroup) or \
													thisFont.kerningForPair(thisMaster.id, leftGroup, rightGroup) >= NSNotFound:
													thisFont.setKerningForPair(thisMaster.id, leftGroup, rightGroup, 0.0)
													self.report(
														"%s: zero kern @%s-@%s" % (thisMaster.name, leftGroup[7:], rightGroup[7:]),
														reportInMacroWindow,
													)

				self.w.progress.set(100.0)
				self.w.status.set("✅ Done.")
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Zero Kerner Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ZeroKerner()
