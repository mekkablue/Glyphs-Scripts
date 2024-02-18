# MenuTitle: Exception Cleaner
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Compares every exception to the group kerning available for the same pair. If the difference is below a threshold, remove the kerning exception.
"""

import vanilla
from AppKit import NSBeep
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


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
		windowHeight = 190
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Exception Cleaner",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset, line, lineHeight = 15, 10, 22

		self.w.text_1 = vanilla.TextBox((inset, line, -inset, lineHeight * 2), "Delete all kerning exceptions in the current master if they are less than the threshold value away from their corresponding group-to-group kerning:", sizeStyle='small')
		line += int(lineHeight * 1.5)

		self.w.text_2 = vanilla.TextBox((inset, line + 3, 200, lineHeight), "Required minimum kern difference:", sizeStyle='small')
		self.w.threshold = vanilla.EditText((inset + 200, line, -15, 20), "10", sizeStyle='small', callback=self.SavePreferences)
		self.w.threshold.getNSTextField().setToolTip_("A kern exception must be at least this number of units different from its corresponding group kern pair, otherwise it will be deleted.")
		line += lineHeight

		self.w.selectedGlyphsOnly = vanilla.CheckBox((inset, line, -inset, lineHeight), "Only consider pairs where at least one glyph is currently selected", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.selectedGlyphsOnly.getNSButton().setToolTip_("If enabled, respects your current glyph selection. Will only process kern pairs if one or both of the involved glyphs are in your selection.")
		line += lineHeight

		self.w.onlyReportDontDelete = vanilla.CheckBox((inset, line, -inset, lineHeight), "Only report, do not delete pairs yet", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.onlyReportDontDelete.getNSButton().setToolTip_("Opens a new tab with affected pairs, but does not delete any kerning.")
		line += lineHeight

		self.w.openTab = vanilla.CheckBox((inset, line, 180, 20), "Open tab with affected pairs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.getNSButton().setToolTip_("Opens a new tab for reporting. Otherwise will only write a report in Macro Window.")
		self.w.reuseTab = vanilla.CheckBox((inset + 180, line, -inset, 20), "Reuse current tab if possible", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.getNSButton().setToolTip_("If a tab is open and active already, will not open a new tab but rather reuse the current tab. Otherwise, will always open a new tab.")
		line += lineHeight

		# Buttons:
		self.w.nextMasterButton = vanilla.Button((-220 - inset, -20 - inset, -90 - inset, -inset), "Next Master", callback=self.NextMaster)
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Clean", callback=self.DeleteExceptionsTooCloseToGroupKerningMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		self.updateUI()

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
