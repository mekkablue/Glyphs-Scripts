# MenuTitle: Auto Bumper
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Specify a minimum distance, left and right glyphs, and Auto Bumper will add the minimum necessary kerning for the current master.
"""

import vanilla
from mekkablue import mekkaObject, reportTimeInNaturalLanguage
from timeit import default_timer as timer
from kernanalysis import intervalList, minDistanceBetweenTwoLayers, sortedIntervalsFromString, stringToListOfGlyphsForFont, effectiveKerning, distanceFromEntry
from AppKit import NSColor
from GlyphsApp import Glyphs, Message

defaultStrings = """

iíĭǐîïịìỉīįĩjĵ
ÍǏÎÏİÌỈĪĨ  # UPPERCASE
/iacute.sc/icaron.sc/icircumflex.sc/idieresis.sc/idotaccent.sc/igrave.sc/ihookabove.sc/imacron.sc/itilde.sc
FTKVWY  # TOP RIGHT
f
ÐĦðđħ/Lslash/lslash
bhlkþ
rtkvwxyz

ĄĘĮ  # OGONEK
gjpy  # DESCENDER

AKLRXZ  # BOTTOM RIGHT
sxz  # BOTTOM LEFT

abcdefghijklmnopqrstuvwxyzßð
ABCDEFGHIJKLMNOPQRSTUVWXYZẞÞ
/a.sc/b.sc/c.sc/d.sc/e.sc/f.sc/g.sc/h.sc/i.sc/j.sc/k.sc/l.sc/m.sc/n.sc/o.sc/p.sc/q.sc/r.sc/s.sc/t.sc/u.sc/v.sc/w.sc/x.sc/y.sc/z.sc/germandbls.sc/thorn.sc

({[„“”«»¿¡/slash
„“”]})*®?!»«/slash
/parenleft.sc/braceleft.sc/bracketleft.sc
/parenright.sc/braceright.sc/bracketright.sc

/Ohorn/Uhorn #VIETNAMESE
/ohorn/uhorn #VIETNAMESE
/ohorn.sc/uhorn.sc #VIETNAMESE
/i/iacute/idotbelow/igrave/ihookabove/itilde #VIETNAMESE
/i.sc/iacute.sc/idotbelow.sc/igrave.sc/ihookabove.sc/itilde.sc #VIETNAMESE

»«‹›/quotesinglbase/quotedblbase/quotedblleft/quotedblright/quoteleft/quoteright/quotedbl/quotesingle

/lcaron/dcaron/tcaron #CZECH AND SLOVAK
ňčěšäížůô #CZECH AND SLOVAK EXCEPTIONS
"“”]})*?!»« #CZECH AND SLOVAK GROUPS

/a.sc/aogonek.sc/ae.sc/b.sc/c.sc/d.sc/e.sc/f.sc/g.sc/h.sc/i.sc/j.sc/k.sc/l.sc/m.sc/n.sc/eng.sc/o.sc/oe.sc/p.sc/thorn.sc/q.sc/r.sc/s.sc/germandbls.sc/t.sc/u.sc/v.sc/w.sc/x.sc/y.sc/z.sc
/slash
/iacute.sc/icaron.sc/icircumflex.sc/idieresis.sc/idotaccent.sc/igrave.sc/imacron.sc/iogonek.sc/itilde.sc/icaron.sc

