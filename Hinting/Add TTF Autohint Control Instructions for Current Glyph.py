# MenuTitle: Add TTF Autohint Control Instructions for Current Glyph
__doc__ = """
Adds a touch line for a given up/down amount to the Control Instructions of the current instance.
"""

import math
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSClassFromString,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSNotificationCenter,
	NSTextAlignmentRight,
)


def sizeStringIsOK(sizeString):
	"""
	Checks if the size string adheres to the syntax.
	"""
	for character in sizeString:
		if character not in "1234567890-, ":
			return False
	return True


def italic(yOffset, italicAngle=0.0, pivotalY=0.0):
	"""
	Returns the italicized position of an NSPoint 'thisPoint'
	for a given angle 'italicAngle' and the pivotal height 'pivotalY',
	around which the italic slanting is executed, usually half x-height.
	Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
	"""

	# yOffset = thisPoint.y - pivotalY  # calculate vertical offset
	italicAngle = math.radians(italicAngle)  # convert to radians
	tangens = math.tan(italicAngle)  # math.tan needs radians
	horizontalDeviance = tangens * yOffset  # vertical distance from pivotal point
	return horizontalDeviance


def addToInstructions(instructionLine, currentInstance):
	parameterName = "TTFAutohint control instructions"
	currentInstanceName = currentInstance.name
	commentHeadline = "# %s" % currentInstanceName.upper()

	# determine existing instructions:
	instructions = currentInstance.customParameters[parameterName]

	# normalize single space after comma:
	instructionLine = instructionLine.replace(",", ", ").replace("  ", " ").replace("  ", " ")

	# add to custom parameter:
	if instructions:
		if not instructions.startswith(commentHeadline):
			instructions = "%s\n%s" % (commentHeadline, instructions)
		currentInstance.customParameters[parameterName] = "%s\n%s" % (instructions, instructionLine)
	else:
		currentInstance.customParameters[parameterName] = "%s\n%s" % (commentHeadline, instructionLine)

	# trigger redraw for TTF Control Instructions Palette:
	thisFont = currentInstance.font
	if Glyphs.versionNumber >= 3 and thisFont and thisFont.currentTab:
		NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont.currentTab)


def numberIndexStringFromNumbers(indexes):
	"""
	Turns sequence 1,2,3,4,7,8,9,10,14,19,21,22,23,27,30,31,32
	into "1-4, 7-10, 14, 19, 21-23, 27, 30-32"
	"""
	indexes = sorted(indexes)
	outputString = ""
	previousNumber = -100
	for i, thisNumber in enumerate(indexes):
		if not outputString:
			outputString += str(thisNumber)
		else:
			if previousNumber == thisNumber - 1:
				if outputString[-1] != "-":
					outputString += "-"
				if i == len(indexes) - 1:
					outputString += "%i" % thisNumber
			else:
				if outputString[-1] == "-":
					outputString += "%i" % previousNumber
				outputString += ", %i" % thisNumber
		previousNumber = thisNumber
	return outputString


