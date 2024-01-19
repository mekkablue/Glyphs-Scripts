# MenuTitle: Instance Cooker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Insert many instances at once with a recipe.
"""

import vanilla
import codecs
from AppKit import NSFont, NSDictionary
from GlyphsApp import Glyphs, GSAxis, GSInstance, INSTANCETYPEVARIABLE, GetSaveFile, GetOpenFile, Message
from mekkablue import mekkaObject

defaultRecipe = """
Recipe instructions:
1. After a hashtag, enter the axis name (optionally followed by colon and axis tag), e.g. ‘#Weight’ or ‘#Width:wdth’
2. Per line, enter an axis value, followed by a colon, followed by the name particle for the axis position, e.g. ‘75:Condensed’ or ‘190:Extrabold’
3. Mark elidable name particles with an asterisk after the name, e.g. ‘Regular*’
4. If you need to differentiate between internal and external coordinates, write them with a greater sign: internal>external, e.g. ‘115>500:Medium’
5. Write a width class after a vertical bar, e.g. ‘75|3:Condensed’. The weight class will be derived from the external coordinate.
6. Use whitespace and empty lines as you like, write comments before the first hashtag.

#Width:wdth
75|3:Condensed
100|5:Regular*
150|7:Extended

#Weight:wght
30>100:Thin
50>200:Extralight
70>300:Light
85>400:Regular*
105>500:Medium
120>600:Semibold
145>700:Bold
175>800:Extrabold
190>900:Black

