# MenuTitle: Batch Grader
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__ = """
Batch-add graded masters to a multiple-master setup.
"""

import vanilla
from copy import copy
from Foundation import NSPoint
from AppKit import NSFont
from GlyphsApp import Glyphs, GSFont, GSLayer, GSAxis, GSInstance, GSCustomParameter, GSSMOOTH, GSOFFCURVE, Message
from mekkablue import mekkaObject


def hasIncrementalKey(layer, checkLSB=True, checkRSB=True):
	incrementalKeys = ("=-", "=+", "=*", "=/")
	glyph = layer.parent
	if checkLSB:
		for key in incrementalKeys:
			if layer.leftMetricsKey:
				if key in layer.leftMetricsKey:
					return True
			elif glyph.leftMetricsKey:
				if key in glyph.leftMetricsKey:
					return True
	if checkRSB:
		for key in incrementalKeys:
			if layer.rightMetricsKey:
				if key in layer.rightMetricsKey:
					return True
			elif glyph.rightMetricsKey:
				if key in glyph.rightMetricsKey:
					return True
	return False


def biggestSubstringInStrings(strings):
	if len(strings) > 1:
		sortedStrings = sorted(strings, key=lambda string: len(string))
		shortestString = sortedStrings[0]
		shortestLength = len(shortestString)
		otherStrings = sortedStrings[1:]

		if len(shortestString) > 2:
			for stringLength in range(shortestLength, 1, -1):
				for position in range(shortestLength - stringLength + 1):
					subString = shortestString[position: position + stringLength]
					if all([subString in s for s in otherStrings]):
						return subString

	elif len(strings) == 1:
		return strings[0]

	return ""


def updateBraceLayers(font, defaultValue=0, newAxisTag=None, newAxisValue=None):
	axisRanges = font.variationAxesRanges_(None)  # ["GRAD"][0]
	# newAxisIdx = axisIndexForTag(font, tag=newAxisTag)

	for glyph in font.glyphs:
		if not glyph.hasSpecialLayers():
			continue
		print(glyph.name)
		count = 0
		try:
			newBraceCoordinates = []
			for layer in glyph.layers:
				isBraceLayer = (
					layer.isSpecialLayer
					and layer.attributes
					and layer.attributes["coordinates"]
				)
				if isBraceLayer:
					coords = dict(layer.attributes["coordinates"])
					allAxisIDs = []
					changed = False
					for axis in font.axes:
						# add missing axis (GRAD axis just added) to brace layer:
						allAxisIDs.append(axis.id)
						if axis.id not in coords.keys():
							coords[axis.id] = defaultValue
							changed = True

						# fix range errors for recently subsetted file,
						# e.g. slnt=0 when all the font is slnt=-10:
						axisMin = axisRanges[axis.axisTag][0]
						axisMax = axisRanges[axis.axisTag][2]
						axisValue = coords[axis.id]
						if axisValue < axisMin or axisValue > axisMax:
							axisValue = min(axisMax, axisValue)
							axisValue = max(axisMin, axisValue)
							coords[axis.id] = axisValue
							changed = True

					# clean out axes from brace layer if they are not in the file anymore:
					existingKeys = tuple(coords.keys())
					for key in existingKeys:
						if key not in allAxisIDs:
							del coords[key]
							changed = True

					if changed:
						layer.attributes["coordinates"] = coords
						count += 1

					if newAxisTag:
						for axis in font.axes:
							if axis.axisTag == newAxisTag:
								coords[axis.id] = newAxisValue
						newBraceCoordinates.append((layer.associatedMasterId, coords))

			if not newBraceCoordinates:
				continue
			newBraceLayerCount = 0
			for masterID, newBraceCoordinate in newBraceCoordinates:
				# clean existing layers with the same coordinates
				for i in range(len(glyph.layers) - 1, -1, -1):
					layer = glyph.layers[i]
					if layer.isSpecialLayer and layer.attributes and layer.attributes["coordinates"]:
						if layer.attributes["coordinates"] == newBraceCoordinate:
							print(f"❌ Deleting preexisting brace layer in {glyph.name}...")
							del glyph.layers[i]
				# add and reinterpolate the brace layer
				newBraceLayerCount += 1
				newBraceLayer = GSLayer()
				glyph.layers.append(newBraceLayer)
				originalMaster = font.fontMasterForId_(masterID)
				axes = originalMaster.axes
				for i, axis in enumerate(font.axes):
					if axis.axisTag == newAxisTag:
						axes[i] = newAxisValue
						break
				for master in font.masters:
					if master.axes == axes:
						newBraceLayer.associatedMasterId = master.id
				newBraceLayer.attributes["coordinates"] = newBraceCoordinate
				newBraceLayer.reinterpolate()
			print(f"✅ Added {newBraceLayerCount} new brace layer{'' if newBraceLayerCount==1 else 's'} with {newAxisTag}={newAxisValue}.")

		except IndexError:
			pass

		if count > 0:
			print(f"🦾 Updated {count} brace layer{'' if count==1 else 's'} for ‘{glyph.name}’")


