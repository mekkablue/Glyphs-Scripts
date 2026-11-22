# MenuTitle: Instance Cooker
__doc__ = """
Insert many instances at once with a recipe.
"""

import codecs
import vanilla
from mekkablue import mekkaObject, getLegibleFont, makeWindowResizable
from GlyphsApp import Glyphs, GSAxis, GSCustomParameter, GSInstance, INSTANCETYPESINGLE, INSTANCETYPEVARIABLE, GetSaveFile, GetOpenFile, Message
from AppKit import (
	NSColor,
	NSDictionary,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
)

INSTANCETYPEPARTICLE = 4  # GSInstance.type for axis particle instances (Glyphs 4+)

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
0:Roman*
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

	if tagDict.get(axisName):
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
		thisLine = thisLine.strip()
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
					axisTag = tagForAxisName(axisName)
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


def isGlyphs4OrHigher():
	return bool(Glyphs.versionNumber) and Glyphs.versionNumber >= 4


def externalAxisValue(instance, axisName, axisIndex):
	"""
	Returns the user-space coordinate of the instance on the given axis as a float,
	or None if there is none. Glyphs 4: .externalAxesValues; Glyphs 2 and 3 (and as
	fallback for documents not converted yet): the Axis Location parameter.
	"""
	externalAxesValues = getattr(instance, "externalAxesValues", None)
	if externalAxesValues is not None and axisIndex is not None and axisIndex < len(externalAxesValues):
		try:
			value = externalAxesValues[axisIndex]
			if value is not None:
				return float(value)
		except:
			pass

	locationParameter = instance.customParameters["Axis Location"]
	if locationParameter:
		for entry in locationParameter:
			if entry["Axis"] == axisName:
				try:
					return float(entry["Location"])
				except:
					pass

	return None


def markParticleElidable(instance, axisId, nameParticle):
	"""
	Glyphs 4 does not expose elidability of name particles through the API yet.
	The hasattr hooks below pick it up as soon as it does; until then this is a
	no-op returning False, and elidable particles are simply left out of the
	instance name (see removeElidableNames()).
	"""
	if not axisId:
		return False

	setter = getattr(instance, "setNameParticle_elidable_forAxisId_", None)
	if setter:
		try:
			setter(nameParticle, True, axisId)
			return True
		except:
			pass

	setter = getattr(instance, "setElidableNameParticle_forAxisId_", None)
	if setter:
		try:
			setter(nameParticle, axisId)
			return True
		except:
			pass

	return False


def elidableParticleNames(font, axisId):
	"""
	Returns the set of elidable name particles of the font for the given axis.
	Elidability is not in the Glyphs 4 API yet, so the hasattr hooks below will
	return an empty set until it is.
	"""
	elidableNames = set()
	if not isGlyphs4OrHigher():
		return elidableNames

	for instance in font.instances:
		if instance.type != INSTANCETYPEPARTICLE:
			continue
		particles = instance.nameParticles[axisId]
		if not particles:
			continue
		for particle in particles:
			for attributeName in ("elidable", "isElidable"):
				accessor = getattr(particle, attributeName, None)
				if accessor is None:
					continue
				try:
					isElidable = accessor() if callable(accessor) else accessor
				except:
					continue
				if isElidable:
					elidableNames.add(particle.name)
				break

	return elidableNames


def addLocationToInstance(instance, axisName, axisLoc, axisId=None, axisIndex=None):
	if isGlyphs4OrHigher():
		# GLYPHS 4: no more Axis Location parameter, user-space coordinates live on the instance
		if axisIndex is None:
			print(f"⚠️ Could not set external {axisName} coordinate {axisLoc} in ‘{instance.name}’: no such axis.")
		else:
			instance.externalAxesValues[axisIndex] = float(axisLoc)
	else:
		# GLYPHS 2+3:
		paramName = "Axis Location"
		entry = axisLocationEntry(axisName, axisLoc)

		existingLocations = []
		if instance.customParameters[paramName]:
			existingLocations = list(instance.customParameters[paramName])

		existingLocations.append(entry)
		instance.customParameters[paramName] = tuple(existingLocations)

	if axisName == "Weight":
		instance.weightClass = axisLoc


def styleLinkInstance(instance, axisName, particle, defaultName="Regular"):
	linkedParticles = []
	for existingNameParticle in instance.name.split():
		if "*" not in existingNameParticle:
			if not existingNameParticle == particle:
				linkedParticles.append(existingNameParticle)
	linkedStyleName = " ".join(linkedParticles).strip()

	if axisName == "Weight" and particle == "Bold":
		instance.isBold = True
		instance.linkStyle = linkedStyleName
	elif axisName == "Italic" and particle in ("Oblique", "Italic"):
		instance.isItalic = True
		if not instance.linkStyle and linkedStyleName != defaultName:
			instance.linkStyle = linkedStyleName