#Italic:ital
0:Regular*
1:Italic
"""


def saveFileInLocation(content="", filePath="~/Desktop/test.txt"):
	with codecs.open(filePath, "w", "utf-8-sig") as thisFile:
		print("💾 Writing:", thisFile.name)
		thisFile.write(content)
		thisFile.close()
	return True


def readFileFromLocation(filePath="~/Desktop/test.txt"):
	content = ""
	with codecs.open(filePath, "r", "utf-8-sig") as thisFile:
		print("💾 Reading:", thisFile.name)
		content = thisFile.read()
		thisFile.close()
	return content


def tagForAxisName(axisName):
	tagDict = {
		"Weight": "wght",
		"Width": "wdth",
		"Italic": "ital",
		"Slant": "slnt",
		"Optical Size": "opsz",
	}

	if tagDict[axisName]:
		return tagDict[axisName]
	else:
		tag = ""
		for letter in axisName.upper():
			if letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
				tag += letter
		if len(tag) < 4:
			tag = tag + (4 - len(tag)) * "X"
		return tag


def axisLocationEntry(axisName, locationValue):
	return NSDictionary.alloc().initWithObjects_forKeys_((axisName, locationValue), ("Axis", "Location"))


def parseAxes(code):
	axisDict = {}
	axisKey = None
	axisIndex = 0
	for thisLine in code.splitlines():
		if thisLine:
			if thisLine[0] == "#":
				# new axis
				if ":" in thisLine:
					axisName, axisTag = thisLine[1:].strip().split(":")
					axisName, axisTag = axisName.strip(), axisTag.strip()
				else:
					axisName = thisLine[1:].strip()
					axisTag = ""
				if not axisTag:
					tagForAxisName(axisName)
				axisKey = "%03i,%s:%s" % (axisIndex, axisName, axisTag)
				axisDict[axisKey] = []
				axisIndex += 1
			elif axisKey:
				# new axis position
				if ":" in thisLine:
					lineParts = thisLine.split(":")
					nameParticle = lineParts[1].strip()
					axisPosition = lineParts[0].strip()
					axisValue = None

					widthClass = None
					if "|" in axisPosition:
						axisPosition, widthClass = [x.strip() for x in axisPosition.split("|")[:2]]
						widthClass = int(widthClass)

					if ">" in axisPosition:
						positions = tuple([int(x.strip()) for x in axisPosition.split(">")][:2])
						axisValue = (positions, nameParticle, widthClass)
					else:
						position = int(axisPosition)
						axisValue = (position, nameParticle, widthClass)
					if axisValue:
						axisDict[axisKey].append(axisValue)
	return axisDict


def parsePosInfo(posInfo):
	if isinstance(posInfo, tuple):
		return posInfo

	posInfo = str(posInfo)
	if ">" in posInfo:
		coord, axisLoc = [int(c.strip()) for c in posInfo.split(">")]
	else:
		coord = int(posInfo.strip())
		axisLoc = coord
	return coord, axisLoc


def addLocationToInstance(instance, axisName, axisLoc):
	paramName = "Axis Location"
	entry = axisLocationEntry(axisName, axisLoc)

	existingLocations = []
	if instance.customParameters[paramName]:
		existingLocations = list(instance.customParameters[paramName])

	existingLocations.append(entry)
	instance.customParameters["Axis Location"] = tuple(existingLocations)

	if axisName == "Weight":
		instance.weightClass = axisLoc


def styleLinkInstance(instance, axisName, particle):
	linkedParticles = []
	for existingNameParticle in instance.name.split():
		if "*" not in existingNameParticle:
			if not existingNameParticle == particle:
				linkedParticles.append(existingNameParticle)
	linkedStyleName = " ".join(linkedParticles)
	if not linkedStyleName:
		linkedStyleName = "Regular"

	if axisName == "Weight" and particle == "Bold":
		instance.isBold = True
		instance.linkStyle = linkedStyleName
	elif axisName == "Italic" and particle == axisName:
		instance.isItalic = True
		if not instance.linkStyle:
			instance.linkStyle = linkedStyleName


def removeElidableNames(instance):
	if "*" in instance.name:
		particles = instance.name.split()
		elidableName = ""
		newParticles = []

		# collect non-elidable name particles:
		for particle in particles:
			if not particle.endswith("*"):
				newParticles.append(particle)
			elif not elidableName:
				elidableName = particle[:-1]

		# fallback for elidable name
		if not newParticles:
			newParticles = [elidableName]

		# set instance name:
		instance.name = " ".join(newParticles)


def biggestSubstringInStrings(strings):
	if len(strings) > 1:
		sortedStrings = sorted(strings, key=lambda string: len(string))
		shortestString = sortedStrings[0]
		shortestLength = len(shortestString)
		otherStrings = sortedStrings[1:]

		if len(shortestString) > 2:
			for stringLength in range(shortestLength, 1, -1):
				for position in range(shortestLength - stringLength + 1):
					subString = shortestString[position:position + stringLength]
					if all([subString in s for s in otherStrings]):
						return subString

	elif len(strings) == 1:
		return strings[0]

	return ""


class InstanceCooker(mekkaObject):
	prefDict = {
		"recipe": defaultRecipe.lstrip()
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 500
		windowHeight = 300
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 1000  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Instance Cooker",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Enter recipe (see tooltips):", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.recipe = vanilla.TextEditor((1, linePos, -1, -inset * 3), text="", callback=self.SavePreferences, checksSpelling=False)
		self.w.recipe.getNSTextView().setToolTip_("Syntax:\n#Axisname\n#Axisname:tag\nposition:instance name particle\ninternal>external:instance name particle\n* after particle for elidable names\n\nExample:\n#Weight\n100>400:Regular*\n120>500:Medium\n150>600:Semibold\n#Width:wdth\n75:Condensed\n100:Regular*\n125:Extended")
		self.w.recipe.getNSScrollView().setHasVerticalScroller_(1)
		self.w.recipe.getNSScrollView().setHasHorizontalScroller_(1)
		self.w.recipe.getNSScrollView().setRulersVisible_(0)

		legibleFont = NSFont.legibleFontOfSize_(NSFont.systemFontSize())
		textView = self.w.recipe.getNSTextView()
		textView.setFont_(legibleFont)
		textView.setHorizontallyResizable_(1)
		textView.setVerticallyResizable_(1)
		textView.setAutomaticDataDetectionEnabled_(1)
		textView.setAutomaticLinkDetectionEnabled_(1)
		textView.setDisplaysLinkToolTips_(1)
		textView.setUsesFindBar_(1)
		textSize = textView.minSize()
		textSize.width = 1000
		textView.setMinSize_(textSize)
		# textView.textContainer().setWidthTracksTextView_(0)
		# textView.textContainer().setContainerSize_(textSize)

		# Run Button:
		buttonPos = inset
		buttonWidth = 70
		self.w.openButton = vanilla.Button((buttonPos, -20 - inset, buttonWidth, -inset), "Open…", sizeStyle='regular', callback=self.importRecipe)
		buttonPos += buttonWidth + 10
		self.w.saveButton = vanilla.Button((buttonPos, -20 - inset, buttonWidth, -inset), "Save…", sizeStyle='regular', callback=self.exportRecipe)
		buttonPos += buttonWidth + 10
		self.w.resetButton = vanilla.Button((buttonPos, -20 - inset, buttonWidth, -inset), "Reset", sizeStyle='regular', callback=self.resetRecipe)
		buttonPos += buttonWidth + 10
		self.w.extractButton = vanilla.Button((buttonPos, -20 - inset, buttonWidth, -inset), "Extract", sizeStyle='regular', callback=self.extractRecipe)
		self.w.runButton = vanilla.Button((-140 - inset, -20 - inset, -inset, -inset), "Cook Instances", sizeStyle='regular', callback=self.InstanceCookerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def exportRecipe(self, sender=None):
		self.SavePreferences()
		filePath = GetSaveFile(message="Save Recipe", ProposedFileName="instance recipe.txt", filetypes=("txt"))
		if filePath:
			fileContent = self.pref("recipe")
			saveFileInLocation(content=fileContent, filePath=filePath)

	def importRecipe(self, sender=None):
		filePath = GetOpenFile(message="Open Recipe", allowsMultipleSelection=False, filetypes=("txt"))
		if filePath:
			fileContent = readFileFromLocation(filePath=filePath)
			if fileContent:
				self.setPref("recipe", fileContent)
				self.LoadPreferences()
			else:
				Message(title="File Error", message="File could not be read. Perhaps empty?", OKButton=None)

	def resetRecipe(self, sender=None):
		self.setPref("recipe", defaultRecipe.lstrip())
		self.LoadPreferences()

	def extractRecipe(self, sender=None):
		thisFont = Glyphs.font
		if not thisFont:
			Message(title="No Font Error", message="You need to have a font open for extracting a recipe.", OKButton=None)
		else:
			text = ""
			for thisAxis in thisFont.axes:
				text += "\n#%s:%s" % (thisAxis.name, thisAxis.axisTag)
				axisValues = sorted(set([int(i.axisValueValueForId_(thisAxis.axisId)) for i in thisFont.instances if i.type == 0]))
				for axisValue in axisValues:
					instancesWithThisAxisValue = [i for i in thisFont.instances if i.axisValueValueForId_(thisAxis.axisId) == axisValue]

					# determine particle:
					allNamesForThisAxisValue = [i.name for i in instancesWithThisAxisValue]
					axisValueName = biggestSubstringInStrings(allNamesForThisAxisValue).strip()

					# determine axis location if any:
					axisLoc = ""
					for thisInstance in instancesWithThisAxisValue:
						locationParameter = thisInstance.customParameters["Axis Location"]
						if locationParameter:
							for entry in locationParameter:
								if entry["Axis"] == thisAxis.name:
									location = float(entry["Location"])
									if location != axisValue:
										axisLoc = ">%i" % location
										break  # skip other entries if we found our value
							if axisLoc:
								break  # skip other instances if we found our value

					# determine width class if any:
					if thisAxis.name == "Width":
						widthClass = "|%i" % instancesWithThisAxisValue[0].widthClass
						axisLoc += widthClass

					if not axisValueName:
						axisValueName = "Regular*"
					text += "\n%i%s:%s" % (axisValue, axisLoc, axisValueName)
				text += "\n"

			text = text.lstrip()
			if not text:
				Message(title="No Instances Found", message="Could not find any instances with discrete values.", OKButton=None)
			else:
				self.w.recipe.set(text)
				self.SavePreferences()

	def InstanceCookerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			instanceCount = 0

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Instance Cooker Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				recipe = self.pref("recipe")
				recipeDict = parseAxes(recipe)
				axisKeys = sorted(recipeDict.keys())
				instances = []

				existingAxisNames = [a.name for a in thisFont.axes]

				for axisKey in axisKeys:
					axisNameParts = axisKey.split(":")
					axisIndex, axisName = axisNameParts[0].split(",")
					axisTag = axisNameParts[1]

					if axisName not in existingAxisNames:
						# create axis
						newAxis = GSAxis()
						newAxis.name = axisName
						newAxis.axisTag = axisTag
						thisFont.axes.append(newAxis)

					axisID = "0"
					for thisAxis in thisFont.axes:
						if thisAxis.name == axisName:
							axisID = thisAxis.axisId

					if not instances:
						for particleInfo in recipeDict[axisKey]:
							instance = GSInstance()
							instance.font = thisFont
							posInfo, instance.name, widthClass = particleInfo
							coord, axisLoc = parsePosInfo(posInfo)
							if widthClass:
								instance.widthClass = widthClass

							# set internal coordinate:
							instance.setAxisValueValue_forId_(coord, axisID)

							# set external coordinate:
							addLocationToInstance(instance, axisName, axisLoc)

							# add style linking:
							styleLinkInstance(instance, axisName, instance.name)

							# collect instance:
							removeElidableNames(instance)
							instances.append(instance)
							print(instance.name)
					else:
						newInstances = []
						for existingInstance in instances:
							for particleInfo in recipeDict[axisKey]:
								instance = existingInstance.copy()
								posInfo, nameParticle, widthClass = particleInfo
								instance.name += " %s" % nameParticle
								coord, axisLoc = parsePosInfo(posInfo)
								if widthClass:
									instance.widthClass = widthClass

								# add internal coordinate:
								instance.setAxisValueValue_forId_(coord, axisID)

								# add external coordinate:
								addLocationToInstance(instance, axisName, axisLoc)

								# add style linking:
								styleLinkInstance(instance, axisName, nameParticle)

								# collect instance:
								removeElidableNames(instance)
								newInstances.append(instance)
								print(instance.name)

						instances = newInstances

				# clean elidable names:
				# print("\nPreparing elidable names...")
				# for instance in instances:
				# 	removeElidableNames(instance)

				# add instances to this font:
				thisFont.instances = [i for i in thisFont.instances if i.type == INSTANCETYPEVARIABLE] + instances
				instanceCount = len(instances)

			# Final report:
			print("Added %i instance%s to %s. Details in Macro Window." % (
				instanceCount,
				"" if instanceCount == 1 else "s",
				thisFont.familyName,
			))
			thisFont.parent.windowController().showFontInfoWindowWithTabSelected_(2)
			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Instance Cooker Error: %s" % e)
			import traceback
			print(traceback.format_exc())


InstanceCooker()