def axisIndexForTag(font, tag="wght"):
	for i, a in enumerate(font.axes):
		if a.axisTag == tag:
			return i
	return None


def fitSidebearings(layer, targetWidth, left=0.5):
	if not layer.shapes:
		layer.width = targetWidth
	else:
		diff = targetWidth - layer.width
		diff *= left
		layer.LSB += diff
		layer.width = targetWidth


def straightenBCPs(layer):
	def closestPointOnLine(P, A, B):
		# vector of line AB
		AB = NSPoint(B.x - A.x, B.y - A.y)
		# vector from point A to point P
		AP = NSPoint(P.x - A.x, P.y - A.y)
		# dot product of AB and AP
		dotProduct = AB.x * AP.x + AB.y * AP.y
		ABsquared = AB.x**2 + AB.y**2
		t = dotProduct / ABsquared
		x = A.x + t * AB.x
		y = A.y + t * AB.y
		return NSPoint(x, y)

	def ortho(n1, n2):
		xDiff = n1.x - n2.x
		yDiff = n1.y - n2.y
		# must not have the same coordinates,
		# and either vertical or horizontal:
		if xDiff != yDiff and xDiff * yDiff == 0.0:
			return True
		return False

	for p in layer.paths:
		for n in p.nodes:
			if n.connection != GSSMOOTH:
				continue
			nn, pn = n.nextNode, n.prevNode
			if any((nn.type == GSOFFCURVE, pn.type == GSOFFCURVE)):
				# surrounding points are BCPs
				smoothen, center, opposite = None, None, None
				for handle in (nn, pn):
					if ortho(handle, n):
						center = n
						opposite = handle
						smoothen = nn if nn != handle else pn
						p.setSmooth_withCenterNode_oppositeNode_(
							smoothen, center, opposite
						)
						break
				if smoothen == center == opposite is None:
					n.position = closestPointOnLine(n.position, nn, pn)

			# elif n.type != GSOFFCURVE and (nn.type, pn.type).count(GSOFFCURVE) == 1:
			# 	# only one of the surrounding points is a BCP
			# 	center = n
			# 	if nn.type == GSOFFCURVE:
			# 		smoothen = nn
			# 		opposite = pn
			# 	elif pn.type == GSOFFCURVE:
			# 		smoothen = pn
			# 		opposite = nn
			# 	else:
			# 		continue  # should never occur
			# 	p.setSmooth_withCenterNode_oppositeNode_(
			# 		smoothen, center, opposite,
			# 	)


