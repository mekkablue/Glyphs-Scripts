#MenuTitle: GapFinder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Opens a new tab with kerning combos that have large gaps in the current fontmaster.
"""

import vanilla
from timeit import default_timer as timer
from Foundation import NSNotFound
intervalList = (1, 3, 5, 10, 20)
categoryList = (
	"Letter:Uppercase",
	"Letter:Lowercase",
	"Letter:Smallcaps",
	"Punctuation",
	"Symbol:Currency",
	"Symbol:Math",
	"Symbol:Other",
	"Symbol:Arrow",
	"Number:Decimal Digit",
	"Number:Small",
	"Number:Fraction",
	)

if Glyphs.versionNumber >= 3:
	caseDict = {
		"Uppercase": GSUppercase,
		"Lowercase": GSLowercase,
		"Smallcaps": GSSmallcaps,
		}

class GapFinder(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 410
		windowHeight = 260
		windowWidthResize = 800 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"GapFinder", # window title
			minSize=(windowWidth, windowHeight), # Maximum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.GapFinder.mainwindow" # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), u"Open tab with kern gaps in current master:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.textScript = vanilla.TextBox((inset, linePos + 2, 42, 14), u"Script:", sizeStyle='small', selectable=True)
		self.w.popupScript = vanilla.ComboBox((inset + 42, linePos - 1, 110, 18), ("latin", "cyrillic", "greek"), callback=self.SavePreferences, sizeStyle='small')
		self.w.textDistance = vanilla.TextBox((inset + 160, linePos + 2, 100, 14), "Max distance:", sizeStyle='small')
		self.w.maxDistance = vanilla.EditText((inset + 240, linePos - 1, -15, 19), "200", sizeStyle='small')
		linePos += lineHeight

		self.w.textSpeed = vanilla.TextBox((inset, linePos + 2, 42, 14), u"Speed:", sizeStyle='small', selectable=True)
		self.w.popupSpeed = vanilla.PopUpButton(
			(inset + 42, linePos, 110, 17), ("very slow", "slow", "medium", "fast", "very fast"), callback=self.SavePreferences, sizeStyle='small'
			)
		intervalIndex = Glyphs.defaults["com.mekkablue.GapFinder.popupSpeed"]
		if intervalIndex is None:
			intervalIndex = 0
		self.w.text_speedExplanation = vanilla.TextBox((inset + 160, linePos + 2, -inset, 14), "Measuring every %i units." % intervalList[intervalIndex], sizeStyle='small')
		linePos += lineHeight

		self.w.text_3 = vanilla.TextBox((inset, linePos + 2, 90, 14), "Left Category:", sizeStyle='small')
		self.w.popupLeftCat = vanilla.PopUpButton((inset + 90, linePos, -inset, 17), categoryList, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.text_4 = vanilla.TextBox((inset, linePos + 2, 90, 14), "Right Category:", sizeStyle='small')
		self.w.popupRightCat = vanilla.PopUpButton((inset + 90, linePos, -inset, 17), categoryList, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.text_5 = vanilla.TextBox((inset, linePos + 2, 160, 14), "Exclude glyphs containing:", sizeStyle='small')
		self.w.excludeSuffixes = vanilla.EditText(
			(inset + 150, linePos, -inset, 19), ".locl, .alt, .sups, .sinf, .tf, .tosf, Ldot, ldot, Jacute, jacute", callback=self.SavePreferences, sizeStyle='small'
			)
		linePos += lineHeight

		self.w.excludeNonExporting = vanilla.CheckBox((inset, linePos, -inset, 20), "Exclude non-exporting glyphs", value=True, sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.reportGapsInMacroWindow = vanilla.CheckBox(
			(inset, linePos, -inset, 20), "Also report in Macro Window (slower)", value=False, sizeStyle='small', callback=self.SavePreferences
			)
		self.w.reuseCurrentTab = vanilla.CheckBox((inset + 240, linePos, -inset, 20), u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseCurrentTab.getNSButton(
		).setToolTip_(u"If enabled, will not open a new tab with newly added kern pairs, but reuse the current Edit tab. Will open an Edit tab if none is open.")
		linePos += lineHeight

		# Percentage:
		self.w.bar = vanilla.ProgressBar((inset, linePos, -inset, 16))

		#self.w.percentage = vanilla.TextBox( (15-1, -30, -100-15, -15), "", sizeStyle='small' )

		# Buttons:
		self.w.nextButton = vanilla.Button((-inset - 210, -20 - inset, -inset - 100, -inset), u"Next Master", sizeStyle='regular', callback=self.masterSwitch)

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.GapFinderMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'GapFinder' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults["com.mekkablue.GapFinder.popupScript"] = self.w.popupScript.get()
			Glyphs.defaults["com.mekkablue.GapFinder.popupSpeed"] = self.w.popupSpeed.get()
			Glyphs.defaults["com.mekkablue.GapFinder.popupLeftCat"] = self.w.popupLeftCat.get()
			Glyphs.defaults["com.mekkablue.GapFinder.popupRightCat"] = self.w.popupRightCat.get()
			Glyphs.defaults["com.mekkablue.GapFinder.excludeSuffixes"] = self.w.excludeSuffixes.get()
			Glyphs.defaults["com.mekkablue.GapFinder.excludeNonExporting"] = self.w.excludeNonExporting.get()
			Glyphs.defaults["com.mekkablue.GapFinder.maxDistance"] = self.w.maxDistance.get()
			Glyphs.defaults["com.mekkablue.GapFinder.reportGapsInMacroWindow"] = self.w.reportGapsInMacroWindow.get()
			Glyphs.defaults["com.mekkablue.GapFinder.reuseCurrentTab"] = self.w.reuseCurrentTab.get()
		except Exception as e:
			return False

		# update speed explanation:
		if sender == self.w.popupSpeed:
			intervalIndex = Glyphs.defaults["com.mekkablue.GapFinder.popupSpeed"]
			if intervalIndex is None:
				intervalIndex = 0
			self.w.text_speedExplanation.set("Measuring every %i units." % intervalList[intervalIndex])

		return True

	def LoadPreferences(self):
		try:
			Glyphs.registerDefault("com.mekkablue.GapFinder.maxDistance", "200")
			Glyphs.registerDefault("com.mekkablue.GapFinder.popupScript", "latin")
			Glyphs.registerDefault("com.mekkablue.GapFinder.popupSpeed", 0)
			Glyphs.registerDefault("com.mekkablue.GapFinder.popupLeftCat", 0)
			Glyphs.registerDefault("com.mekkablue.GapFinder.popupRightCat", 0)
			Glyphs.registerDefault("com.mekkablue.GapFinder.excludeSuffixes", ".locl, .alt, .sups, .sinf, .tf, .tosf, Ldot, ldot, Jacute, jacute")
			Glyphs.registerDefault("com.mekkablue.GapFinder.excludeNonExporting", 1)
			Glyphs.registerDefault("com.mekkablue.GapFinder.reportGapsInMacroWindow", 0)
			Glyphs.registerDefault("com.mekkablue.GapFinder.reuseCurrentTab", 1)

			self.w.maxDistance.set(Glyphs.defaults["com.mekkablue.GapFinder.maxDistance"])
			self.w.popupScript.set(Glyphs.defaults["com.mekkablue.GapFinder.popupScript"])
			self.w.popupSpeed.set(Glyphs.defaults["com.mekkablue.GapFinder.popupSpeed"])
			self.w.popupLeftCat.set(Glyphs.defaults["com.mekkablue.GapFinder.popupLeftCat"])
			self.w.popupRightCat.set(Glyphs.defaults["com.mekkablue.GapFinder.popupRightCat"])
			self.w.excludeSuffixes.set(Glyphs.defaults["com.mekkablue.GapFinder.excludeSuffixes"])
			self.w.excludeNonExporting.set(Glyphs.defaults["com.mekkablue.GapFinder.excludeNonExporting"])
			self.w.reportGapsInMacroWindow.set(Glyphs.defaults["com.mekkablue.GapFinder.reportGapsInMacroWindow"])
			self.w.reuseCurrentTab.set(Glyphs.defaults["com.mekkablue.GapFinder.reuseCurrentTab"])
		except:
			return False

		return True

	def masterSwitch(self, sender=None):
		if sender is self.w.nextButton:
			Glyphs.font.masterIndex += 1

	def nameUntilFirstPeriod(self, glyphName):
		if not "." in glyphName:
			return glyphName
		else:
			offset = glyphName.find(".")
			return glyphName[:offset]

	def effectiveKerning(self, leftGlyphName, rightGlyphName, thisFont, thisFontMasterID):
		leftLayer = thisFont.glyphs[leftGlyphName].layers[thisFontMasterID]
		rightLayer = thisFont.glyphs[rightGlyphName].layers[thisFontMasterID]
		if Glyphs.versionNumber >= 3:
			effectiveKerning = leftLayer.nextKerningForLayer_direction_(
				rightLayer,
				0 # LTR
				)
		else:
			effectiveKerning = leftLayer.rightKerningForLayer_(rightLayer)
		if effectiveKerning < NSNotFound:
			return effectiveKerning
		else:
			return 0.0

	def listOfNamesForCategories(self, thisFont, requiredCategory, requiredSubCategory, requiredScript, excludedGlyphNameParts, excludeNonExporting):
		nameList = []
		for thisGlyph in thisFont.glyphs:
			thisScript = thisGlyph.script
			glyphName = thisGlyph.name
			nameIsOK = True

			if excludedGlyphNameParts:
				for thisNamePart in excludedGlyphNameParts:
					nameIsOK = nameIsOK and not thisNamePart in glyphName

			if nameIsOK and (thisGlyph.export or not excludeNonExporting):
				if thisScript == None or thisScript == requiredScript:
					if thisGlyph.category == requiredCategory:
						if requiredSubCategory:
							if Glyphs.versionNumber >= 3 and requiredSubCategory in caseDict:
								requiredCase = caseDict[requiredSubCategory]
								if thisGlyph.case == requiredCase:
									nameList.append(glyphName)
							else:
								if thisGlyph.subCategory == requiredSubCategory:
									nameList.append(glyphName)
						else:
							nameList.append(glyphName)
		return nameList

	def splitString(self, string, delimiter=":", Maximum=2):
		# split string into a list:
		returnList = string.split(delimiter)

		# remove trailing spaces:
		for i in range(len(returnList)):
			returnList[i] = returnList[i].strip()

		# if necessary fill up with None:
		while len(returnList) < Maximum:
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
		except:
			return None

	def minDistanceBetweenTwoLayers(self, leftLayer, rightLayer, interval=5.0, kerning=0.0, report=False):
		# correction = leftLayer.RSB+rightLayer.LSB
		topY = min(leftLayer.bounds.origin.y + leftLayer.bounds.size.height, rightLayer.bounds.origin.y + rightLayer.bounds.size.height)
		bottomY = max(leftLayer.bounds.origin.y, rightLayer.bounds.origin.y)
		distance = topY - bottomY
		minDist = None
		for i in range(int(distance // interval)):
			height = bottomY + i * interval
			left = self.measureLayerAtHeightFromLeftOrRight(leftLayer, height, leftSide=False)
			right = self.measureLayerAtHeightFromLeftOrRight(rightLayer, height, leftSide=True)
			try: # avoid gaps like in i or j
				total = left + right + kerning # +correction
				if minDist == None or minDist > total:
					minDist = total
			except:
				pass
		return minDist

	def queryPrefs(self):
		script = Glyphs.defaults["com.mekkablue.GapFinder.popupScript"]
		firstCategory, firstSubCategory = self.splitString(self.w.popupLeftCat.getItems()[Glyphs.defaults["com.mekkablue.GapFinder.popupLeftCat"]])
		secondCategory, secondSubCategory = self.splitString(self.w.popupRightCat.getItems()[Glyphs.defaults["com.mekkablue.GapFinder.popupRightCat"]])
		return script, firstCategory, firstSubCategory, secondCategory, secondSubCategory

	def GapFinderMain(self, sender):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print("Note: 'GapFinder' could not write preferences.")

			# query frontmost fontmaster:
			thisFont = Glyphs.font
			thisFontMaster = thisFont.selectedFontMaster
			thisFontMasterID = thisFontMaster.id

			# reset progress bar:
			self.w.bar.set(0)

			# start taking time:
			start = timer()

			# start reporting to macro window:
			if Glyphs.defaults["com.mekkablue.GapFinder.reportGapsInMacroWindow"]:
				Glyphs.clearLog()
				print("GapFinder Report for %s, master %s:\n" % (thisFont.familyName, thisFontMaster.name))

			# query user input:
			script, firstCategory, firstSubCategory, secondCategory, secondSubCategory = self.queryPrefs()
			step = intervalList[Glyphs.defaults["com.mekkablue.GapFinder.popupSpeed"]]
			excludedGlyphNameParts = self.splitString(Glyphs.defaults["com.mekkablue.GapFinder.excludeSuffixes"], delimiter=",", Maximum=0)
			excludeNonExporting = bool(Glyphs.defaults["com.mekkablue.GapFinder.excludeNonExporting"])
			maxDistance = 200.0 # default
			try:
				maxDistance = float(Glyphs.defaults["com.mekkablue.GapFinder.maxDistance"])
			except Exception as e:
				print("Warning: Could not read min distance entry. Will default to 200.\n%s" % e)
				import traceback
				print(traceback.format_exc())
				print()

			# save prefs
			if not self.SavePreferences(None):
				print("Note: GapFinder could not write preferences.")

			# get list of glyph names:
			firstList = self.listOfNamesForCategories(thisFont, firstCategory, firstSubCategory, script, excludedGlyphNameParts, excludeNonExporting)
			secondList = self.listOfNamesForCategories(thisFont, secondCategory, secondSubCategory, script, excludedGlyphNameParts, excludeNonExporting)

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

			if Glyphs.defaults["com.mekkablue.GapFinder.reportGapsInMacroWindow"]:
				print("Maximum Distance: %i\n" % maxDistance)
				print("Left glyphs:\n%s\n" % ", ".join(firstList))
				print("Right glyphs:\n%s\n" % ", ".join(secondList))

			tabString = "\n"
			gapCount = 0
			numOfGlyphs = len(firstList)
			for index in range(numOfGlyphs):
				# update progress bar:
				self.w.bar.set(int(100 * (float(index) / numOfGlyphs)))
				# determine left glyph:
				firstGlyphName = firstList[index]
				leftLayer = thisFont.glyphs[firstGlyphName].layers[thisFontMasterID]

				# cycle through right glyphs:
				for secondGlyphName in secondList:
					rightLayer = thisFont.glyphs[secondGlyphName].layers[thisFontMasterID]
					kerning = self.effectiveKerning(firstGlyphName, secondGlyphName, thisFont, thisFontMasterID)
					distanceBetweenShapes = self.minDistanceBetweenTwoLayers(leftLayer, rightLayer, interval=step, kerning=kerning, report=False)
					if (not distanceBetweenShapes is None) and (distanceBetweenShapes > maxDistance):
						gapCount += 1
						tabString += "/%s/%s/space" % (firstGlyphName, secondGlyphName)
						if Glyphs.defaults["com.mekkablue.GapFinder.reportGapsInMacroWindow"]:
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
				report = '%i kerning gaps have been found. Time elapsed: %s.' % (gapCount, timereport)
				if Glyphs.defaults["com.mekkablue.GapFinder.reuseCurrentTab"] and thisFont.currentTab:
					thisFont.currentTab.text = tabString
				else:
					thisFont.newTab(tabString)
			# or report that nothing was found:
			else:
				report = 'No gaps found. Time elapsed: %s. Congrats!' % timereport

			# Notification:
			notificationTitle = "GapFinder: %s (%s)" % (thisFont.familyName, thisFontMaster.name)
			Glyphs.showNotification(notificationTitle, report)

			# Report in Macro Window:
			if Glyphs.defaults["com.mekkablue.GapFinder.reportGapsInMacroWindow"]:
				print(report)
				Glyphs.showMacroWindow()

		except Exception as e:
			print("GapFinder Error: %s" % e)
			import traceback
			print(traceback.format_exc())

GapFinder()