"""


class Bumper(mekkaObject):
	prefDict = {
		"leftGlyphs": "TVWY",
		"leftIsGroups": 1,
		"rightGlyphs": "iíĭǐîïịìỉīįĩjĵ",
		"rightIsGroups": 0,

		"minDistance": 50,
		"maxDistance": 200,
		"roundFactor": 10,
		"speedPopup": 2,
		"ignoreIntervals": "",
		"keepExistingKerning": 1,
		"excludeNonExporting": 1,
		"reportInMacroWindow": 1,
		"openNewTabWithKernPairs": 0,
		"resetExceptionsForGroups": 1,
		"reuseCurrentTab": 1,
		"avoidZeroKerning": 1,
		"suffix": "",

		"kernStrings": defaultStrings,
	}

	def __init__(self):
		# register prefs if run for the first time:

		# Window 'self.w':
		windowWidth = 500
		windowHeight = 365
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 500  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Auto Bumper",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset, lineHeight, linePos = 14, 24, -10
		linePos += lineHeight

		self.w.text_1 = vanilla.TextBox((inset, linePos, -inset, 14), "Add supplementary kerning for specified glyphs in the current master:", sizeStyle='small')
		linePos += lineHeight

		self.w.swapButton = vanilla.SquareButton((-inset - 20, linePos, -inset, 42), "↰\n↲", callback=self.swap)

		self.w.text_left = vanilla.TextBox((inset, linePos + 3, 80, 14), "Left glyphs:", sizeStyle='small')
		self.w.leftGlyphs = vanilla.ComboBox((inset + 80, linePos, -inset - 102, 18), self.kernStringList(self), callback=self.sideGlyphsAction, sizeStyle='small')
		self.w.leftGlyphs.getNSComboBox().setToolTip_("Measures the specified glyphs from their right side to the following glyph. You can type the character ‘é’ or the slash-escaped glyph name ‘/eacute’. Or specify a category after an at sign ‘@Letter’, add a subcategory after a colon ‘@Letter:Lowercase’.\nAdd default strings in the text box at the bottom of the window. Expand the window at the bottom to access it.")
		self.w.leftIsGroups = vanilla.CheckBox((-inset - 94, linePos + 1, -inset - 22, 17), "As groups", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.leftIsGroups.getNSButton().setToolTip_("If on, will measure only the specified glyph, but set the calculated kerning for the whole right group of the glyph (i.e., add group kerning). If off, will set the kerning for the glyph only (i.e., add an exception).")
		linePos += lineHeight

		self.w.text_right = vanilla.TextBox((inset, linePos + 3, 80, 14), "Right glyphs:", sizeStyle='small')
		self.w.rightGlyphs = vanilla.ComboBox((inset + 80, linePos, -inset - 102, 18), self.kernStringList(self), callback=self.sideGlyphsAction, sizeStyle='small')
		self.w.rightGlyphs.getNSComboBox().setToolTip_("Measures from the previous glyphs to the specified glyphs to their left side. You can type the character ‘é’ or the slash-escaped glyph name ‘/eacute’. Or specify a category after an at sign ‘@Letter’, add a subcategory after a colon ‘@Letter:Lowercase’.\nAdd default strings in the text box at the bottom of the window. Expand the window at the bottom to access it.")
		self.w.rightIsGroups = vanilla.CheckBox((-inset - 94, linePos + 1, -inset - 22, 17), "As groups", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.rightIsGroups.getNSButton().setToolTip_("If on, will measure only the specified glyph, but set the calculated kerning for the whole left group of the glyph (i.e., add group kerning). If off, will set the kerning for the glyph only (i.e., add an exception).")
		linePos += lineHeight

		self.w.suffixText = vanilla.TextBox((inset, linePos + 3, 80, 14), "Add suffix:", sizeStyle='small', selectable=True)
		self.w.suffix = vanilla.EditText((inset + 80, linePos, 150, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.suffix.getNSTextField().setToolTip_("Looks for the suffixed version of the listed glyphs, with this suffix added to the name. Useful with .sc for smallcaps. Enter WITH the leading dot for dot suffixes. Can also be used with 'superior' for figures.")
		linePos += lineHeight

		self.w.text_21 = vanilla.TextBox((inset, linePos + 3, 80, 14), "Min distance:", sizeStyle='small')
		self.w.minDistance = vanilla.EditText((inset + 80, linePos, 60, 19), "50", sizeStyle='small', callback=self.SavePreferences)
		self.w.minDistance.getNSTextField().setPlaceholderString_("50")
		self.w.minDistance.getNSTextField().setToolTip_("Adds kerning if the shortest distance between two glyphs is shorter than specified value. You can also type ‘vw’ for the distance between v and w, and ‘vw+10’ for that distance plus 10 units. Leave blank or set to zero to ignore.")
		self.w.text_22 = vanilla.TextBox((inset + 80 * 2, linePos + 3, 80, 14), "Max distance:", sizeStyle='small')
		self.w.maxDistance = vanilla.EditText((inset + 80 * 3, linePos, 60, 19), "200", sizeStyle='small', callback=self.SavePreferences)
		self.w.maxDistance.getNSTextField().setPlaceholderString_("200")
		self.w.maxDistance.getNSTextField().setToolTip_("Adds kerning if the shortest distance between two glyphs is larger than specified value. You can also type ‘AV’ for the distance between A and V, and ‘AV-10’ for that distance minus 10 units. Leave blank or set to zero to ignore.")
		self.w.text_23 = vanilla.TextBox((inset + 80 * 4, linePos + 3, 80, 14), "Round by:", sizeStyle='small')
		self.w.roundFactor = vanilla.EditText((inset + 80 * 5, linePos, -inset, 19), "10", sizeStyle='small', callback=self.SavePreferences)
		self.w.roundFactor.getNSTextField().setPlaceholderString_("10")
		self.w.roundFactor.getNSTextField().setToolTip_("Rounds calculated kerning. Leave blank or set to zero to ignore.")
		linePos += lineHeight

		self.w.text_speed = vanilla.TextBox((inset, linePos + 3, 42, 14), "Speed:", sizeStyle='small')
		self.w.speedPopup = vanilla.PopUpButton((inset + 42, linePos + 1, 80, 17), ("very slow", "slow", "medium", "fast", "very fast"), callback=self.updateUI, sizeStyle='small')
		self.w.speedPopup.getNSPopUpButton().setToolTip_("Specifies the number of measurements. Measuring is processor-intensive and can take a while. Slow: many measurements, fast: few measurements.")
		intervalIndex = self.pref("speedPopup")
		if intervalIndex is None:
			intervalIndex = 0
		self.w.text_speedExplanation = vanilla.TextBox((inset + 42 + 90, linePos + 3, -15, 14), "Measuring every %i units." % intervalList[intervalIndex], sizeStyle='small')
		linePos += lineHeight

		self.w.text_6 = vanilla.TextBox((inset, linePos + 3, 130, 14), "Ignore height intervals:", sizeStyle='small')
		self.w.ignoreIntervals = vanilla.EditText((inset + 130, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreIntervals.getNSTextField().setPlaceholderString_("200:300, 400:370, -200:-150")
		self.w.ignoreIntervals.getNSTextField().setToolTip_("Does not measure on y coordinates in intervals specified as y1:y2. Separate multiple intervals with commas. You can also specify glyph names, e.g. x:o (from bottom of x to top of o).")
		linePos += lineHeight

		smallCheckboxHeight = 20
		tabStop = 235

		self.w.keepExistingKerning = vanilla.CheckBox((inset + 5, linePos, tabStop - inset, smallCheckboxHeight), "Keep (don’t overwrite) existing kerning", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.keepExistingKerning.getNSButton().setToolTip_("If the kern pair already exists in the font, it will not be overwritten.")
		self.w.resetExceptionsForGroups = vanilla.CheckBox((inset + tabStop, linePos, -inset, smallCheckboxHeight), "Delete exceptions when group-kerning", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.resetExceptionsForGroups.getNSButton().setToolTip_("When Auto Bumper is supposed to add group kerning (when you have one or both of the ‘As groups’ checkboxes on), and a group kern is overridden by a kerning exception, then delete that kerning exception. Does nothing if no ‘As groups’ checkboxes are selected.")
		linePos += lineHeight

		self.w.excludeNonExporting = vanilla.CheckBox((inset + 5, linePos, tabStop - inset, smallCheckboxHeight), "Exclude non-exporting glyphs", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.excludeNonExporting.getNSButton().setToolTip_("If one of the specified glyphs is not set to export, Auto Bumper will skip it.")
		self.w.avoidZeroKerning = vanilla.CheckBox((inset + tabStop, linePos, -inset, smallCheckboxHeight), "Avoid zero kerns", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.avoidZeroKerning.getNSButton().setToolTip_("If the calculated (and rounded) kerning value is 0, it will not be added to the font.")
		linePos += lineHeight

		self.w.reportInMacroWindow = vanilla.CheckBox((inset + 5, linePos, -inset, smallCheckboxHeight), "Also report in Macro Window (a few seconds slower)", value=False, sizeStyle='small', callback=self.SavePreferences)
		self.w.reportInMacroWindow.getNSButton().setToolTip_("Outputs a detailed report in the Macro Window, and opens it.")
		linePos += lineHeight

		self.w.openNewTabWithKernPairs = vanilla.CheckBox((inset + 5, linePos, tabStop - inset, smallCheckboxHeight), "Open Edit tab with new kern pairs", value=False, sizeStyle='small', callback=self.SavePreferences)
		self.w.openNewTabWithKernPairs.getNSButton().setToolTip_("If kern pairs were added, opens them in a new Edit tab, for inspection.")
		self.w.reuseCurrentTab = vanilla.CheckBox((inset + tabStop, linePos, -inset, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseCurrentTab.getNSButton().setToolTip_("If enabled, will not open a new tab with newly added kern pairs, but reuse the current Edit tab. Will open an Edit tab if none is open. Only available in connection with the Open Edit Tab checkbox.")
		linePos += lineHeight

		# Progress Bar:
		self.w.bar = vanilla.ProgressBar((inset, linePos, -inset, 16))
		linePos += lineHeight

		# (Hidden) Preferences Kern Strings:
		self.w.kernStrings = vanilla.TextEditor((1, linePos, -1, -45), callback=self.SavePreferences)
		self.w.kernStrings.getNSTextView().setToolTip_("Add your default kern strings here. They will show up in the left/right dropdowns at the top. Everything after a hashtag (#) is ignored. Use blank lines for structuring.")

		self.w.text_kernStrings = vanilla.TextBox((inset, -14 - inset, -100 - inset, -inset), "Expand window below to access default strings.", sizeStyle='small')
		self.w.text_kernStrings.getNSTextField().setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0, 0, 0, 0.2))

		# Buttons:
		self.w.nextButton = vanilla.Button((-inset - 210, -20 - inset, -inset - 100, -inset), "Next Master", callback=self.masterSwitch)

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Kern", callback=self.BumperMain)
		self.w.setDefaultButton(self.w.runButton)

		self.w.status = vanilla.TextBox((inset, -28 - inset, -inset - 210, 14), "Ready.", sizeStyle="small", selectable=True)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def masterSwitch(self, sender=None):
		if sender is self.w.nextButton:
			Glyphs.font.masterIndex += 1

	def kernStringList(self, sender):
		kernStrings = self.pref("kernStrings").splitlines()
		if kernStrings:
			return kernStrings
		else:
			return defaultStrings.splitlines()

	def swap(self, sender=None):
		rightEntry = self.w.rightGlyphs.get()
		rightGroupEntry = self.w.rightIsGroups.get()
		leftEntry = self.w.leftGlyphs.get()
		leftGroupEntry = self.w.leftIsGroups.get()

		self.w.rightGlyphs.set(leftEntry)
		self.w.rightIsGroups.set(leftGroupEntry)
		self.w.leftGlyphs.set(rightEntry)
		self.w.leftIsGroups.set(rightGroupEntry)

		self.SavePreferences(sender)

	def kernStringsAction(self, sender):
		self.SavePreferences()
		kernStrings = self.pref("kernStrings").splitlines()
		if kernStrings:
			self.w.leftGlyphs.setItems(kernStrings)
			self.w.rightGlyphs.setItems(kernStrings)

	def sideGlyphsAction(self, sender):
		self.SavePreferences()
		kernStrings = self.pref("kernStrings").splitlines()
		for thisItem in sender.getItems():
			if thisItem not in kernStrings:
				kernStrings = self.pref("kernStrings") + "\n%s" % thisItem
				self.setPref("kernStrings", kernStrings)

	def updateUI(self, sender=None):
		if sender is not None:
			self.SavePreferences()

		# enable/disable options based on settings:
		self.w.reuseCurrentTab.enable(onOff=self.pref("openNewTabWithKernPairs"))

		# update speed explanation:
		if sender == self.w.speedPopup:
			intervalIndex = self.pref("speedPopup")
			if intervalIndex is None:
				intervalIndex = 0
			self.w.text_speedExplanation.set("Measuring every %i units." % intervalList[intervalIndex])

	def addMissingKerning(self, thisFont, thisMasterID, leftSide, rightSide, minMaxDistance, distanceBetweenShapes, existingKerning=0):
		# query user settings:
		shouldReportInMacroWindow = self.pref("reportInMacroWindow")
		shouldKeepExistingKerning = self.prefBool("keepExistingKerning")
		avoidZeroKerning = self.pref("avoidZeroKerning")
		try:
			roundValue = self.prefFloat("roundFactor")
		except:
			roundValue = 1.0
		roundValue = max(roundValue, 1.0)

		# check for existing kerning:
		# existingKerning = thisFont.kerningForPair(thisMasterID, leftSide, rightSide)
		kerningExists = existingKerning < 1000000  # NSNotDefined constant
		if not kerningExists:
			existingKerning = 0
		newKernValue = round((minMaxDistance - distanceBetweenShapes + existingKerning) / roundValue, 0) * roundValue

		# add only if it is OK:
		if newKernValue == 0.0 and avoidZeroKerning:
			if shouldReportInMacroWindow:
				print("- %s %s: zero kerning, not added." % (leftSide, rightSide))
			return False  # do not increase kern count
		else:
			if kerningExists and shouldKeepExistingKerning:
				if shouldReportInMacroWindow:
					print("- %s %s: keeps existing %i (instead of new %i)." % (leftSide, rightSide, existingKerning, newKernValue))
				return False  # do not increase kern count
			else:
				thisFont.setKerningForPair(thisMasterID, leftSide, rightSide, newKernValue)
				if shouldReportInMacroWindow:
					print("- %s %s: %i" % (leftSide, rightSide, newKernValue))
				return True  # increase kern count

	def BumperMain(self, sender):
		try:
			# save prefs
			self.SavePreferences()

			# query frontmost fontmaster:
			thisFont = Glyphs.font
			thisMaster = thisFont.selectedFontMaster
			thisMasterID = thisMaster.id

			# start reporting to macro window:
			shouldReportInMacroWindow = self.pref("reportInMacroWindow")
			if shouldReportInMacroWindow:
				Glyphs.clearLog()
				print("Auto Bumper Report for %s, master %s:\n" % (thisFont.familyName, thisMaster.name))
			self.w.status.set(f"Bumping in ‘{thisMaster.name}’")

			# reset progress bar:
			self.w.bar.set(0)
			# start taking time:
			start = timer()

			# COLLECTING THE DATA WE NEED:

			# query user input:
			step = intervalList[self.pref("speedPopup")]
			ignoreIntervals = sortedIntervalsFromString(self.pref("ignoreIntervals"), font=thisFont, mID=thisMasterID)
			shouldExcludeNonExporting = self.prefBool("excludeNonExporting")
			resetExceptionsForGroups = self.prefBool("resetExceptionsForGroups")
			leftIsGroups = self.prefBool("leftIsGroups")
			rightIsGroups = self.prefBool("rightIsGroups")

			minDistance = distanceFromEntry(self.pref("minDistance"), thisFont, thisMasterID)
			maxDistance = distanceFromEntry(self.pref("maxDistance"), thisFont, thisMasterID)

			roundFactor = self.pref("roundFactor")
			try:
				roundFactor = float(roundFactor)
			except:
				roundFactor = None
				self.w.roundFactor.set("")
				self.SavePreferences()

			suffix = self.pref("suffix")
			cleanedSuffix = ""
			if suffix is None:
				suffix = ""
			else:
				suffix = suffix.strip()
				for letter in suffix:
					if letter in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-":
						cleanedSuffix += letter
			if cleanedSuffix != suffix:
				Message(
					title="Invalid Suffix Error",
					message="The suffix you entered ('%s') is invalid. The script suggests '%s' instead. Please verify and try again." % (suffix, cleanedSuffix),
					OKButton=None
				)
				self.w.suffix.set(cleanedSuffix)
				self.SavePreferences()
			else:
				# find list of glyph names:
				firstGlyphList = stringToListOfGlyphsForFont(
					self.pref("leftGlyphs"),
					thisFont,
					report=shouldReportInMacroWindow,
					excludeNonExporting=shouldExcludeNonExporting,
					suffix=suffix,
				)
				secondGlyphList = stringToListOfGlyphsForFont(
					self.pref("rightGlyphs"),
					thisFont,
					report=shouldReportInMacroWindow,
					excludeNonExporting=shouldExcludeNonExporting,
					suffix=suffix,
				)

				# report key values for kerning:
				if shouldReportInMacroWindow:
					print()
					if minDistance is not None:
						print("Minimum Distance: %i" % minDistance)
					if maxDistance is not None:
						print("Maximum Distance: %i" % maxDistance)
					if roundFactor is not None:
						print("Rounding: %i" % roundFactor)

					print()
					print("⬅️ L glyphs:\n%s\n" % ", ".join([g.name for g in firstGlyphList]))
					print("➡️ R glyphs:\n%s\n" % ", ".join([g.name for g in secondGlyphList]))

				# CREATE KERNING DATA:

				tabString = ""
				kernCount = 0
				numOfGlyphs = len(firstGlyphList)
				for index in range(numOfGlyphs):
					# update progress bar:
					self.w.bar.set(int(100 * (float(index) / numOfGlyphs)))
					# determine left glyph:
					leftGlyph = firstGlyphList[index]
					leftLayer = leftGlyph.layers[thisMasterID]
					leftGroup = leftGlyph.rightKerningGroup
					if leftIsGroups:
						if leftGroup:
							leftSide = "@MMK_L_%s" % leftGroup
						else:
							print("⚠️ Left glyph %s has no kerning group. Cannot apply group kerning." % leftGlyph.name)
							leftSide = None
					else:
						leftSide = leftGlyph.name

					# only continue if we could establish a left side:
					if leftSide:
						# cycle through right glyphs:
						for rightGlyph in secondGlyphList:
							rightLayer = rightGlyph.layers[thisMasterID]
							rightGroup = rightGlyph.leftKerningGroup
							if rightIsGroups:
								if rightGroup:
									rightSide = "@MMK_R_%s" % rightGroup
								else:
									print("⚠️ Right glyph %s has no kerning group. Cannot apply group kerning." % rightGlyph.name)
									rightSide = None
							else:
								rightSide = rightGlyph.name

							# only continue if we could establish a right side:
							if rightSide:
								if resetExceptionsForGroups:
									if leftIsGroups and thisFont.kerningForPair(thisMasterID, leftGlyph.name, rightSide) is not None:
										thisFont.removeKerningForPair(thisMasterID, leftGlyph.name, rightSide)
									if rightIsGroups and thisFont.kerningForPair(thisMasterID, leftSide, rightGlyph.name) is not None:
										thisFont.removeKerningForPair(thisMasterID, leftSide, rightGlyph.name)
									if (leftIsGroups and rightIsGroups) and thisFont.kerningForPair(thisMasterID, leftGlyph.name, rightGlyph.name) is not None:
										thisFont.removeKerningForPair(thisMasterID, leftGlyph.name, rightGlyph.name)

								kerning = effectiveKerning(leftGlyph.name, rightGlyph.name, thisFont, thisMasterID)
								distanceBetweenShapes = minDistanceBetweenTwoLayers(
									leftLayer, rightLayer, interval=step, kerning=kerning, report=False, ignoreIntervals=ignoreIntervals
								)

								# positive kerning (if desired):
								if minDistance and (distanceBetweenShapes is not None) and (distanceBetweenShapes < minDistance):
									if self.addMissingKerning(thisFont, thisMasterID, leftSide, rightSide, minDistance, distanceBetweenShapes, existingKerning=kerning):
										kernCount += 1
										tabString += "/%s/%s  " % (leftGlyph.name, rightGlyph.name)

								# negative kerning (if desired):
								if maxDistance and (distanceBetweenShapes is not None) and (distanceBetweenShapes > maxDistance):
									if self.addMissingKerning(thisFont, thisMasterID, leftSide, rightSide, maxDistance, distanceBetweenShapes, existingKerning=kerning):
										kernCount += 1
										tabString += "/%s/%s  " % (leftGlyph.name, rightGlyph.name)
							else:
								print("No right side.")

					tabString = tabString.strip()
					tabString += "\n"

				# FINISH UP AND REPORT:

				# update progress bar:
				self.w.bar.set(100)
				# take time:
				timereport = reportTimeInNaturalLanguage(timer() - start)

				# clean up the tab string:
				tabString = tabString.strip()
				while "\n\n" in tabString:
					tabString = tabString.replace("\n\n", "\n")

				# Report number of new kern pairs:
				if kernCount:
					report = f'Added {kernCount} kern pair{"s" if kernCount != 1 else ""} in {timereport}.'
				# or report that nothing was found:
				else:
					report = f'No kerning added ({timereport}).'

				# Floating notification:
				# notificationTitle = "Bumper: %s (%s)" % (thisFont.familyName, thisMaster.name)
				# Message(
				# 	title=notificationTitle,
				# 	message=report,
				# 	OKButton=None,
				# )
				self.w.status.set(f"✅ {report}")

				# Open new tab:
				if self.pref("openNewTabWithKernPairs"):
					if self.pref("reuseCurrentTab") and thisFont.currentTab:
						thisFont.currentTab.text = tabString
					else:
						thisFont.newTab(tabString)

				# Report in Macro Window:
				if shouldReportInMacroWindow:
					print()
					print(report)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Auto Bumper Error: %s" % e)
			import traceback
			print(traceback.format_exc())


Bumper()