def removeElidableNames(instance, fallbackName="Regular", splitString=" "):
	if "*" not in instance.name:
		return

	particles = instance.name.split(splitString)
	elidable = len(particles) > 1

	# collect non-elidable name particles:
	newParticles = []
	while particles:
		particle = particles.pop(0)
		if not particle.endswith("*"):
			newParticles.append(particle)
		elif not elidable:
			newParticles.append(particle[:-1])  # the only particle: keep it, without the asterisk

	# fallback for fallback name
	if not newParticles:
		newParticles = [fallbackName]

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
		windowWidth = 530  # wide enough for the four buttons plus the Cook Instances button
		windowHeight = 300
		# the window stays resizable, so the user can enlarge the recipe editor:
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Instance Cooker",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Enter recipe (see tooltips):", sizeStyle='small', selectable=True)

		self.w.recipe = vanilla.TextEditor("auto", text="", callback=self.SavePreferences, checksSpelling=False)
		self.w.recipe.setToolTip("Syntax:\n#Axisname\n#Axisname:tag\nposition:instance name particle\ninternal>external:instance name particle\n* after particle for elidable names\n\nExample:\n#Weight\n100>400:Regular*\n120>500:Medium\n150>600:Semibold\n#Width:wdth\n75:Condensed\n100:Regular*\n125:Extended")
		self.w.recipe.getNSScrollView().setHasVerticalScroller_(1)
		self.w.recipe.getNSScrollView().setHasHorizontalScroller_(1)
		self.w.recipe.getNSScrollView().setRulersVisible_(0)

		legibleFont = getLegibleFont()

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

		# Buttons:
		self.w.openButton = vanilla.Button("auto", "Open…", callback=self.importRecipe)
		self.w.openButton.setToolTip("Load a recipe from a text file.")
		self.w.saveButton = vanilla.Button("auto", "Save…", callback=self.exportRecipe)
		self.w.saveButton.setToolTip("Save the current recipe as a text file.")
		self.w.resetButton = vanilla.Button("auto", "Reset", callback=self.resetRecipe)
		self.w.resetButton.setToolTip("Replace the current recipe with the default recipe, including the recipe instructions.")
		self.w.extractButton = vanilla.Button("auto", "Extract", callback=self.extractRecipe)
		self.w.extractButton.setToolTip("Build a recipe from the instances of the frontmost font.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Cook Instances", callback=self.InstanceCookerMain)
		self.w.runButton.setToolTip("Inserts the instances described by the recipe into the frontmost font.")
		self.w.setDefaultButton(self.w.runButton)

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")

		# everything but the recipe editor hugs vertically, so the editor takes all the leftover height:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		self.w.recipe.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-(>=inset)-|",
				"H:|-1-[recipe]-1-|",
				"H:|-inset-[openButton(>=70)]-gap-[saveButton(>=70)]-gap-[resetButton(>=70)]-gap-[extractButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				"H:|-inset-[status]-inset-|",
				"V:|-gap-[descriptionText]-gap-[recipe(>=150)]-inset-[status]-gap-[runButton]-inset-|",
				"V:[openButton]-inset-|",
				"V:[saveButton]-inset-|",
				"V:[resetButton]-inset-|",
				"V:[extractButton]-inset-|",
			],
			metrics={"inset": inset, "gap": 8},
		)

		makeWindowResizable(self.w, vertical=True)  # resizable, limits in content sizes

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def exportRecipe(self, sender=None):
		self.SavePreferences()
		# positional arguments: the second one is called ProposedFileName in Glyphs 3, proposedFileName in Glyphs 4
		filePath = GetSaveFile("Save Recipe", "instance recipe.txt", ["txt"])
		if filePath:
			self.setStatus("🛠️ Saving recipe …")
			fileContent = self.pref("recipe")
			saveFileInLocation(content=fileContent, filePath=filePath)
			self.setStatus("✅ Saved recipe.")


	def importRecipe(self, sender=None):
		filePath = GetOpenFile(message="Open Recipe", allowsMultipleSelection=False, filetypes=["txt"])
		if filePath:
			self.setStatus("🛠️ Loading recipe …")
			fileContent = readFileFromLocation(filePath=filePath)
			if fileContent:
				self.setPref("recipe", fileContent)
				self.LoadPreferences()
				self.setStatus("✅ Loaded recipe.")
			else:
				self.setStatus("⚠️ File could not be read.")
				Message(title="File Error", message="File could not be read. Perhaps empty?", OKButton=None)


	def resetRecipe(self, sender=None):
		self.setPref("recipe", defaultRecipe.lstrip())
		self.LoadPreferences()
		self.setStatus("✅ Reset recipe.")


	def extractRecipe(self, sender=None):
		thisFont = Glyphs.font
		if not thisFont:
			self.setStatus("⚠️ No font open.")
			Message(title="No Font Error", message="You need to have a font open for extracting a recipe.", OKButton=None)
		else:
			self.setStatus("🛠️ Extracting recipe …")
			text = ""
			singleInstances = [i for i in thisFont.instances if i.type == INSTANCETYPESINGLE]
			for axisIndex, thisAxis in enumerate(thisFont.axes):
				self.setStatus(f"🔠 {thisAxis.name}")
				text += "\n#%s:%s" % (thisAxis.name, thisAxis.axisTag)
				elidableNames = elidableParticleNames(thisFont, thisAxis.axisId)
				axisValues = sorted(set([int(i.axisValueValueForId_(thisAxis.axisId)) for i in singleInstances]))
				for axisValue in axisValues:
					instancesWithThisAxisValue = [i for i in singleInstances if i.axisValueValueForId_(thisAxis.axisId) == axisValue]

					# determine particle:
					allNamesForThisAxisValue = [i.name for i in instancesWithThisAxisValue]
					axisValueName = biggestSubstringInStrings(allNamesForThisAxisValue).strip()

					# determine external coordinate if any:
					axisLoc = ""
					for thisInstance in instancesWithThisAxisValue:
						location = externalAxisValue(thisInstance, thisAxis.name, axisIndex)
						if location is not None and location != axisValue:
							axisLoc = ">%i" % location
							break  # skip other instances if we found our value

					# determine width class if any:
					if thisAxis.name == "Width":
						widthClass = "|%i" % instancesWithThisAxisValue[0].widthClass
						axisLoc += widthClass

					if not axisValueName:
						axisValueName = "Regular*"
					elif axisValueName in elidableNames:
						axisValueName += "*"
					text += "\n%i%s:%s" % (axisValue, axisLoc, axisValueName)
				text += "\n"

			text = text.lstrip()
			if not text:
				self.setStatus("⚠️ No instances with discrete values found.")
				Message(title="No Instances Found", message="Could not find any instances with discrete values.", OKButton=None)
			else:
				self.w.recipe.set(text)
				self.SavePreferences()
				self.setStatus(f"✅ Extracted recipe for {len(thisFont.axes)} axes.")


	def axisLocationsFromRecipe(self, recipeDict):
		axisLocations = []
		for axisKey in sorted(recipeDict.keys()):
			# axis tag
			axisInfo, axisName, axisTag = axisKey, None, None
			if "," in axisInfo:
				axisInfo = axisInfo.split(",")[1]
			if ":" in axisInfo:
				axisName, axisTag = axisInfo.split(":")
			else:
				axisName = axisInfo
				axisTag = tagForAxisName(axisName)
			axisLocation = f"{axisTag}; "

			# style attributes
			for styleInfo in recipeDict[axisKey]:
				# add axis location:
				styleCoord = styleInfo[0]
				if isinstance(styleCoord, (list, tuple)):
					styleCoord = styleCoord[1]
				axisLocation += f"{styleCoord:.1f}"

				# add style linking:
				if axisTag == "wght" and styleCoord == 400:
					axisLocation += ">700.0"
				if axisTag == "ital" and styleCoord == 0:
					axisLocation += ">1"

				# add style name:
				styleName = styleInfo[1]
				axisLocation += f"={styleName}, "

			# collect axis location
			axisLocation = axisLocation.strip(", ")
			axisLocations.append(axisLocation)

		return axisLocations


	def addAxisLocations(self, thisFont, recipeDict, paramName="Axis Values"):
		firstVF = None
		for instance in thisFont.instances:
			if instance.type == INSTANCETYPEVARIABLE:
				firstVF = instance
				break

		if not firstVF:
			return

		if firstVF.customParameters[paramName]:
			return  # do not overwrite existing axis values

		# turn user entry into STAT axis values:
		axisLocations = self.axisLocationsFromRecipe(recipeDict)

		# add italic axis if necessary:
		if not any([x.startswith("ital") for x in axisLocations]):
			if "Italic" in firstVF.name:
				axisLocations.append("ital; 1=Italic")
			elif "Oblique" in firstVF.name:
				axisLocations.append("ital; 1=Oblique")
			else:
				axisLocations.append("ital; 0>1=Roman")

		# add axis values parameters to VF:
		for axisLocation in axisLocations:
			parameter = GSCustomParameter(paramName, axisLocation)
			parameter.active = False  # does not seem to work?
			firstVF.customParameters.append(parameter)


	def InstanceCookerMain(self, sender=None):
		lastItem = "start"
		try:
			# clear macro window log:
			Glyphs.clearLog()
			instanceCount = 0
			self.setStatus("🛠️ Processing …")

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				self.setStatus("⚠️ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Instance Cooker Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(f"📄 {thisFont.filepath}")
				else:
					print(f"📄 {thisFont.familyName} (unsaved)")
				print()

				recipe = self.pref("recipe")
				recipeDict = parseAxes(recipe)
				axisKeys = sorted(recipeDict.keys())
				instances = []

				# add to VFs if possible and necessary:
				# single-entry axes are included so they get a STAT design axis entry
				self.addAxisLocations(thisFont, recipeDict)

				existingAxisNames = [a.name for a in thisFont.axes]

				# separate single-entry axes: skip as variation axes, just add particle to all instances
				singleEntryParticles = []  # list of (axisName, nameParticle) tuples
				multiEntryAxisKeys = []
				for axisKey in axisKeys:
					if len(recipeDict[axisKey]) == 1:
						axisNameParts = axisKey.split(":")
						_, axisName = axisNameParts[0].split(",")
						_, nameParticle, _ = recipeDict[axisKey][0]
						singleEntryParticles.append((axisName, nameParticle))
						print(f"ℹ️ Axis '{axisName}' has only one entry — skipping variation axis, adding '{nameParticle.rstrip('*')}' to all instances.")
					else:
						multiEntryAxisKeys.append(axisKey)

				for axisKey in multiEntryAxisKeys:
					lastItem = axisKey
					self.setStatus(f"🔠 {axisKey.split(',', 1)[-1].split(':')[0]}")
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
					axisIndex = None
					for i, thisAxis in enumerate(thisFont.axes):
						if thisAxis.name == axisName:
							axisID = thisAxis.axisId
							axisIndex = i

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
							addLocationToInstance(instance, axisName, axisLoc, axisId=axisID, axisIndex=axisIndex)

							# mark elidable name particle (no-op until the API supports it):
							if instance.name.endswith("*"):
								markParticleElidable(instance, axisID, instance.name.rstrip("*"))

							# add style linking:
							styleLinkInstance(instance, axisName, instance.name)

							# collect instance:
							# removeElidableNames(instance)
							instances.append(instance)
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
								addLocationToInstance(instance, axisName, axisLoc, axisId=axisID, axisIndex=axisIndex)

								# mark elidable name particle (no-op until the API supports it):
								if nameParticle.endswith("*"):
									markParticleElidable(instance, axisID, nameParticle.rstrip("*"))

								# add style linking:
								styleLinkInstance(instance, axisName, nameParticle)

								# collect instance:
								# removeElidableNames(instance)
								newInstances.append(instance)

						instances = newInstances

				# if only single-entry axes were defined, seed one base instance
				if not instances and singleEntryParticles:
					instance = GSInstance()
					instance.font = thisFont
					instance.name = ""
					instances.append(instance)

				# append single-entry axis particles to all instances
				for axisName, nameParticle in singleEntryParticles:
					for instance in instances:
						if instance.name:
							instance.name += " %s" % nameParticle
						else:
							instance.name = nameParticle
						styleLinkInstance(instance, axisName, nameParticle)

				# clean elidable names:
				for instance in instances:
					lastItem = instance.name
					self.setStatus(f"🔠 {instance.name}")
					removeElidableNames(instance)
					print(f"ℹ️ {instance.name}")

				# add instances to this font:
				# keep VF settings and (Glyphs 4) particle instances, replace the single instances:
				keptTypes = (INSTANCETYPEVARIABLE, INSTANCETYPEPARTICLE)
				thisFont.instances = [i for i in thisFont.instances if i.type in keptTypes] + instances
				instanceCount = len(instances)

				# Final report:
				print("\nAdded %i instance%s to %s." % (
					instanceCount,
					"" if instanceCount == 1 else "s",
					thisFont.familyName,
				))
				thisFont.parent.windowController().showFontInfoWindowWithTabSelected_(2)
				self.setStatus(f"✅ Added {instanceCount} instance{'' if instanceCount == 1 else 's'}.")
				self.w.close()
				print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			self.setStatus(f"❌ Error at {lastItem}. Details in Macro Window.")
			print("Instance Cooker Error: %s" % e)
			import traceback
			print(traceback.format_exc())


InstanceCooker()
