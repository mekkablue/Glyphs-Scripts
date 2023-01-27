#MenuTitle: KernCrasher
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Opens a new tab with Kerning Combos that crash in the current fontmaster.
"""

import vanilla
from timeit import default_timer as timer
from Foundation import NSNotFound
from kernanalysis import categoryList, intervalList, effectiveKerning

if Glyphs.versionNumber >= 3:
	caseDict = {
		"Uppercase": GSUppercase,
		"Lowercase": GSLowercase,
		"Smallcaps": GSSmallcaps,
		}

class KernCrasher(object):
	prefID = "com.mekkablue.KernCrasher"
	prefDict = {
		# "prefName": defaultValue,
		"minDistance": 0,
		"popupScript": "latin",
		"popupSpeed": 0,
		"popupLeftCat": 0,
		"popupRightCat": 0,
		"excludeSuffixes": ".locl, .alt, .sups, .sinf, .tf, .tosf, Ldot, ldot, Jacute, jacute",
		"excludeNonExporting": 1,
		"reportCrashesInMacroWindow": 0,
		"ignoreIntervals": "",
		"pathGlyphsOnly": 0,
		"reuseCurrentTab": 1,
		"limitRightSuffixes": "",
		"limitLeftSuffixes": "",
		"directionSensitive": "",
	}
	
	def __init__(self):
		# Window 'self.w':
		windowWidth = 410
		windowHeight = 370
		windowWidthResize = 800 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"KernCrasher", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName=self.domain("mainwindow") # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), u"Open tab with kern collisions in current master:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.textScript = vanilla.TextBox((inset, linePos + 2, 42, 14), u"Script:", sizeStyle='small', selectable=True)
		self.w.popupScript = vanilla.ComboBox((inset + 42, linePos - 1, 110, 18), ("latin", "cyrillic", "greek"), callback=self.SavePreferences, sizeStyle='small')
		self.w.popupScript.getNSComboBox().setToolTip_("Limits the kerning pairs only to glyphs of this script, and those of no script.")
		self.w.updateScriptsButton = vanilla.SquareButton((inset + 160, linePos, 20, 18), "↺", sizeStyle='small', callback=self.update)
		self.w.updateScriptsButton.getNSButton(
		).setToolTip_("Scans the frontost font for the scripts of all its glyphs (Latin, Greek, Cyrillic, Hebrew, Arabic, Thai, ...) and lists only those in the combo box.")
		self.w.textDistance = vanilla.TextBox((inset + 200, linePos + 2, 100, 14), "Min distance:", sizeStyle='small')
		self.w.minDistance = vanilla.EditText((inset + 280, linePos - 1, -15, 19), "10", sizeStyle='small')
		tooltipText = "Minimum distance required between glyphs in any given pairing with the current setup. Measured in units."
		self.w.textDistance.getNSTextField().setToolTip_(tooltipText)
		self.w.minDistance.getNSTextField().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.textSpeed = vanilla.TextBox((inset, linePos + 2, 42, 14), u"Speed:", sizeStyle='small', selectable=True)
		self.w.popupSpeed = vanilla.PopUpButton(
			(inset + 42, linePos, 110, 17), ("very slow", "slow", "medium", "fast", "very fast"), callback=self.SavePreferences, sizeStyle='small'
			)
		intervalIndex = self.pref("popupSpeed")
		if intervalIndex is None:
			intervalIndex = 0
		self.w.text_speedExplanation = vanilla.TextBox((inset + 160, linePos + 2, -inset, 14), "Measuring every %i units." % intervalList[intervalIndex], sizeStyle='small')
		tooltipText = "The distances within every glyph pair will be measured from top to bottom. This setting determines how many measurements are taken. Higher speed means less measurements and thus less accuracy. Many measurements are more accurate, but also slow down the script significantly."
		self.w.textSpeed.getNSTextField().setToolTip_(tooltipText)
		self.w.popupSpeed.getNSPopUpButton().setToolTip_(tooltipText)
		self.w.text_speedExplanation.getNSTextField().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.text_popupLeftCat = vanilla.TextBox((inset, linePos + 2, 90, 14), "Left Category:", sizeStyle='small')
		self.w.popupLeftCat = vanilla.PopUpButton((inset + 90, linePos, -inset, 17), categoryList, callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "The category for the glyph on the LEFT side of the kerning pair. In ‘AV’, that would be ‘A’."
		self.w.text_popupLeftCat.getNSTextField().setToolTip_(tooltipText)
		self.w.popupLeftCat.getNSPopUpButton().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.text_popupRightCat = vanilla.TextBox((inset, linePos + 2, 90, 14), "Right Category:", sizeStyle='small')
		self.w.popupRightCat = vanilla.PopUpButton((inset + 90, linePos, -inset, 17), categoryList, callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "The category for the glyph on the RIGHT side of the kerning pair. In ‘AV’, that would be ‘V’."
		self.w.text_popupRightCat.getNSTextField().setToolTip_(tooltipText)
		self.w.popupRightCat.getNSPopUpButton().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.text_limitLeftSuffixes = vanilla.TextBox((inset, linePos + 2, 160, 14), "Left glyph must contain:", sizeStyle='small')
		self.w.limitLeftSuffixes = vanilla.EditText((inset + 150, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.limitLeftSuffixes.getNSTextField().setPlaceholderString_("tilde, macron, dieresis, circumflex, caron")
		tooltipText = "Only glyphs with these parts in their glyph names will be considered for the LEFT side. Comma-separated list. Usually not necessary, but useful for tracking down problems with wide diacritics."
		self.w.text_limitLeftSuffixes.getNSTextField().setToolTip_(tooltipText)
		self.w.limitLeftSuffixes.getNSTextField().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.text_limitRightSuffixes = vanilla.TextBox((inset, linePos + 2, 160, 14), "Right glyph must contain:", sizeStyle='small')
		self.w.limitRightSuffixes = vanilla.EditText((inset + 150, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.limitRightSuffixes.getNSTextField().setPlaceholderString_("tilde, macron, dieresis, circumflex, caron")
		tooltipText = "Only glyphs with these parts in their glyph names will be considered for the RIGHT side. Comma-separated list. Usually not necessary, but useful for tracking down problems with wide diacritics."
		self.w.text_limitRightSuffixes.getNSTextField().setToolTip_(tooltipText)
		self.w.limitRightSuffixes.getNSTextField().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.text_excludeSuffixes = vanilla.TextBox((inset, linePos + 2, 160, 14), "Exclude glyphs containing:", sizeStyle='small')
		self.w.excludeSuffixes = vanilla.EditText(
			(inset + 150, linePos, -inset, 19), ".locl, .alt, .sups, .sinf, .tf, .tosf, Ldot, ldot, Jacute, jacute", callback=self.SavePreferences, sizeStyle='small'
			)
		tooltipText = "Glyphs with these parts in their glyph names will be ignored. Comma-separated list. Useful for excluding impossible pairings, like ldot (can only appear before l) and jacute (can only appear after iacute), or OpenType variants."
		self.w.text_excludeSuffixes.getNSTextField().setToolTip_(tooltipText)
		self.w.excludeSuffixes.getNSTextField().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.text_ignoreIntervals = vanilla.TextBox((inset, linePos + 2, 160, 14), "Ignore height intervals:", sizeStyle='small')
		self.w.ignoreIntervals = vanilla.EditText((inset + 150, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreIntervals.getNSTextField().setPlaceholderString_("200:300, 400:370, -200:-150")
		tooltipText = "Will not measure between the specified heights. Useful for excluding connectors of connecting script typefaces or rekha lines like in Devanagari, where an overlap is intended by design. Specify two numbers separated by a colon, e.g., 200:300, and it will only measure until y=200 and start measuring again at y=300, skipping everything in between. If you specify multiple ranges, separate them with commas."
		self.w.text_ignoreIntervals.getNSTextField().setToolTip_(tooltipText)
		self.w.ignoreIntervals.getNSTextField().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.pathGlyphsOnly = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), u"Limit to glyphs containing paths (i.e., exclude composites)", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.pathGlyphsOnly.getNSButton().setToolTip_(
			"If enabled, will ignore glyphs that do not have paths. Useful for focusing on the base shapes (before you deal with the specific problems of composite diacritics)."
			)
		linePos += lineHeight

		self.w.excludeNonExporting = vanilla.CheckBox((inset, linePos, -inset, 20), "Exclude non-exporting glyphs", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.excludeNonExporting.getNSButton(
		).setToolTip_("If enabled, will ignore glyphs that are set to not export. Recommended, otherwise you may get a lot of false positives.")
		linePos += lineHeight

		self.w.directionSensitive = vanilla.CheckBox(
			(inset, linePos, -inset, 20), "Auto-detect writing direction (LTR vs. RTL)", value=True, sizeStyle='small', callback=self.SavePreferences
			)
		self.w.directionSensitive.getNSButton().setToolTip_("If enabled, will determine writing direction based on settings in current tab. If disabled, LTR will be used")
		linePos += lineHeight

		self.w.reportCrashesInMacroWindow = vanilla.CheckBox(
			(inset, linePos, -inset, 20), "Verbose report in Macro Window", value=False, sizeStyle='small', callback=self.SavePreferences
			)
		self.w.reportCrashesInMacroWindow.getNSButton().setToolTip_(
			"Will output a detailed report of the kern crashing in Window > Macro Panel. Will slow down the script a bit. Usually not necessary, but can be useful for checking if a certain pairing has been taken care of or not."
			)
		self.w.reuseCurrentTab = vanilla.CheckBox((inset + 240, linePos, -inset, 20), u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseCurrentTab.getNSButton(
		).setToolTip_("If enabled, will not open a new tab with newly added kern pairs, but reuse the current Edit tab. Will open an Edit tab if none is open.")
		linePos += lineHeight

		# Percentage:
		self.w.bar = vanilla.ProgressBar((inset, linePos, -inset, 16))

		#self.w.percentage = vanilla.TextBox( (15-1, -30, -100-15, -15), "", sizeStyle='small' )

		# Buttons:
		self.w.nextButton = vanilla.Button((-inset - 210, -20 - inset, -inset - 100, -inset), u"Next Master", sizeStyle='regular', callback=self.masterSwitch)

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.KernCrasherMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'KernCrasher' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		if sender == self.w.updateScriptsButton and Glyphs.font:
			scriptList = [g.script for g in Glyphs.font.glyphs if g.script]
			if scriptList:
				updatedScriptList = list(set(scriptList))
				self.w.popupScript.setItems(updatedScriptList)
				self.w.popupScript.set(updatedScriptList[0])
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
				
			# update speed explanation:
			if sender == self.w.popupSpeed:
				intervalIndex = self.pref("popupSpeed")
				if intervalIndex is None:
					intervalIndex = 0
				self.w.text_speedExplanation.set("Measuring every %i units." % intervalList[intervalIndex])
			
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set( self.pref(prefName) )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def nameUntilFirstPeriod(self, glyphName):
		if not "." in glyphName:
			return glyphName
		else:
			offset = glyphName.find(".")
			return glyphName[:offset]

	def listOfNamesForCategories(self, thisFont, requiredCategory, requiredSubCategory, requiredScript, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, mustContain):
		nameList = []
		for thisGlyph in thisFont.glyphs:
			thisScript = thisGlyph.script
			glyphName = thisGlyph.name
			nameIsOK = True

			if excludedGlyphNameParts:
				for thisNamePart in excludedGlyphNameParts:
					nameIsOK = nameIsOK and not thisNamePart in glyphName

			if mustContain:
				nameIsOK = False
				for thisNamePart in mustContain:
					if thisNamePart in glyphName:
						nameIsOK = True

			if nameIsOK and (thisGlyph.export or not excludeNonExporting):
				if thisScript == None or thisScript == requiredScript:
					if thisGlyph.category == requiredCategory:
						if requiredSubCategory:
							if Glyphs.versionNumber >= 3 and requiredSubCategory in caseDict:
								requiredCase = caseDict[requiredSubCategory]
								if thisGlyph.case == requiredCase:
									if (not pathGlyphsOnly) or thisGlyph.layers[0].paths:
										nameList.append(glyphName)
							else:
								if thisGlyph.subCategory == requiredSubCategory or (requiredSubCategory == "Other" and thisGlyph.subCategory is None):
									if (not pathGlyphsOnly) or thisGlyph.layers[0].paths:
										nameList.append(glyphName)
						else:
							if (not pathGlyphsOnly) or thisGlyph.layers[0].paths:
								nameList.append(glyphName)
		return nameList

	def masterSwitch(self, sender=None):
		if sender is self.w.nextButton:
			Glyphs.font.masterIndex += 1

	def splitString(self, string, delimiter=":", minimum=2):
		# split string into a list:
		returnList = string.split(delimiter)

		# remove trailing spaces:
		for i in range(len(returnList)):
			returnList[i] = returnList[i].strip()

		# if necessary fill up with None:
		while len(returnList) < minimum:
			returnList.append(None)

		if returnList == [""]:
			return None

		return returnList

	def measureLayerAtHeightFromLeftOrRight(self, thisLayer, height, leftSide=True):
		try:
			if leftSide:
				measurement = thisLayer.lsbAtHeight_(height)
			else:
				measurement = thisLayer.rsbAtHeight_(height)
			if measurement < NSNotFound:
				return measurement
			else:
				return None
		except Exception as e:
			raise e
			return None

	def isHeightInIntervals(self, height, ignoreIntervals):
		if ignoreIntervals:
			for interval in ignoreIntervals:
				if height <= interval[1] and height >= interval[0]:
					return True
		return False

	def minDistanceBetweenTwoLayers(self, leftLayer, rightLayer, interval=5.0, kerning=0.0, report=False, ignoreIntervals=[]):
		# correction = leftLayer.RSB+rightLayer.LSB
		if Glyphs.versionNumber>=3.2:
			leftBounds, rightBounds = leftLayer.fastBounds(), rightLayer.fastBounds()
		else:
			leftBounds, rightBounds = leftLayer.bounds, rightLayer.bounds
		topY = min(leftBounds.origin.y + leftBounds.size.height, rightBounds.origin.y + rightBounds.size.height)
		bottomY = max(leftLayer.bounds.origin.y, rightLayer.bounds.origin.y)
		distance = topY - bottomY
		minDist = None
		for i in range(int(distance / interval)):
			height = bottomY + i * interval
			if not self.isHeightInIntervals(height, ignoreIntervals) or not ignoreIntervals:
				left = leftLayer.rsbAtHeight_(height)
				right = rightLayer.lsbAtHeight_(height)
				if left < NSNotFound and right < NSNotFound: # avoid gaps like in i or j
					total = left + right + kerning # +correction
					if minDist == None or minDist > total:
						minDist = total
		return minDist

	def queryPrefs(self):
		script = self.pref("popupScript")
		firstCategory, firstSubCategory = self.splitString(self.w.popupLeftCat.getItems()[self.pref("popupLeftCat")])
		secondCategory, secondSubCategory = self.splitString(self.w.popupRightCat.getItems()[self.pref("popupRightCat")])
		return script, firstCategory, firstSubCategory, secondCategory, secondSubCategory

	def sortedIntervalsFromString(self, intervals=""):
		ignoreIntervals = []
		if intervals:
			for interval in intervals.split(","):
				if interval.find(":") != -1:
					interval = interval.strip()
					try:
						intervalTuple = tuple(sorted([
							int(interval.split(":")[0].strip()),
							int(interval.split(":")[1].strip()),
							]))
						ignoreIntervals.append(intervalTuple)
					except:
						print("Warning: could not convert '%s' into a number interval." % interval.strip())
						pass
				else:
					print("Warning: '%s' is not an interval (missing colon)" % interval.strip())

		return ignoreIntervals

	def KernCrasherMain(self, sender):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print("Note: 'KernCrasher' could not write preferences.")

			# query frontmost fontmaster:
			thisFont = Glyphs.font
			thisFontMaster = thisFont.selectedFontMaster
			thisFontMasterID = thisFontMaster.id

			# reset progress bar:
			self.w.bar.set(0)

			# start taking time:
			start = timer()

			# start reporting to macro window:
			if self.pref("reportCrashesInMacroWindow"):
				Glyphs.clearLog()
				print("KernCrasher Report for %s, master %s:\n" % (thisFont.familyName, thisFontMaster.name))

			# query user input:
			script, firstCategory, firstSubCategory, secondCategory, secondSubCategory = self.queryPrefs()
			step = intervalList[self.pref("popupSpeed")]
			excludedGlyphNameParts = self.splitString(self.pref("excludeSuffixes"), delimiter=",", minimum=0)
			excludeNonExporting = bool(self.pref("excludeNonExporting"))
			pathGlyphsOnly = bool(self.pref("pathGlyphsOnly"))
			limitRightSuffixes = self.splitString(self.pref("limitRightSuffixes"), delimiter=",", minimum=0)
			limitLeftSuffixes = self.splitString(self.pref("limitLeftSuffixes"), delimiter=",", minimum=0)
			minDistance = 0.0
			ignoreIntervals = self.sortedIntervalsFromString(self.pref("ignoreIntervals"))
			try:
				minDistance = float(self.pref("minDistance"))
			except Exception as e:
				print("Warning: Could not read min distance entry. Will default to 0.\n%s" % e)
				import traceback
				print(traceback.format_exc())
				print()

			# save prefs
			if not self.SavePreferences(None):
				print("Note: KernCrasher could not write preferences.")

			# get list of glyph names:
			firstList = self.listOfNamesForCategories(
				thisFont, firstCategory, firstSubCategory, script, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, limitLeftSuffixes
				)
			secondList = self.listOfNamesForCategories(
				thisFont, secondCategory, secondSubCategory, script, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, limitRightSuffixes
				)

			directionSensitive = False
			if self.w.directionSensitive.get() == 1:
				directionSensitive = True

			if not firstList or not secondList:
				Message(
					title="Error: could not find any pairs",
					message=
					"The criteria for glyph selection are too strict. With the current settings, there are %i glyphs for the left side in the current font, and %i glyphs for the right side."
					% (
						len(firstList),
						len(secondList),
						),
					OKButton=None,
					)

			if self.pref("reportCrashesInMacroWindow"):
				print("Minimum Distance: %i\n" % minDistance)
				print("Left glyphs:\n%s\n" % ", ".join(firstList))
				print("Right glyphs:\n%s\n" % ", ".join(secondList))

			tabString = "\n"
			crashCount = 0
			numOfGlyphs = len(firstList)
			for index in range(numOfGlyphs):
				# update progress bar:
				self.w.bar.set(int(100 * (float(index) / numOfGlyphs)))
				# determine left glyph:
				firstGlyphName = firstList[index]
				leftLayer = thisFont.glyphs[firstGlyphName].layers[thisFontMasterID].copyDecomposedLayer()
				leftLayer.decomposeSmartOutlines()

				# cycle through right glyphs:
				for secondGlyphName in secondList:
					rightLayer = thisFont.glyphs[secondGlyphName].layers[thisFontMasterID].copyDecomposedLayer()
					rightLayer.decomposeSmartOutlines()
					kerning = effectiveKerning(firstGlyphName, secondGlyphName, thisFont, thisFontMasterID, directionSensitive)
					distanceBetweenShapes = self.minDistanceBetweenTwoLayers(leftLayer, rightLayer, interval=step, kerning=kerning, report=False, ignoreIntervals=ignoreIntervals)
					if (not distanceBetweenShapes is None) and (distanceBetweenShapes < minDistance):
						crashCount += 1
						tabString += "/%s/%s/space" % (firstGlyphName, secondGlyphName)
						if self.pref("reportCrashesInMacroWindow"):
							print("- %s %s: %i" % (firstGlyphName, secondGlyphName, distanceBetweenShapes))
				tabString += "\n"

			# clean up the tab string:
			tabString = tabString[:-6].replace("/space\n", "\n")
			while "\n\n" in tabString:
				tabString = tabString.replace("\n\n", "\n")
			tabString = tabString[1:]

			# update progress bar:
			self.w.bar.set(100)

			# take time:
			end = timer()
			seconds = end - start
			if seconds > 60.0:
				timereport = "%i:%02i minutes" % (seconds // 60, seconds % 60)
			elif seconds < 1.0:
				timereport = "%.2f seconds" % seconds
			elif seconds < 20.0:
				timereport = "%.1f seconds" % seconds
			else:
				timereport = "%i seconds" % seconds

			# open new Edit tab:
			if tabString:
				if len(tabString) > 40:
					# disable reporters (avoid slowdown)
					Glyphs.defaults["visibleReporters"] = None
				report = '%i kerning crashes have been found. Time elapsed: %s.' % (crashCount, timereport)
				if self.pref("reuseCurrentTab") and thisFont.currentTab:
					thisFont.currentTab.text = tabString
				else:
					thisFont.newTab(tabString)
			# or report that nothing was found:
			else:
				report = 'No collisions found. Time elapsed: %s. Congrats!' % timereport

			# Notification:
			notificationTitle = "KernCrasher: %s (%s)" % (thisFont.familyName, thisFontMaster.name)
			Glyphs.showNotification(notificationTitle, report)

			# Report in Macro Window:
			if self.pref("reportCrashesInMacroWindow"):
				print(report)
				Glyphs.showMacroWindow()

		except Exception as e:
			print("KernCrasher Error: %s" % e)
			import traceback
			print(traceback.format_exc())

KernCrasher()
