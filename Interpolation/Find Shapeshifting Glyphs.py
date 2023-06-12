#MenuTitle: Find Shapeshifting Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds glyphs that change the number of visible shapes and countershapes while interpolating, so-called ‘shapeshifters’. Often unintended. Opens a new tab and reports to Macro Window.
"""

import vanilla
tempMarker = "###DELETEME###"

def instanceIsActive(instance):
	if Glyphs.buildNumber>3198:
		return instance.exports
	else:
		return instance.active

def glyphInterpolation(thisGlyphName, thisInstance):
	"""
	Yields a layer.
	"""
	try:
		# calculate interpolation:
		# interpolatedFont = thisInstance.interpolatedFont # too slow still
		interpolatedFont = thisInstance.pyobjc_instanceMethods.interpolatedFont()
		interpolatedLayer = interpolatedFont.glyphForName_(thisGlyphName).layers[0]

		# if interpolatedLayer.components:
		# 	interpolatedLayer.decomposeComponents()

		# round to grid if necessary:
		if interpolatedLayer.paths:
			if interpolatedFont.gridLength == 1.0:
				interpolatedLayer.roundCoordinates()
			return interpolatedLayer
		else:
			return interpolatedLayer

	except:
		import traceback
		print(traceback.format_exc())
		return None

class FindShapeshiftingGlyphs(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 310
		windowHeight = 270
		windowWidthResize = 300 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Find Shapeshifting Glyphs", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.FindShapeshiftingGlyphs.mainwindow" # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox(
			(inset, linePos + 2, -inset, 28), "Reports glyphs that change number of cw/ccw paths (‘shapeshift’) in interpolation.", sizeStyle='small', selectable=True
			)
		linePos += int(lineHeight * 1.7)

		self.w.text_1 = vanilla.TextBox((inset, linePos + 2, 85, 14), "Count paths in", sizeStyle='small')
		self.w.checkInstances = vanilla.PopUpButton(
			(inset + 85, linePos, -inset, 17), ("constructed instances midway between masters", "all active instances in font", "all active and inactive instances in font"),
			callback=self.SavePreferences,
			sizeStyle='small'
			)
		self.w.checkInstances.getNSPopUpButton().setToolTip_(
			"Where to count paths (for comparison of path counts). Shapeshifting is most visible in midway interpolations (50%% between masters), so pick that option if you have two masters only, or all masters on a single axis."
			)
		linePos += lineHeight

		self.w.onlyCheckSelection = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Limit to selected glyphs (otherwise all glyphs)", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		linePos += lineHeight

		self.w.ignoreGlyphsWithoutPaths = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Ignore glyphs without paths", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		linePos += lineHeight

		self.w.ignoreNonexportingGlyphs = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Ignore glyphs that do not export", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		linePos += lineHeight

		self.w.openTab = vanilla.CheckBox((inset, linePos - 1, 170, 20), "Open tab with shapeshifters", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab = vanilla.CheckBox((inset + 170, linePos - 1, -inset, 20), "Reuse current tab", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "⚠️ Process ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allFonts.getNSButton().setToolTip_("If enabled, will process all fonts currently opened. Careful, may take a while.")
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Find", sizeStyle='regular', callback=self.FindShapeshiftingGlyphsMain)
		self.w.setDefaultButton(self.w.runButton)

		self.w.status = vanilla.TextBox((inset, -17 - inset, -90 - inset, 14), "", sizeStyle='small', selectable=False)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Find Shapeshifting Glyphs' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.checkInstances"] = self.w.checkInstances.get()
			# Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.alsoCheckMasters"] = self.w.alsoCheckMasters.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.onlyCheckSelection"] = self.w.onlyCheckSelection.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreGlyphsWithoutPaths"] = self.w.ignoreGlyphsWithoutPaths.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreNonexportingGlyphs"] = self.w.ignoreNonexportingGlyphs.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.openTab"] = self.w.openTab.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.reuseTab"] = self.w.reuseTab.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.allFonts"] = self.w.allFonts.get()
		except:
			return False

		return True

	def LoadPreferences(self):
		try:
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.checkInstances", 0)

			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.onlyCheckSelection", 0)
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.ignoreGlyphsWithoutPaths", 0)
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.ignoreNonexportingGlyphs", 0)
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.openTab", 0)
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.reuseTab", 0)
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.allFonts", 0)
			self.w.checkInstances.set(Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.checkInstances"])
			self.w.onlyCheckSelection.set(Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.onlyCheckSelection"])
			self.w.ignoreGlyphsWithoutPaths.set(Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreGlyphsWithoutPaths"])
			self.w.ignoreNonexportingGlyphs.set(Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreNonexportingGlyphs"])
			self.w.openTab.set(Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.openTab"])
			self.w.reuseTab.set(Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.reuseTab"])
			self.w.allFonts.set(Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.allFonts"])
		except:
			return False

		return True

	def generateTestInstance(self, thisFont, indexMasterDict):
		numOfMasters = len(indexMasterDict)
		significance = 1.0 / numOfMasters
		interpolationDict = {}
		sortedIndexes = sorted(indexMasterDict.keys())
		for i in sortedIndexes:
			master = indexMasterDict[i]
			interpolationDict[master.id] = significance

		testInstance = GSInstance()
		testInstance.active = False
		testInstance.name = "%s-%s" % ("-".join([str(i) for i in sortedIndexes]), tempMarker)
		testInstance.setManualInterpolation_(1)
		testInstance.setInstanceInterpolations_(interpolationDict)

		disabledMasters = []
		for m in range(len(thisFont.masters)):
			if not m in sortedIndexes:
				disabledMasters.append(thisFont.masters[m].name)
		if disabledMasters:
			disabledMasters = tuple(disabledMasters)
			testInstance.customParameters["Disable Masters"] = disabledMasters

		testInstance.setFont_(thisFont)
		return testInstance

	def addMasterInstances(self, thisFont, keepExisting=False):
		for i, master in enumerate(thisFont.masters):
			testInstance = self.generateTestInstance(thisFont, {i: master})
			self.instances.append(testInstance)

	def addHalfWayInstances(self, thisFont, keepExisting=False):
		numOfMasters = len(thisFont.masters)
		r = range(numOfMasters)
		for i in r[:-1]:
			for j in r[i + 1:]:
				master1 = thisFont.masters[i]
				master2 = thisFont.masters[j]
				testInstance = self.generateTestInstance(thisFont, {
					i: master1,
					j: master2
					})
				self.instances.append(testInstance)

	def FindShapeshiftingGlyphsMain(self, sender):
		try:
			# query settings:
			checkInstances = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.checkInstances"]
			onlyCheckSelection = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.onlyCheckSelection"]
			ignoreGlyphsWithoutPaths = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreGlyphsWithoutPaths"]
			ignoreNonexportingGlyphs = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreNonexportingGlyphs"]
			openTab = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.openTab"]
			reuseTab = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.reuseTab"]
			allFonts = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.allFonts"]

			# Clear macro window log:
			Glyphs.clearLog()
			if not openTab:
				# brings macro window to front:
				Glyphs.showMacroWindow()
			self.w.status.set("")

			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			alsoCheckMasters = False
			totalAffectedGlyphCount = 0
			totalAffectedFontCount = 0
			oneFontPercentage = 100.0 / len(theseFonts)

			for fontIndex, thisFont in enumerate(theseFonts):
				print("🦋 Find Shapeshifters in %s" % thisFont.familyName)
				try:
					fileName = thisFont.filepath.lastPathComponent()
				except:
					fileName = "⚠️ %s (unsaved)" % thisFont.familyName
				print("📄 %s" % fileName)
				self.w.status.set("Examining %s..." % fileName)

				# determine glyphs to be checked:
				if onlyCheckSelection:
					glyphs = [l.glyph() for l in thisFont.selectedLayers if l.glyph()]
				else:
					glyphs = thisFont.glyphs
				glyphNamesToBeChecked = [g.name for g in glyphs if (g.export or not ignoreNonexportingGlyphs) and (len(g.layers[0].paths) > 0 or not ignoreGlyphsWithoutPaths)]
				print("🔠 Checking %i glyph%s:\n%s\n" % (
					len(glyphNamesToBeChecked),
					"" if len(glyphNamesToBeChecked) == 1 else "s",
					", ".join(glyphNamesToBeChecked),
					))

				# determine the instances to calculate:
				self.instances = []
				# 0: constructed midway instances
				if checkInstances == 0:
					alsoCheckMasters = True
					self.addHalfWayInstances(thisFont)
				# 1: all active instances in font
				elif checkInstances == 1:
					self.instances = [i for i in thisFont.instances if instanceIsActive(i)]
				# 2: all active and inactive instances in font
				else:
					self.instances = thisFont.instances
				# add masters as instances if required:
				if alsoCheckMasters:
					self.addMasterInstances(thisFont)
				# report:
				print("Calculating %i instance interpolations:" % len(self.instances))
				for i in self.instances:
					print("\n🅸 %s:" % i.name)
					for key in i.instanceInterpolations.keys():
						# print(i.instanceInterpolations[key]) #DEBUG
						try:
							print("   🅜 %.3f %s" % (
								float(i.instanceInterpolations[key]),
								thisFont.masters[key].name,
								))
						except:
							pass

				print("\n\nFinding potential shapeshifters...\n")

				# iterate through glyphs:
				affectedGlyphNames = []
				numOfGlyphs = len(glyphNamesToBeChecked)
				for i, thisGlyphName in enumerate(glyphNamesToBeChecked):
					# tick the progress bar:
					self.w.progress.set(oneFontPercentage * fontIndex + int(oneFontPercentage * (float(i) / numOfGlyphs)))

					# collect number of paths for every instance:
					pathCounts = []
					for thisInstance in self.instances:
						interpolation = glyphInterpolation(thisGlyphName, thisInstance)
						if interpolation:
							# only decompose and remove overlap when necessary, should speed things up:
							if interpolation.components:
								interpolation.decomposeComponents()
							if len(interpolation.paths) > 1:
								interpolation.removeOverlap()
							countOfCWPaths = len([p for p in interpolation.paths if p.direction == 1])
							countOfCCWPaths = len(interpolation.paths) - countOfCWPaths
							pathCounts.append((countOfCWPaths, countOfCCWPaths), )
						else:
							print("❌ ERROR: %s has no interpolation for '%s'." % (thisGlyphName, thisInstance.name))

					# see if path counts changed:
					pathCounts = set(pathCounts)
					if len(pathCounts) > 1:
						sortedPathCounts = ["%i⟳+%i⟲" % (pair[0], pair[1]) for pair in sorted(pathCounts, key=lambda count: count[0])]
						print("⚠️ %s: changing between %s paths." % (thisGlyphName, ", ".join(sortedPathCounts)))
						affectedGlyphNames.append(thisGlyphName)

				# report:
				if affectedGlyphNames:
					totalAffectedGlyphCount += len(affectedGlyphNames)
					totalAffectedFontCount += 1
					if openTab:
						tabString = "/" + "/".join(affectedGlyphNames)
						if not thisFont.currentTab or not reuseTab:
							thisFont.newTab(tabString)
						else:
							thisFont.currentTab.text = tabString

				print("\n\n\n")

			message = ""

			if totalAffectedGlyphCount:
				message = "Found %i affected glyph%s in %i font%s (out of %i font%s examined)." % (
					totalAffectedGlyphCount,
					"" if totalAffectedGlyphCount == 1 else "s",
					totalAffectedFontCount,
					"" if totalAffectedFontCount == 1 else "s",
					len(theseFonts),
					"" if len(theseFonts) == 1 else "s",
					)
				Message(
					title="⚠️ %i Shapeshifting Glyphs" % totalAffectedGlyphCount,
					message="%s Details in Macro Window." % message,
					OKButton="OK",
					)
			else:
				message = "Among the specified fonts, glyphs and interpolations, no changes of path numbers could be found."
				Message(
					title="✅ No Shapeshifting Glyphs",
					message=message,
					OKButton="🍻Cheers!",
					)

			print("%s\nDone." % message)

			if not self.SavePreferences(self):
				print("Note: 'Find Shapeshifting Glyphs' could not write preferences.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Find Shapeshifting Glyphs Error: %s" % e)
			import traceback
			print(traceback.format_exc())

FindShapeshiftingGlyphs()
