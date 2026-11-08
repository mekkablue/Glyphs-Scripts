# MenuTitle: Exception Cleaner
__doc__ = """
Compares every exception to the group kerning available for the same pair. If the difference is below a threshold, remove the kerning exception.
"""

import objc
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSBeep,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
)
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def integerFormatter(minimum=None, maximum=None):
	"""Number formatter that only accepts integers, optionally within a range."""
	formatter = NSNumberFormatter.alloc().init()
	formatter.setAllowsFloats_(False)
	if minimum is not None:
		formatter.setMinimum_(minimum)
	if maximum is not None:
		formatter.setMaximum_(maximum)
	return formatter


class DeleteExceptionsTooCloseToGroupKerning(mekkaObject):
	prefDict = {
		"selectedGlyphsOnly": 0,
		"threshold": 10,
		"onlyReportDontDelete": 0,
		"reuseTab": 1,
		"openTab": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 430
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Exception Cleaner",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.text_1 = vanilla.TextBox("auto", "Delete all kerning exceptions in the current master if they are less than the threshold value away from their corresponding group-to-group kerning:", sizeStyle='small')
		self.w.text_1.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		tooltipText = "A kern exception must be at least this number of units different from its corresponding group kern pair, otherwise it will be deleted."
		self.w.text_2 = vanilla.TextBox("auto", "Required minimum kern difference:", sizeStyle='small', selectable=True)
		self.w.threshold = SteppingEditText("auto", "10", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter(0))
		self.w.text_2.setToolTip(tooltipText)
		self.w.threshold.setToolTip(tooltipText)

		self.w.selectedGlyphsOnly = vanilla.CheckBox("auto", "Only consider pairs where at least one glyph is currently selected", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.selectedGlyphsOnly.setToolTip("If enabled, respects your current glyph selection. Will only process kern pairs if one or both of the involved glyphs are in your selection.")

		self.w.onlyReportDontDelete = vanilla.CheckBox("auto", "Only report, do not delete pairs yet", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.onlyReportDontDelete.setToolTip("Opens a new tab with affected pairs, but does not delete any kerning.")

		self.w.openTab = vanilla.CheckBox("auto", "Open tab with affected pairs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.setToolTip("Opens a new tab for reporting. Otherwise will only write a report in Macro Window.")
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab if possible", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.setToolTip("If a tab is open and active already, will not open a new tab but rather reuse the current tab. Otherwise, will always open a new tab.")

		# Buttons:
		self.w.nextMasterButton = vanilla.Button("auto", "Next Master", callback=self.NextMaster)
		self.w.runButton = vanilla.Button("auto", "Clean", callback=self.DeleteExceptionsTooCloseToGroupKerningMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-inset-|",
				"H:|-inset-[text_2]-gap-[threshold(50)]-(>=inset)-|",
				"H:|-inset-[selectedGlyphsOnly]-(>=inset)-|",
				"H:|-inset-[onlyReportDontDelete]-(>=inset)-|",
				"H:|-inset-[openTab]-gap-[reuseTab]-(>=inset)-|",
				"H:|-(>=inset)-[nextMasterButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[text_1(descriptionHeight)]-row-[threshold]-row-[selectedGlyphsOnly]-checkRow-[onlyReportDontDelete]-checkRow-[openTab]-inset-[runButton]-inset-|",
				"V:[nextMasterButton]-inset-|",
				{"view1": self.w.text_2, "attribute1": "centerY", "view2": self.w.threshold, "attribute2": "centerY"},
				{"view1": self.w.reuseTab, "attribute1": "centerY", "view2": self.w.openTab, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "descriptionHeight": 42},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def NextMaster(self, sender=None):
		thisFont = Glyphs.font
		if thisFont:
			thisFont.masterIndex = (thisFont.masterIndex + 1) % len(thisFont.masters)
		else:
			NSBeep()

	def updateUI(self, sender=None):
		self.w.reuseTab.enable(self.w.openTab.get())

		if self.pref("onlyReportDontDelete"):
			self.w.runButton.setTitle("Report")
		else:
			self.w.runButton.setTitle("Clean")

	def glyphNameForKernSide(self, thisFont, kernSideName, isTheLeftSide=True):
		if kernSideName.startswith("@"):
			groupName = kernSideName.replace("@MMK_L_", "").replace("@MMK_R_", "").replace("@", "")
			for thisGlyph in thisFont.glyphs:
				if isTheLeftSide:
					if thisGlyph.rightKerningGroup == groupName:
						return thisGlyph.name
				else:
					if thisGlyph.leftKerningGroup == groupName:
						return thisGlyph.name
			print(
				"⚠️ No glyph found for %s group: @%s" % (
					"right" if isTheLeftSide else "left",  # if it is on the left side, we are looking for the right group and vice versa
					groupName,
				)
			)
			return None
		else:
			if thisFont.glyphs[kernSideName]:
				return kernSideName
			else:
				print("⚠️ Glyph not found: %s" % kernSideName)
				return None

	def DeleteExceptionsTooCloseToGroupKerningMain(self, sender):
		try:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			thisMaster = thisFont.selectedFontMaster
			thisMasterID = thisMaster.id

			onlyReportDontDelete = self.pref("onlyReportDontDelete")
			onlySelectedGlyphs = self.pref("selectedGlyphsOnly")
			threshold = self.prefInt("threshold")
			openTab = self.pref("openTab")
			reuseTab = self.pref("reuseTab")

			if onlySelectedGlyphs:
				selection = thisFont.selectedLayers
				if selection:
					selectedGlyphs = [layer.parent for layer in selection]
					selectedLeftGlyphGroups = [glyph.rightKerningGroup for glyph in selectedGlyphs]
					selectedRightGlyphGroups = [glyph.leftKerningGroup for glyph in selectedGlyphs]
				else:
					Message(
						title="Selection Error",
						message="You specified you want to process only selected glyphs, but no glyphs appear to be selected in the frontmost font.",
						OKButton="😬 Oops"
					)
					return
			else:
				selectedGlyphs = ()
				selectedLeftGlyphGroups = ()
				selectedRightGlyphGroups = ()

			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			print("Font: %s" % thisFont.familyName)
			print("Path: %s" % (thisFont.filepath if thisFont.filepath else "(unsaved)"))
			print("Master: %s" % thisMaster.name)
			print()

			# collect unnecessary kerning exceptions:
			unnecessaryKernPairs = []
			for leftSide in thisFont.kerning[thisMasterID].keys():
				if leftSide.startswith("@"):
					# group on the left side

					leftGlyphGroup = leftSide.replace("@MMK_L_", "")
					leftGlyphGroupMMK = leftSide

					for rightSide in thisFont.kerning[thisMasterID][leftSide].keys():

						if not rightSide.startswith("@"):
							# right side is exception:
							rightGlyph = thisFont.glyphForId_(rightSide)

							if onlySelectedGlyphs:
								okToContinue = (leftGlyphGroup in selectedLeftGlyphGroups) or (rightGlyph in selectedGlyphs)
							else:
								okToContinue = True

							if okToContinue:
								if not rightGlyph:
									# found orphaned kerning, report and abort:
									print("- Warning: could not find glyph for ID %s, consider cleaning up kerning" % rightSide)
								else:
									rightGlyphGroup = rightGlyph.leftKerningGroup

									if not rightGlyphGroup:
										# no corresponding kerning group, report and abort:
										print("- Note: Glyph '%s' has no left group; skipping." % rightGlyph.name)
									else:
										rightGlyphGroupMMK = "@MMK_R_%s" % rightGlyphGroup
										exceptionKerning = thisFont.kerning[thisMasterID][leftSide][rightSide]
										groupKerning = thisFont.kerningForPair(thisMasterID, leftGlyphGroupMMK, rightGlyphGroupMMK)
										if groupKerning is None or groupKerning > 100000:  # NSNotFound
											groupKerning = 0
										if abs(exceptionKerning - groupKerning) < threshold:
											print(
												"- Insignificant exception @%s-%s: %i vs. @%s-@%s: %i" % (
													leftGlyphGroup,
													rightGlyph.name,
													exceptionKerning,
													leftGlyphGroup,
													rightGlyphGroup,
													groupKerning,
												)
											)
											unnecessaryKernPairs.append(("@%s" % leftGlyphGroup, rightGlyph.name))

				else:
					# left side is exception
					leftGlyph = thisFont.glyphForId_(leftSide)
					okToContinue = (not onlySelectedGlyphs or leftGlyph in selectedGlyphs)
					if not leftGlyph:
						# found orphaned kerning, report and abort:
						if okToContinue:
							print("- Warning: could not find glyph for ID %s, consider cleaning up kerning" % leftSide)

					elif leftGlyph.export:
						# only proceed if the glyph is set to export:
						leftGlyphGroup = leftGlyph.rightKerningGroup

						if not leftGlyphGroup:
							# no corresponding kerning group, report and abort:
							if okToContinue:
								print("- Note: Glyph '%s' has no right group; skipping." % leftGlyph.name)

						else:
							# step through exceptions:
							leftGlyphGroupMMK = "@MMK_L_%s" % leftGlyphGroup

							for rightSide in thisFont.kerning[thisMasterID][leftSide].keys():
								if rightSide.startswith("@"):
									# exception-group:
									rightGlyph = None
									rightGlyphGroupMMK = rightSide
									rightGlyphGroup = rightSide.replace("@MMK_R_", "")
									okToContinue = okToContinue or (not onlySelectedGlyphs or rightGlyphGroup in selectedRightGlyphGroups)
								else:
									# exception-exception:
									rightGlyph = thisFont.glyphForId_(rightSide)
									rightGlyphGroup = rightGlyph.leftKerningGroup
									rightGlyphGroupMMK = "@MMK_R_%s" % rightGlyphGroup
									okToContinue = okToContinue or (not onlySelectedGlyphs or rightGlyph in selectedGlyphs)

								if okToContinue:
									exceptionKerning = thisFont.kerning[thisMasterID][leftSide][rightSide]
									groupKerning = thisFont.kerningForPair(thisMasterID, leftGlyphGroupMMK, rightGlyphGroupMMK)
									if groupKerning is None or groupKerning > 100000:  # NSNotFound
										groupKerning = 0

									if abs(exceptionKerning - groupKerning) < threshold:
										if rightGlyph:
											rightSideName = rightGlyph.name
										else:
											rightSideName = "@%s" % rightGlyphGroup

										print(
											"- Found unnecessary exception %s-%s: %i vs. @%s-@%s: %i" % (
												leftGlyph.name,
												rightSideName,
												exceptionKerning,
												leftGlyphGroup,
												rightGlyphGroup,
												groupKerning,
											)
										)
										unnecessaryKernPairs.append((leftGlyph.name, rightSideName))

			if not unnecessaryKernPairs:
				Message(
					title="No insignificant exceptions found",
					message="Found no kerning exceptions that are less than %i off the group kerning in %s, master ‘%s’." % (
						threshold,
						thisFont.familyName,
						thisMaster.name,
					),
					OKButton="😎Cool"
				)
			else:
				tabString = ""
				for kernPair in unnecessaryKernPairs:
					leftSide, rightSide = kernPair

					# DELETE
					if not onlyReportDontDelete:
						print("- Removing: %s-%s" % (leftSide, rightSide))
						if leftSide.startswith("@") and not leftSide.startswith("@MMK_L_"):
							leftSide = "@MMK_L_%s" % leftSide[1:]
						if rightSide.startswith("@") and not rightSide.startswith("@MMK_R_"):
							rightSide = "@MMK_R_%s" % rightSide[1:]
						thisFont.removeKerningForPair(thisMasterID, leftSide, rightSide)

					# COLLECT FOR REPORT
					leftGlyphName = self.glyphNameForKernSide(thisFont, leftSide, isTheLeftSide=True)
					rightGlyphName = self.glyphNameForKernSide(thisFont, rightSide, isTheLeftSide=False)
					if leftGlyphName is not None and rightGlyphName is not None:
						tabString += "/%s/%s " % (leftGlyphName, rightGlyphName)

				# REPORT
				if tabString and openTab:

					# prepare report message:
					countPairs = len(unnecessaryKernPairs)
					if onlyReportDontDelete:
						title = "%i insignificant pairs" % countPairs
						message = "Found %i insignificant exception%s in %s, master ‘%s’." % (
							countPairs,
							"" if countPairs == 1 else "s",
							thisFont.familyName,
							thisMaster.name,
						)
					else:
						title = "Removed unnecessary exceptions"
						message = "Deleted %i kerning exception%s in %s, master: ‘%s’." % (
							countPairs,
							"" if countPairs == 1 else "s",
							thisFont.familyName,
							thisMaster.name,
						)

					# Floating notification:
					Glyphs.showNotification(title, message + " Details in Macro Window.")

					# Macro Window:
					print()
					print(message)

					# Open tab with affected pairs:
					if thisFont.currentTab and reuseTab:
						thisFont.currentTab.text = tabString.strip()
					else:
						thisFont.newTab(tabString.strip())

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("'Exception Cleaner' Error: %s" % e)
			import traceback
			print(traceback.format_exc())


DeleteExceptionsTooCloseToGroupKerning()