class BatchGrader(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"graderCode": "# mastername: wght+=100, wdth=100 ",
		"axisName": "Grade",
		"gradeAxisTag": "GRAD",
		"grade": 100,
		"searchFor": "GD0",
		"replaceWith": "GD100",
		"excludeFromInterpolation": "Grade, GD100",
		"addSyncMetricCustomParameter": True,
		"metricsKeyChoice": 0,
		"keepCenteredGlyphsCentered": True,
		"keepCenteredThreshold": 2,
		"addGradedBraceLayers": False,
		"temporarilySwitchToDefaultInterpolation": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 390
		windowHeight = 260
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 1000  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Batch Grader",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(
				windowWidth + windowWidthResize,
				windowHeight + windowHeightResize,
			),  # maximum size (for resizing)
			autosaveName=self.domain(
				"mainwindow"
			),  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		indent = 65

		tooltipText = "The Grade value. Should roughly correspnd to the weight value. E.g., Grade 100 means that the shapes appear to be of the weight that is 100 above the current weight."
		self.w.gradeText = vanilla.TextBox((inset, linePos + 3, indent, 14), "Add grade:", sizeStyle="small", selectable=True)
		self.w.gradeText.getNSTextField().setToolTip_(tooltipText)
		self.w.grade = vanilla.ComboBox((inset + indent, linePos - 1, 55, 19), ("-100", "-50", "50", "100"), sizeStyle="small", callback=self.SavePreferences)
		self.w.grade.getNSComboBox().setToolTip_(tooltipText)

		tooltipText = "The Grade axis. Specify a four-letter axis tag (default ‘GRAD’) and a human-readable name (default ‘Grade’). Use all-caps letters for the axis tag as long as Grade is not a registered axis in the OpenType spec. The update button will insert the current convention: tag ‘GRAD’ and name ‘Grade’."
		self.w.gradeAxisTagText = vanilla.TextBox((inset + indent + 65, linePos + 3, 100, 14), "Axis tag & name:", sizeStyle="small", selectable=True)
		self.w.gradeAxisTagText.getNSTextField().setToolTip_(tooltipText)
		self.w.gradeAxisTag = vanilla.EditText((inset + indent + 100 + 60, linePos, 45, 19), "GRAD", callback=self.SavePreferences, sizeStyle="small")
		self.w.gradeAxisTag.getNSTextField().setToolTip_(tooltipText)
		self.w.axisName = vanilla.EditText((inset + indent + 100 + 110, linePos, -inset - 25, 19), "Grade", callback=self.SavePreferences, sizeStyle="small")
		self.w.axisName.getNSTextField().setToolTip_(tooltipText)
		self.w.axisReset = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.updateUI)
		self.w.axisReset.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight

		indent = 110

		tooltipText = "Renaming for the newly added graded masters. You can search and replace in the name of the base master, the result will be used as name for the graded master. Leave the ‘Search for’ field empty if you want to just add a particle to the end of the master name, e.g. ‘Graded’ only in the ‘Replace with’ field."
		self.w.searchForText = vanilla.TextBox((inset, linePos + 3, indent, 14), "In name, search for:", sizeStyle="small", selectable=True)
		self.w.searchForText.getNSTextField().setToolTip_(tooltipText)
		self.w.searchFor = vanilla.EditText((inset + indent, linePos, 60, 19), self.pref("searchFor"), callback=self.SavePreferences, sizeStyle="small")
		self.w.searchFor.getNSTextField().setToolTip_(tooltipText)
		self.w.replaceWithText = vanilla.TextBox((inset + indent + 65, linePos + 3, 100, 14), "and replace with:", sizeStyle="small", selectable=True)
		self.w.replaceWithText.getNSTextField().setToolTip_(tooltipText)
		self.w.replaceWith = vanilla.EditText((inset + indent + 165, linePos, -inset, 19), self.pref("replaceWith"), callback=self.SavePreferences, sizeStyle="small")
		self.w.replaceWith.getNSTextField().setToolTip_(tooltipText)
		linePos += lineHeight

		indent = 150
		tooltipText = "Specify which masters are ignored for (a) interpolating the graded masters and (b) resetting the recipe. Add comma-separated name particles. All masters containing these particles will be ignored."
		self.w.excludeFromInterpolationText = vanilla.TextBox((inset, linePos + 3, -inset, 14), "Ignore masters containing:", sizeStyle="small", selectable=True)
		self.w.excludeFromInterpolationText.getNSTextField().setToolTip_(tooltipText)
		self.w.excludeFromInterpolation = vanilla.EditText((inset + indent, linePos, -inset - 25, 19), self.prefDict["excludeFromInterpolation"], callback=self.SavePreferences, sizeStyle="small")
		self.w.excludeFromInterpolation.getNSTextField().setToolTip_(tooltipText)
		self.w.ignoreReset = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.updateUI)
		self.w.ignoreReset.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.addGradedBraceLayers = vanilla.CheckBox((inset, linePos - 1, 200, 20), "Add graded brace layers (slow)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.temporarilySwitchToDefaultInterpolation = vanilla.CheckBox((inset + 200, linePos - 1, -inset + 230, 20), "Use default interpolation", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.addSyncMetricCustomParameter = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Add custom parameter ‘Link Metrics With Master’ (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.addSyncMetricCustomParameter.getNSButton().setToolTip_("Will add a custom parameter that links the spacing and kerning of the graded master to its respective base master. Keep this checkbox on unless you know what you are doing.")
		linePos += lineHeight

		tooltipText = "When refitting the graded shapes into the respective base widths, what should happen with metrics keys? If you don’t do anything, it will still work, but Glyphs will show a lot of metric sync warnings in Font View. If you disable all keys, the script will add self referential layer keys to overwrite the glyph keys, effectively disabling the metrics key on the graded master. In special cases, you can also choose to prefer (and update) the keys of one side only."
		metricsKeyOptions = (
			"Don’t do anything (will keep metrics warnings though)",
			"Prefer RSB keys (and disable LSB keys in graded masters)",
			"Prefer LSB keys (and disable RSB keys in graded masters)",
			"Disable all keys in graded masters (recommended)",
		)
		self.w.metricsKeyChoiceText = vanilla.TextBox((inset, linePos + 2, 130, 14), "Deal with metrics keys:", sizeStyle="small", selectable=True)
		self.w.metricsKeyChoiceText.getNSTextField().setToolTip_(tooltipText)
		self.w.metricsKeyChoice = vanilla.PopUpButton((inset + 130, linePos, -inset, 17), metricsKeyOptions, sizeStyle="small", callback=self.SavePreferences)
		self.w.metricsKeyChoice.getNSPopUpButton().setToolTip_(tooltipText)
		linePos += lineHeight

		tooltipText = "Will actively recenter glyphs after interpolation if they are centered in the base master. The threshold specifies the maximum difference between LSB and RSB that is acceptable to consider the glyph centered. Best to use 1 or 2."
		self.w.keepCenteredGlyphsCentered = vanilla.CheckBox((inset, linePos, 305, 20), "Keep centered glyphs centered; max SB diff threshold:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.keepCenteredGlyphsCentered.getNSButton().setToolTip_(tooltipText)
		self.w.keepCenteredThreshold = vanilla.EditText((inset + 305, linePos, -inset, 19), "2", callback=self.SavePreferences, sizeStyle="small")
		self.w.keepCenteredThreshold.getNSTextField().setToolTip_(tooltipText)
		linePos += lineHeight

		linePos += 10
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Recipe for new graded masters:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.graderCode = vanilla.TextEditor((1, linePos, -1, -inset * 3), text=self.prefDict["graderCode"], callback=self.SavePreferences, checksSpelling=False)
		self.w.graderCode.getNSTextView().setToolTip_("- Prefix comments with hashtag (#)\n- Empty line are ignored\n- Recipe syntax: MASTERNAME: AXISTAG+=100, AXISTAG=400, AXISTAG-=10")
		self.w.graderCode.getNSScrollView().setHasVerticalScroller_(1)
		self.w.graderCode.getNSScrollView().setHasHorizontalScroller_(1)
		self.w.graderCode.getNSScrollView().setRulersVisible_(0)
		textView = self.w.graderCode.getNSTextView()
		try:
			legibleFont = NSFont.userFixedPitchFontOfSize_(NSFont.systemFontSize())
			textView.setFont_(legibleFont)
		except Exception as e:
			print(e)

		# Buttons:
		self.w.resetButton = vanilla.Button((inset, -20 - inset, 80, -inset), "Reset", sizeStyle="regular", callback=self.ResetGraderCode)
		self.w.resetButton.getNSButton().setToolTip_("Will populate the recipe field with the masters and the settings above. Careful: will overwrite what you had here before.")
		self.w.helpButton = vanilla.HelpButton((inset + 90, -20 - inset, 21, 21), callback=self.openURL)
		self.w.helpButton.getNSButton().setToolTip_("Will open a Loom video explaining the script. You need an internet connection.")
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Add Grades", sizeStyle="regular", callback=self.BatchGraderMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		if sender == self.w.axisReset:
			self.w.gradeAxisTag.set("GRAD")
			self.w.axisName.set("Grade")
			self.SavePreferences()
		elif sender == self.w.ignoreReset:
			excludeParticles = []
			thisFont = Glyphs.font
			grade = self.prefInt("grade")
			gradeAxisTag = f'{self.pref("gradeAxisTag").strip()[:4]:4}'
			axisIdx = axisIndexForTag(thisFont, gradeAxisTag)
			if axisIdx is not None:
				masterNames = [m.name for m in thisFont.masters if m.axes[axisIdx] == grade]
				commonParticle = biggestSubstringInStrings(masterNames)
				if commonParticle:
					excludeParticles.append(commonParticle)
			for prefName in ("replaceWith", "axisName"):
				if self.pref(prefName):
					excludeParticles.append(self.pref(prefName))
			if excludeParticles:
				self.w.excludeFromInterpolation.set(", ".join(set(excludeParticles)))
			self.SavePreferences()
		else:
			self.w.keepCenteredGlyphsCentered.enable(
				not self.w.metricsKeyChoice.get() in (1, 2)
			)
			self.w.keepCenteredThreshold.enable(
				self.w.keepCenteredGlyphsCentered.get()
				and self.w.keepCenteredGlyphsCentered.isEnabled()
			)

	def openURL(self, sender=None):
		URL = None
		if sender == self.w.helpButton:
			URL = "https://www.loom.com/share/3883d03e5f194b35ae80a90b2aca1395?sid=a1619ac8-c38a-4e30-879d-f08ea907d045"
		if URL:
			import webbrowser

			webbrowser.open(URL)

	def ResetGraderCode(self, sender=None):
		thisFont = Glyphs.font
		text = "# mastername: wght+=100, wdth=100\n"
		gradeValue = self.prefInt("grade")
		wghtCode = f"wght+={gradeValue}".replace("+=-", "-=")
		for m in thisFont.masters:
			if self.shouldExcludeMaster(m):
				continue
			text += f"{m.name}: {wghtCode}\n"
		self.w.graderCode.set(text)

	def shouldExcludeMaster(self, master):
		excludedParticles = self.pref("excludeFromInterpolation")
		excludedParticles = [p.strip() for p in excludedParticles.split(",") if p]
		for particle in excludedParticles:
			if particle in master.name:
				return True  # yes, exclude
		return False  # no, don't exclude

	def masterAxesString(self, master):
		font = master.font
		return ", ".join(
			[f"{a.axisTag}={master.axes[i]}" for i, a in enumerate(font.axes)]
		)

	def reducedInterpolation(self, originalFont, interpolationDict, axes):
		# build empty dummy font:
		font = GSFont()
		font.masters = []  # remove default master
		font.axes = copy(originalFont.axes)

		# add only the masters we need:
		for i in range(len(originalFont.masters)):
			if originalFont.masters[i].id in interpolationDict.keys():
				addMaster = copy(originalFont.masters[i])
				addMaster.font = font
				font.masters.append(addMaster)

		# dummy instance for recalculating the coeffs:
		instance = GSInstance()
		instance.font = font
		instance.axes = axes
		return instance.instanceInterpolations

	def cleanInterpolationDict(self, instance):
		font = instance.font
		print(f"🙈 Cleaning interpolation dict for: {self.masterAxesString(instance)}")

		interpolationDict = instance.instanceInterpolations
		# dictReport = [f"{instance.instanceInterpolations[k]*100:8.2f}%: {font.masters[k].name}" for k in interpolationDict.keys()]

		newInterpolationDict = {}
		total = 0.0
		for k in interpolationDict.keys():
			m = font.masters[k]
			if not m or self.shouldExcludeMaster(m):
				continue
			newInterpolationDict[k] = interpolationDict[k]
			total += newInterpolationDict[k]
		if not newInterpolationDict:
			print("⚠️ Exclusion rules would make interpolation impossible. Leaving as is.")
		else:
			if total != 1.0:
				factor = 1.0 / total
				for k in newInterpolationDict.keys():
					newInterpolationDict[k] *= factor
			instance.manualInterpolation = True
			instance.instanceInterpolations = newInterpolationDict

		# circumvent buggy coeff calculation (with many axes) with reduced interpolation:
		reducedDict = self.reducedInterpolation(font, instance.instanceInterpolations, instance.axes)
		if instance.instanceInterpolations != reducedDict:
			reducedInstanceInterpolations = self.reducedInterpolation(font, instance.instanceInterpolations, instance.axes)
			instance.manualInterpolation = True
			instance.instanceInterpolations = reducedInstanceInterpolations

	def updateGradeAxis(self, thisFont):
		# add or update Grade axis if necessary:
		axisName = self.pref("axisName").strip()
		gradeAxisTag = f'{self.pref("gradeAxisTag").strip()[:4]:4}'
		existingAxisTags = [a.axisTag for a in thisFont.axes]
		if gradeAxisTag not in existingAxisTags:
			print(f"Adding axis ‘{axisName}’ ({gradeAxisTag})")
			gradeAxis = GSAxis()
			gradeAxis.name = axisName
			gradeAxis.axisTag = gradeAxisTag
			gradeAxis.hidden = False
			thisFont.axes.append(gradeAxis)
			thisFont.didChangeValueForKey_("axes")
		else:
			gradeAxis = thisFont.axisForTag_(gradeAxisTag)
			if gradeAxis.name != axisName:
				print(f"Updating {gradeAxisTag} axis name: {gradeAxis.name} → {axisName}")
				gradeAxis.name = axisName
		return gradeAxis

	def addGradeLayers(self, metricsKeyChoice, master, weightedInstance, weightedFont, gradeMaster, baseGlyph):
		baseLayer = baseGlyph.layers[master.id]
		baseWidth = baseLayer.width

		# get interpolated layer and prepare for width adjustment
		weightedGlyph = weightedFont.glyphs[baseGlyph.name]
		weightedLayer = weightedGlyph.layers[0]
		straightenBCPs(weightedLayer)
		weightedWidth = weightedLayer.width
		if weightedWidth != baseWidth:
			fitSidebearings(weightedLayer, targetWidth=baseWidth, left=0.5)

		# bring the interpolated shapes back into the open font:
		gradeLayer = baseGlyph.layers[gradeMaster.id]
		gradeLayer.width = weightedLayer.width
		gradeLayer.shapes = copy(weightedLayer.shapes)
		gradeLayer.anchors = copy(weightedLayer.anchors)
		gradeLayer.hints = copy(weightedLayer.hints)

		# cancel instance
		weightedInstance.font = None

		# reinstate automatic alignment if necessary:
		if baseLayer.isAligned and not gradeLayer.isAligned:
			for index, gradeComponent in enumerate(gradeLayer.components):
				baseComponent = baseLayer.components[index]
				gradeComponent.alignment = baseComponent.alignment

		# disable metrics keys where necessary/requested:
		if (baseGlyph.leftMetricsKey or baseLayer.leftMetricsKey) and metricsKeyChoice in (1, 3):
			isIncrementalKey = (baseLayer.isAligned and hasIncrementalKey(baseLayer))
			if not isIncrementalKey:
				gradeLayer.leftMetricsKey = f"=={baseGlyph.name}"
			else:
				gradeLayer.leftMetricsKey = baseLayer.leftMetricsKey
		if (baseGlyph.rightMetricsKey or baseLayer.rightMetricsKey) and metricsKeyChoice in (2, 3):
			isIncrementalKey = (baseLayer.isAligned and hasIncrementalKey(baseLayer))
			if not isIncrementalKey:
				gradeLayer.rightMetricsKey = f"=={baseGlyph.name}"
			else:
				gradeLayer.rightMetricsKey = baseLayer.rightMetricsKey
		if baseGlyph.widthMetricsKey and metricsKeyChoice in (1, 2, 3):
			gradeLayer.widthMetricsKey = f"=={baseGlyph.name}"
		if (baseGlyph.leftMetricsKey or baseGlyph.rightMetricsKey) and metricsKeyChoice in (1, 2):
			gradeLayer.syncMetrics()
		if hasIncrementalKey(gradeLayer):
			gradeLayer.syncMetrics()

	def addMissingAxisLocations(self, thisFont, gradeAxis):
		if Glyphs.versionNumber >= 4:
			return

		print("📐 Updating Axis Locations in masters...")
		for thisMaster in thisFont.masters:
			axLoc = thisMaster.customParameters["Axis Location"]
			if axLoc and len(axLoc) < len(thisFont.axes):
				axLoc.append(
					{
						"Axis": self.pref("axisName"),
						"Location": thisMaster.axisValueValueForId_(gradeAxis.id),
					}
				)
				thisMaster.customParameters["Axis Location"] = axLoc

		print("📐 Updating Axis Locations in instances...")
		for thisInstance in thisFont.instances:
			axLoc = thisInstance.customParameters["Axis Location"]
			if axLoc and len(axLoc) < len(thisFont.axes):
				axLoc = list(axLoc)
				axLoc.append(
					{
						"Axis": self.pref("axisName"),
						"Location": thisInstance.axisValueValueForId_(gradeAxis.id),
					}
				)
				thisInstance.customParameters["Axis Location"] = axLoc
				# Glyphs 4:
				# thisMaster.setExternAxisValueValue_forId_(thisMaster.axisValueValueForId_(gradeID), gradeID)
				# thisMaster.externalAxesValues[gradeID] = thisMaster.internalAxesValues[gradeID]

		# update Axis Locations in Virtual Masters if there are any:
		for parameter in thisFont.customParameters:
			if parameter.name == "Virtual Master":
				print("Updating Virtual Master...")
				axLoc = parameter.value
				if len(axLoc) < len(thisFont.axes):
					axLoc.append(
						{
							"Axis": self.pref("axisName"),
							"Location": 0,
						}
					)
				parameter.value = axLoc

	def processCodeLine(self, codeLine, thisFont, grade, gradeAxisIdx, metricsKeyChoice, searchFor, replaceWith, keepCenteredGlyphsCentered, keepCenteredThreshold, gradeCount):
		if "#" in codeLine:
			codeLine = codeLine[: codeLine.find("#")]
		codeLine = codeLine.strip()
		if not codeLine:
			return

		masterName, axes = codeLine.split(":")
		masterName = masterName.strip()
		master = thisFont.fontMasterForName_(masterName)
		if not master:
			print(f"⚠️ No master called ‘{masterName}’")
			return

		if self.shouldExcludeMaster(master):
			return

		weightedAxes = master.axes[:]
		axisCodes = [a.strip() for a in axes.split(",") if "=" in a]
		if not axisCodes:
			print(f"⚠️ Could not parse: {codeLine}\n")
			return

		gradeCount += 1
		print(f"{gradeCount}. {codeLine}")
		for axisCode in axisCodes:
			if "+=" in axisCode:
				axisTag, value = axisCode.split("+=")
				valueFactor = 1
			elif "-=" in axisCode:
				axisTag, value = axisCode.split("-=")
				valueFactor = -1
			else:
				axisTag, value = axisCode.split("=")
				valueFactor = 0
			axisIdx = axisIndexForTag(thisFont, tag=axisTag.strip())
			value = int(value.strip())

			if valueFactor == 0:
				weightedAxes[axisIdx] = value
			else:
				weightedAxes[axisIdx] = (weightedAxes[axisIdx] + value * valueFactor)

		# weighted instance/font: the shapes
		weightedInstance = GSInstance()
		weightedInstance.font = thisFont
		weightedInstance.name = "###DELETEME###"
		weightedInstance.axes = weightedAxes
		self.cleanInterpolationDict(weightedInstance)
		print(f"🛠️ Interpolating grade: {self.masterAxesString(weightedInstance)}")
		weightedFont = weightedInstance.interpolatedFont

		# add the graded master
		gradeMaster = copy(master)
		if searchFor and replaceWith:
			gradeMaster.name = master.name.replace(searchFor, replaceWith)
		elif replaceWith:
			gradeMaster.name = master.name + replaceWith
		else:
			gradeMaster.name = f"{master.name} Grade {grade}"
		gradeMaster.font = thisFont
		gradeAxes = list(master.axes)
		gradeAxes[gradeAxisID] = grade
		gradeMaster.axes = gradeAxes
		if self.pref("addSyncMetricCustomParameter"):
			gradeMaster.customParameters.append(
				GSCustomParameter(
					"Link Metrics With Master",
					master.id,
				)
			)

		for m in thisFont.masters[::-1]:
			if m.axes == gradeMaster.axes:
				# remove preexisting graded masters if there are any
				print(f"❌ Removing preexisting graded master ‘{m.name}’")
				thisFont.removeFontMaster_(m)

		# otherwise add the one we built above:
		print(f"Ⓜ️ Adding master: ‘{gradeMaster.name}’")
		thisFont.masters.append(gradeMaster)

		# add interpolated content to new (graded) layer of each glyph:
		for baseGlyph in thisFont.glyphs:
			self.addGradeLayers(metricsKeyChoice, master, weightedInstance, weightedFont, gradeMaster, baseGlyph)

		# recenter centered glyphs
		# (in separate loop so we have all component references up to date from the previous loop)
		if keepCenteredGlyphsCentered and metricsKeyChoice not in (1, 2):
			print("↔️ Recentering centered glyphs...")
			for baseGlyph in thisFont.glyphs:
				baseLayer = baseGlyph.layers[master.id]
				if abs(baseLayer.LSB - baseLayer.RSB) <= keepCenteredThreshold:
					gradeLayer = baseGlyph.layers[gradeMaster.id]
					offCenter = gradeLayer.RSB - gradeLayer.LSB
					if abs(offCenter) > 1:
						gradeLayer.applyTransform((1, 0, 0, 1, offCenter // 2, 0))
		print()

	def addGradedBraceLayers(self, thisFont, gradeAxis, grade):
		if self.pref("addGradedBraceLayers"):
			print("\nGrading brace layers...")
			updateBraceLayers(thisFont, defaultValue=0, newAxisTag=gradeAxis.axisTag, newAxisValue=grade)
			glyphsWithBraceLayers = []
			for glyph in thisFont.glyphs:
				for layer in glyph.layers:
					if layer.isSpecialLayer and layer.attributes and "coordinates" in layer.attributes.keys():
						glyphsWithBraceLayers.append(glyph.name)
						break
			thisFont.newTab("/" + "/".join(glyphsWithBraceLayers))

	def BatchGraderMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(
					title="No Font Open",
					message="The script requires a font. Open a font and run the script again.",
					OKButton=None,
				)
				return

			filePath = thisFont.filepath
			if filePath:
				reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
			else:
				reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
			print(f"Batch Grader Report for {reportName}")
			print()

			# store original font type:
			originalFontType = thisFont.fontType()
			if self.pref("temporarilySwitchToDefaultInterpolation"):
				thisFont.setFontType_(0)  # default font type

			gradeAxis = self.updateGradeAxis(thisFont)

			# avoid ‘Master is outside of the interpolation space’ error:
			updateBraceLayers(thisFont)
			print()

			gradeAxisIdx = axisIndexForTag(thisFont, gradeAxis.axisTag)

			# query more user choices:
			searchFor = self.pref("searchFor")
			replaceWith = self.pref("replaceWith")
			metricsKeyChoice = self.pref("metricsKeyChoice")
			keepCenteredGlyphsCentered = self.pref("keepCenteredGlyphsCentered")
			keepCenteredThreshold = self.prefInt("keepCenteredThreshold")
			grade = self.prefInt("grade")

			# parse code and step through masters:
			gradeCount = 0
			graderCode = self.pref("graderCode").strip()
			for codeLine in graderCode.splitlines():
				self.processCodeLine(codeLine, thisFont, grade, gradeAxisIdx, metricsKeyChoice, searchFor, replaceWith, keepCenteredGlyphsCentered, keepCenteredThreshold, gradeCount)

			# add missing axis locations if base master has axis locations:
			self.addMissingAxisLocations(thisFont, gradeAxis)

			self.addGradedBraceLayers(thisFont, gradeAxis, grade)

			if self.pref("temporarilySwitchToDefaultInterpolation"):
				thisFont.setFontType_(originalFontType)  # return to original font type

			if originalFontType != 0:
				print("⚠️ Font Info > Other > Font Type is not ‘Default’.")

			thisFont.didChangeValueForKey_("fontMasters")
			self.w.close()  # delete if you want window to stay open
			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Batch Grader Error: {e}")
			import traceback

			print(traceback.format_exc())


BatchGrader()
