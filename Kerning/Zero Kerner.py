# MenuTitle: Zero Kerner
# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

__doc__ = """
Add group kernings with value zero for pairs that are missing in one master but present in others. Helps preserve interpolatable kerning in OTVar exports.
"""

from vanilla import FloatingWindow, Button, TextBox, CheckBox, ProgressBar  # type: ignore
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
		windowWidth = 320
		windowHeight = 190
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Zero Kerner",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = TextBox((inset, linePos + 2, -inset, 44), u"Add zero-value group-to-group kernings for pairs that are missing in one master but present in others. Helps preserve interpolatable kerning in OTVars.", sizeStyle='small', selectable=True)
		linePos += lineHeight * 2.5

		self.w.limitToCurrentMaster = CheckBox((inset + 2, linePos - 1, -inset, 20), u"Limit to current master only (otherwise, all masters)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.limitToCurrentMaster.getNSButton().setToolTip_("Will apply zero kernings only to the currently selected master. Uncheck if all masters should be zero-kerned.")
		linePos += lineHeight

		self.w.reportInMacroWindow = CheckBox((inset + 2, linePos - 1, -inset, 20), u"Detailed report in Macro Window", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportInMacroWindow.getNSButton().setToolTip_("If checked, will write a progress report in the Macro Window (Cmd-Opt-M).")
		linePos += lineHeight

		self.w.progress = ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		linePos += lineHeight

		self.w.status = TextBox((inset, -20 - inset, -120 - inset, 14), u"", sizeStyle='small', selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.removeButton = Button((-160 - inset, -20 - inset, -80 - inset, -inset), "Remove", callback=self.ZeroKernerMain)

		self.w.addButton = Button((-70 - inset, -20 - inset, -inset, -inset), "Add", callback=self.ZeroKernerMain)
		self.w.setDefaultButton(self.w.addButton)

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
		self.w.status.set(statusMessage.strip())

	def ZeroKernerMain(self, sender: Any = None) -> None:
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
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
						otherMasterKerning = thisFont.kerning[otherMaster.id]
						kerningLength = len(otherMasterKerning)

						for j, leftGroup in enumerate(otherMasterKerning.keys()):
							kernCount = j * masterCountPart / kerningLength
							self.w.progress.set(masterCount + kernCount)

							if leftGroup.startswith("@"):
								for rightGroup in list(otherMasterKerning[leftGroup].keys()):
									if rightGroup.startswith("@"):
										if otherMasterKerning[leftGroup][rightGroup] != 0:
											for j, thisMaster in enumerate(theseMasters):

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
				self.w.status.set("Done.")
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Zero Kerner Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ZeroKerner()