class AddTTFAutohintControlInstructionsForCurrentGlyph(mekkaObject):
	prefDict = {
		"ppm": "8-12,20",
		"sectionToMove": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 200
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add ttfAutohint Control Instructions for Current Glyph",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.explanatoryText = vanilla.TextBox("auto", "Touch instruction with px offset for active glyph & instance, respects italic angle.", sizeStyle='small', selectable=True)
		# the text wraps, so it takes the width it is given (and gets a fixed height in the rules):
		self.w.explanatoryText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		sectionOptions = (
			"All Points",
			"Upper Half",
			"Upper Third",
			"Upper Quarter",
			"Lower Half",
			"Lower Third",
			"Lower Quarter",
		)
		self.w.sectionToMoveText = vanilla.TextBox("auto", "Touch", sizeStyle='small', selectable=True)
		self.w.sectionToMove = vanilla.PopUpButton("auto", sectionOptions, sizeStyle='small', callback=self.SavePreferences)

		self.w.runButtonAdd100 = vanilla.Button("auto", "+1.00", callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain)
		self.w.runButtonAdd075 = vanilla.Button("auto", "+0.75", callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain)
		self.w.runButtonAdd050 = vanilla.Button("auto", "+0.50", callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain)
		self.w.runButtonAdd025 = vanilla.Button("auto", "+0.25", callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain)
		self.w.runButtonSub025 = vanilla.Button("auto", "-0.25", callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain)
		self.w.runButtonSub050 = vanilla.Button("auto", "-0.50", callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain)
		self.w.runButtonSub075 = vanilla.Button("auto", "-0.75", callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain)
		self.w.runButtonSub100 = vanilla.Button("auto", "-1.00", callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain)

		self.w.ppmText = vanilla.TextBox("auto", "@", sizeStyle='small', selectable=True)
		self.w.ppm = vanilla.EditText("auto", "8-12,20", sizeStyle='small', callback=self.SavePreferences)

		self.w.rightAtTop = vanilla.Button("auto", "right at top", callback=self.InsertRightAtTop)
		self.w.leftAtTop = vanilla.Button("auto", "left at top", callback=self.InsertLeftAtTop)

		# with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned, hug their text and share one width:
		for label in (self.w.sectionToMoveText, self.w.ppmText):
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		buttonNames = (
			"runButtonAdd100",
			"runButtonAdd075",
			"runButtonAdd050",
			"runButtonAdd025",
			"runButtonSub025",
			"runButtonSub050",
			"runButtonSub075",
			"runButtonSub100",
		)
		rules = [
			"H:|-inset-[explanatoryText]-inset-|",
			"H:|-inset-[sectionToMoveText]-gap-[sectionToMove]-inset-|",
			"H:|-inset-[ppmText]-gap-[ppm]-inset-|",
			"H:|-inset-[rightAtTop]-inset-|",
			"H:|-inset-[leftAtTop]-inset-|",
		]
		rules += [f"H:|-inset-[{buttonName}]-inset-|" for buttonName in buttonNames]
		rules += [
			"V:|-gap-[explanatoryText(42)]-section-[sectionToMove]-section-" + "-gap-".join(f"[{buttonName}]" for buttonName in buttonNames) + "-section-[ppm]-section-[rightAtTop]-gap-[leftAtTop]-inset-|",
			{"view1": self.w.sectionToMoveText, "attribute1": "centerY", "view2": self.w.sectionToMove, "attribute2": "centerY"},
			{"view1": self.w.ppmText, "attribute1": "centerY", "view2": self.w.ppm, "attribute2": "centerY"},
			{"view1": self.w.ppmText, "attribute1": "width", "view2": self.w.sectionToMoveText, "attribute2": "width"},
		]
		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "section": 12})

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def fontInstanceToolGlyphLayer(self):
		noResult = (None, None, None, None, None, None, None, None, None)
		Font = Glyphs.font
		if not Font or not Font.currentTab:
			Message(title="ttfAutohint Error", message="The script requires a font with an open Edit tab.", OKButton=None)
			return noResult

		# determine current instance:
		try:
			currentInstance = Font.instances[Font.currentTab.selectedInstance()]
		except:
			Message(title="ttfAutohint Error", message="Could not find the current instance. Pick an instance in the preview area at the bottom of the Edit tab.", OKButton=None)
			return noResult

		# switch to Instructor tool:
		ttInstructorClass = NSClassFromString("GlyphsToolTrueTypeInstructor")
		Font.parent.windowController().setToolForClass_(ttInstructorClass)
		tool = Font.parent.windowController().toolForClass_(ttInstructorClass)

		# double check Instructor tool is on:
		if not tool.className() == "GlyphsToolTrueTypeInstructor":
			Message(title="Tool Error", message="TT Instructor tool (I) must be active", OKButton=None)
		else:
			# determine glyph name:
			layer = Font.currentTab.activeLayer()
			if not layer and tool.activeLayers():
				# fallback attempt if line above fails:
				layer = tool.activeLayers()[0]

			if not layer:
				Message(title="ttfAutohint Error", message="Cannot determine current glyph. Perhaps try closing and reopening the tab. Sorry.", OKButton=None)
			else:
				glyph = layer.glyph()
				glyphName = glyph.name

				# prefix comment with glyph name:
				addToInstructions("# %s" % glyphName, currentInstance)

				# overwrite glyph name with production name, if any:
				if glyph.productionName:
					glyphName = glyph.productionName

				# tt outline:
				glyf = tool.valueForKey_("fontOutlineGlyf")
				glyfBounds = glyf.bounds()

				# tt points:
				coords = glyf.coordinates()
				pointCount = coords.count()

				return Font, currentInstance, tool, glyphName, layer, glyf, glyfBounds, coords, pointCount

		return noResult

	def InsertRightAtTop(self, sender):
		Font, currentInstance, tool, glyphName, layer, glyf, glyfBounds, coords, pointCount = self.fontInstanceToolGlyphLayer()
		if not Font:
			print("ERROR: Could not determine font.")
		else:
			# add right instruction for topmost point if desired:
			highestPointIndex = -1
			highestY = -1000
			for i in range(pointCount):
				thisPoint = coords.pointAtIndex_(i)
				if thisPoint.y > highestY:
					highestPointIndex = i
					highestY = thisPoint.y
			if highestPointIndex > -1:
				instructionLine = "%s right %i" % (glyphName, highestPointIndex)
				addToInstructions(instructionLine, currentInstance)
			else:
				print("ERROR: Could not determine highest point in %s." % glyphName)

	def InsertLeftAtTop(self, sender):
		Font, currentInstance, tool, glyphName, layer, glyf, glyfBounds, coords, pointCount = self.fontInstanceToolGlyphLayer()
		if not Font:
			print("ERROR: Could not determine font.")
		else:
			# add left instruction for topmost point if desired:
			highestPointIndex = -1
			highestY = -1000
			topBound = glyfBounds.origin.y + glyfBounds.size.height
			for i in range(pointCount):
				thisPoint = coords.pointAtIndex_(i)
				prevPoint = coords.pointAtIndex_((i - 1) % pointCount)
				nextPoint = coords.pointAtIndex_((i + 1) % pointCount)
				if thisPoint.y < topBound and thisPoint.y > highestY and thisPoint.y > prevPoint.y and thisPoint.y >= nextPoint.y and (
					thisPoint.x < prevPoint.x or nextPoint.x < thisPoint.x
				):
					highestPointIndex = i
					highestY = thisPoint.y
			if highestPointIndex > -1:
				instructionLine = "%s left %i" % (glyphName, highestPointIndex)
				addToInstructions(instructionLine, currentInstance)
			else:
				print("ERROR: Could not determine highest point in %s." % glyphName)

	def AddTTFAutohintControlInstructionsForCurrentGlyphMain(self, sender):
		try:
			self.SavePreferences()

			shift = float(sender.getTitle())
			print(shift)
			if shift:
				Font, currentInstance, tool, glyphName, layer, glyf, glyfBounds, coords, pointCount = self.fontInstanceToolGlyphLayer()
				if Font:
					# determine x/y move based on italic angle:
					currentMaster = Font.selectedFontMaster
					italicAngle = currentMaster.italicAngle
					if italicAngle:
						moveString = "x %1.2f y %1.2f" % (italic(shift, italicAngle), shift)
					else:
						moveString = "y %1.2f" % shift

					# determine PPMs
					sizeString = self.pref("ppm")
					if not sizeString:
						print("ERROR: Could not determine PPMs, will use a default. Did you enter any?")
						sizeString = "17"
					elif not sizeStringIsOK(sizeString):
						print("ERROR: Illegal character found in PPM specification (%s), will use default instead." % sizeString)
						sizeString = "17"

					# build point indexes to be moved:
					sectionChoice = self.pref("sectionToMove")
					pointIndexString = None

					if sectionChoice > 0:
						pointIndexes = []

						# ranges:
						halfHeight = glyfBounds.origin.y + 0.5 * glyfBounds.size.height
						upperThird = glyfBounds.origin.y + 0.666667 * glyfBounds.size.height
						lowerThird = glyfBounds.origin.y + 0.333333 * glyfBounds.size.height
						upperQuarter = glyfBounds.origin.y + 0.75 * glyfBounds.size.height
						lowerQuarter = glyfBounds.origin.y + 0.25 * glyfBounds.size.height

						for i in range(pointCount):
							thisPoint = coords.pointAtIndex_(i)
							if sectionChoice == 1 and thisPoint.y > halfHeight:
								# Upper Half
								pointIndexes.append(i)
							elif sectionChoice == 2 and thisPoint.y > upperThird:
								# Upper Third
								pointIndexes.append(i)
							elif sectionChoice == 3 and thisPoint.y > upperQuarter:
								# Upper Quarter
								pointIndexes.append(i)
							elif sectionChoice == 4 and thisPoint.y < halfHeight:
								# Lower Half
								pointIndexes.append(i)
							elif sectionChoice == 5 and thisPoint.y < lowerThird:
								# Lower Third
								pointIndexes.append(i)
							elif sectionChoice == 6 and thisPoint.y < lowerQuarter:
								# Lower Quarter
								pointIndexes.append(i)

						if pointIndexes:
							pointIndexString = numberIndexStringFromNumbers(pointIndexes)
					else:
						# all points, choice = 0
						# count of tt paths:
						endPoints = glyf.endPtsOfContours()
						pathCount = len(glyf.endPtsOfContours())
						pointIndexStrings = []
						# all points, in ranges, separated by path:
						j = 0
						for i in range(pathCount):
							k = endPoints.elementAtIndex_(i)
							pointIndexStrings.append("%i-%i" % (j, k))
							j = k + 1
						pointIndexString = ", ".join(pointIndexStrings)

					if not pointIndexString:
						print("ERROR: no point indexes matching your criteria could be found.")
					else:
						# build the instruction line:
						instructionLine = "%s touch %s %s @ %s" % (
							glyphName,
							pointIndexString,
							moveString,
							sizeString,
						)

						# add the instruction line to the parameter:
						if instructionLine:
							addToInstructions(instructionLine, currentInstance)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Add ttfAutohint Control Instructions for Current Glyph Error: %s" % e)
			import traceback
			print(traceback.format_exc())


Glyphs.defaults["TTPreviewAlsoShowGSOFFCURVEIndexes"] = True
AddTTFAutohintControlInstructionsForCurrentGlyph()
