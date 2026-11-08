# MenuTitle: Straight Stem Cruncher
__doc__ = """
Measures in centers of straight segments, and reports deviations in stem thicknesses.
"""

import objc
import vanilla
from mekkablue import mekkaObject, UpdateButton
from GlyphsApp import Glyphs, GSAnnotation, PLUS, Message, distance, subtractPoints, scalePoint, addPoints
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from Foundation import NSNumberFormatter, NSPoint


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def pointDistance(p1, p2):
	stemThickness = ((p2.x - p1.x)**2.0 + (p2.y - p1.y)**2.0)**0.5
	return stemThickness


def middleBetweenTwoPoints(p1, p2):
	x = (p1.x + p2.x) * 0.5
	y = (p1.y + p2.y) * 0.5
	return NSPoint(x, y)


class StraightStemCruncher(mekkaObject):
	defaultExcludeList = ".sc, .c2sc, .smcp, .sups, .subs, .sinf, superior, inferior, .numr, .dnom"
	prefDict = {
		"stems": "80, 100",
		"deviationMin": 0.6,
		"deviationMax": 4.0,
		"checkSpecialLayers": 1,
		"selectedGlyphsOnly": 0,
		"includeNonExporting": 0,
		"openTab": 1,
		"includeCompounds": 0,
		"minimumSegmentLength": 200,
		"reportNonMeasurements": 0,
		"excludeGlyphs": 0,
		"excludeGlyphNames": defaultExcludeList,
		"checkVStems": 1,
		"checkHStems": 0,
		"checkDStems": 0,
		"markStems": 1,
		"reuseTab": 1,
	}

	marker = "➕"

	def __init__(self):
		# Window 'self.w':
		windowWidth = 390
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Straight Stem Cruncher",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "In current master, looks for stems close but not exactly at", sizeStyle="small", selectable=True)

		tooltipText = "Comma-separated list of stem sizes to look for. If the script finds stems deviating from these sizes, within the given min/max deviations, it will report them."
		self.w.stemsText = vanilla.TextBox("auto", "Stem Widths", sizeStyle="small", selectable=True)
		self.w.stems = vanilla.EditText("auto", "20, 30, 40", callback=self.SavePreferences, sizeStyle="small")
		self.w.stemsText.setToolTip(tooltipText)
		self.w.stems.setToolTip(tooltipText)
		self.w.stemUpdate = UpdateButton("auto", callback=self.update)
		self.w.stemUpdate.setToolTip("Populate the stems with the stems of the current master.")

		self.w.stemFindText = vanilla.TextBox("auto", "Find deviating stems, min/max", sizeStyle="small", selectable=True)
		self.w.deviationMin = vanilla.EditText("auto", "0.4", callback=self.SavePreferences, sizeStyle="small")
		self.w.deviationMin.setToolTip("Deviations up to this value will be tolerated. Half a unit is a good idea to avoid false positives from rounding errors.")
		self.w.deviationMax = vanilla.EditText("auto", "3.1", callback=self.SavePreferences, sizeStyle="small")
		self.w.deviationMax.setToolTip("Deviations up to this value will be reported. Do not exaggerate value, otherwise you get false positives from cases where the opposing segment is not the other side of the stem.")

		tooltipText = "Looks for straight-line segments with at least this length and measures from their center to the opposing segment. Half x-height is a good idea."
		self.w.minimumSegmentLengthText = vanilla.TextBox("auto", "Minimum segment length", sizeStyle="small", selectable=True)
		minimumSegmentLengthFormatter = NSNumberFormatter.alloc().init()
		minimumSegmentLengthFormatter.setAllowsFloats_(False)
		minimumSegmentLengthFormatter.setMinimum_(0)
		self.w.minimumSegmentLength = SteppingEditText("auto", "200", callback=self.SavePreferences, sizeStyle="small", formatter=minimumSegmentLengthFormatter)
		self.w.minimumSegmentLengthText.setToolTip(tooltipText)
		self.w.minimumSegmentLength.setToolTip(tooltipText)
		self.w.segmentLengthUpdate = UpdateButton("auto", callback=self.update)
		self.w.segmentLengthUpdate.setToolTip("Reset to 40% of x-height.")

		checkStemsTooltip = "Choose which stems to measure: any combination of these three options. At least one must be active to run the script."
		self.w.checkStemsText = vanilla.TextBox("auto", "Check stems", sizeStyle="small", selectable=True)
		self.w.checkVStems = vanilla.CheckBox("auto", "Vertical", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.checkHStems = vanilla.CheckBox("auto", "Horizontal", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.checkDStems = vanilla.CheckBox("auto", "Diagonal", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.checkStemsText.setToolTip(checkStemsTooltip)
		self.w.checkVStems.setToolTip(checkStemsTooltip)
		self.w.checkHStems.setToolTip(checkStemsTooltip)
		self.w.checkDStems.setToolTip(checkStemsTooltip)

		self.w.checkSpecialLayers = vanilla.CheckBox("auto", "Also check bracket layers", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.checkSpecialLayers.setToolTip("If checked, also measures on bracket layers. Otherwise only on master layers.")

		self.w.selectedGlyphsOnly = vanilla.CheckBox("auto", "Measure selected glyphs only (otherwise all glyphs in font)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.selectedGlyphsOnly.setToolTip("Uncheck for measuring complete font.")

		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeNonExporting.setToolTip("Usually not necessary because the algorithm decomposes and removes overlap first.")

		self.w.includeCompounds = vanilla.CheckBox("auto", "Include components", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeCompounds.setToolTip("If checked, also measures components (after decomposition and removing overlap). If unchecked, only measures outlines.")

		tooltipText = "Comma-separated list of glyph name parts (e.g., suffixes). Glyphs containing these will not be measured if checkbox is enabled."
		self.w.excludeGlyphs = vanilla.CheckBox("auto", "Exclude glyphs containing", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.excludeGlyphs.setToolTip(tooltipText)
		self.w.excludeGlyphNames = vanilla.EditText("auto", self.defaultExcludeList, callback=self.SavePreferences, sizeStyle="small")
		self.w.excludeGlyphNames.setToolTip(tooltipText)
		self.w.excludeGlyphNamesReset = UpdateButton("auto", callback=self.update)
		self.w.excludeGlyphNamesReset.setToolTip("Reset to: %s." % self.defaultExcludeList)

		self.w.markStems = vanilla.CheckBox("auto", "Mark affected stems with %s annotation" % self.marker, value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.markStems.setToolTip("If checked, will add a red-plus annotation at the center of the measurement. Will often add two of them because stem will be measured from both sides.\nCAREFUL: May delete existing plus annotations.")

		self.w.reportNonMeasurements = vanilla.CheckBox("auto", "Report layers without measurements", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.reportNonMeasurements.setToolTip("In Macro Window, report if a layer does not have any measurements. Most likely causes: no straight stems in the paths, or wrong path direction.")

		self.w.openTab = vanilla.CheckBox("auto", "Open tab with affected glyphs", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.openTab.setToolTip("If unchecked, will bring macro window with detailed report to front.")
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.setToolTip("If checked, will reuse the active tab if there is one, otherwise will open a new tab. If unchecked, will always open a new tab.")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		# Status message:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		# the status takes the leftover width, and a long message does not widen the window:
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Measure", callback=self.StraightStemCruncherMain)
		self.w.setDefaultButton(self.w.runButton)

		# labels in front of fields: right-aligned, one shared width
		labelNames = ("stemsText", "stemFindText", "minimumSegmentLengthText", "checkStemsText")
		widestLabel = "stemFindText"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		centerRules = [
			{"view1": getattr(self.w, firstName), "attribute1": "centerY", "view2": getattr(self.w, secondName), "attribute2": "centerY"}
			for firstName, secondName in (
				("stemsText", "stems"),
				("stemUpdate", "stems"),
				("stemFindText", "deviationMin"),
				("deviationMax", "deviationMin"),
				("minimumSegmentLengthText", "minimumSegmentLength"),
				("segmentLengthUpdate", "minimumSegmentLength"),
				("checkStemsText", "checkVStems"),
				("checkHStems", "checkVStems"),
				("checkDStems", "checkVStems"),
				("excludeGlyphs", "excludeGlyphNames"),
				("excludeGlyphNamesReset", "excludeGlyphNames"),
				("reuseTab", "openTab"),
				("status", "runButton"),
			)
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[stemsText]-gap-[stems]-gap-[stemUpdate(20)]-inset-|",
				"H:|-inset-[stemFindText]-gap-[deviationMin(50)]-gap-[deviationMax(50)]-(>=inset)-|",
				"H:|-inset-[minimumSegmentLengthText]-gap-[minimumSegmentLength(50)]-gap-[segmentLengthUpdate(20)]-(>=inset)-|",
				"H:|-inset-[checkStemsText]-gap-[checkVStems]-gap-[checkHStems]-gap-[checkDStems]-(>=inset)-|",
				"H:|-inset-[checkSpecialLayers]-(>=inset)-|",
				"H:|-inset-[selectedGlyphsOnly]-(>=inset)-|",
				"H:|-inset-[includeNonExporting]-(>=inset)-|",
				"H:|-inset-[includeCompounds]-(>=inset)-|",
				"H:|-inset-[excludeGlyphs]-gap-[excludeGlyphNames]-gap-[excludeGlyphNamesReset(20)]-inset-|",
				"H:|-inset-[markStems]-(>=inset)-|",
				"H:|-inset-[reportNonMeasurements]-(>=inset)-|",
				"H:|-inset-[openTab]-gap-[reuseTab]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-row-[stems]-row-[deviationMin]-row-[minimumSegmentLength]-row-[checkVStems]-checkRow-[checkSpecialLayers]-checkRow-[selectedGlyphsOnly]-checkRow-[includeNonExporting]-checkRow-[includeCompounds]-row-[excludeGlyphNames]-row-[markStems]-checkRow-[reportNonMeasurements]-checkRow-[openTab]-inset-[progress(16)]-row-[runButton]-inset-|",
			] + widthRules + centerRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.reuseTab.enable(self.w.openTab.get())

		buttonEnable = (
			self.pref("checkVStems") or self.pref("checkHStems")
			or self.pref("checkDStems")
		)
		self.w.runButton.enable(onOff=buttonEnable)

	def update(self, sender=None):
		if sender == self.w.segmentLengthUpdate:
			xHeight = Glyphs.font.selectedFontMaster.xHeight
			self.w.minimumSegmentLength.set("%i" % round(xHeight / 2.1, -1))

		elif sender == self.w.stemUpdate:
			thisFont = Glyphs.font
			if thisFont:
				master = thisFont.selectedFontMaster
				if master:

					if Glyphs.versionNumber >= 3:
						# Glyphs 3 code
						stems = [stem for stem in master.stems]
					else:
						stems = []
						# Glyphs 2 code
						for stemSet in (master.horizontalStems, master.verticalStems):
							if stemSet:
								for s in stemSet:
									stems.append(s)
					stems = sorted(set(stems))
					stemString = ", ".join([str(s) for s in stems])
					if stemString:
						self.w.stems.set(stemString)
					else:
						Message(title="Stem Error", message="No standard stems defined in the current master. Please add some in Font Info > Masters.", OKButton=None)

		elif sender == self.w.excludeGlyphNamesReset:
			self.w.excludeGlyphNames.set(self.defaultExcludeList)

		self.SavePreferences()

	def stemThicknessAtLine(self, layer, p1, p2, measureLength):
		h = p2.x - p1.x
		v = p2.y - p1.y
		length = (h**2 + v**2)**0.5

		hUnit = h / length
		vUnit = v / length

		h = hUnit * measureLength
		v = vUnit * measureLength

		measurePoint1 = middleBetweenTwoPoints(p1, p2)
		# print "  middle:", measurePoint1, hUnit, vUnit
		# measurePoint1.x += vUnit*2
		# measurePoint1.y -= hUnit*2

		measurePoint2 = NSPoint(measurePoint1.x - v, measurePoint1.y + h)
		intersections = layer.intersectionsBetweenPoints(measurePoint1, measurePoint2)

		if measurePoint1 != intersections[0]:
			intersections = intersections[::-1]

		if len(intersections) > 2:
			# two measurement points:
			p1 = NSPoint(intersections[0].x, intersections[0].y)
			p2 = NSPoint(intersections[1].x, intersections[1].y)

			# calculate stem width:
			stemWidth = distance(p1, p2)

			# calculate center of stem:
			vector = subtractPoints(p2, p1)
			scaledVector = scalePoint(vector, 0.5)
			centerOfStem = addPoints(p1, scaledVector)

			# return results:
			return stemWidth, centerOfStem
		else:
			return None

	def measureStraighStemsInLayer(self, layer, glyphName=""):
		try:
			minLength = self.prefInt("minimumSegmentLength")
		except:
			self.update(self.w.segmentLengthUpdate)
			minLength = self.prefInt("minimumSegmentLength")

		checkVStems = self.pref("checkVStems")
		checkHStems = self.pref("checkHStems")
		checkDStems = self.pref("checkDStems")

		centers = []
		measurements = []
		measureLayer = layer.copyDecomposedLayer()
		measureLayer.parent = layer.parent
		measureLayer.removeOverlap()

		for thisPath in measureLayer.paths:
			nodeCount = len(thisPath.nodes)
			if nodeCount > 2:
				for thisSegment in thisPath.segments:
					if len(thisSegment) == 2:
						p1 = thisSegment[0]
						p2 = thisSegment[1]

						isVertical = (p1.x == p2.x)
						isHorizontal = (p1.y == p2.y)
						check = False

						if isHorizontal and checkHStems:
							check = True

						elif isVertical and checkVStems:
							check = True

						elif checkDStems:
							check = True

						# if p1.x==p2.x or p1.y==p2.y or not self.pref("ignoreDiagonals"):
						if check:
							if pointDistance(p1, p2) >= minLength:
								measureLength = max(100.0, measureLayer.bounds.size.width + measureLayer.bounds.size.height)
								results = self.stemThicknessAtLine(measureLayer, p1, p2, measureLength)
								if results:
									measurement, centerOfStem = results
									measurements.append(measurement)
									centers.append(centerOfStem)
			else:
				print(u"⚠️ Found path with only %i point%s%s." % (
					nodeCount,
					"" if nodeCount == 1 else "s",
					" in %s" % glyphName if glyphName else "",
				))
		return measurements, centers

	def StraightStemCruncherMain(self, sender):
		try:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			print("Straight Stem Cruncher Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()

			self.w.progress.set(0)
			if self.pref("selectedGlyphsOnly"):
				glyphsToCheck = [layer.parent for layer in thisFont.selectedLayers]
			else:
				glyphsToCheck = thisFont.glyphs

			excludedGlyphNameParts = []
			if self.pref("excludeGlyphs"):
				enteredParts = [x.strip() for x in self.pref("excludeGlyphNames").split(",")]
				if enteredParts:
					excludedGlyphNameParts.extend(set(enteredParts))

			stems = self.pref("stems")  # "80, 100"
			stems = [float(s.strip()) for s in stems.split(",")]

			shouldMark = self.pref("markStems")
			deviationMin = self.prefFloat("deviationMin")  # 0.6
			deviationMax = self.prefFloat("deviationMax")  # 4.0

			affectedLayers = []
			for glyphIndex, thisGlyph in enumerate(glyphsToCheck):
				self.w.progress.set(100 * glyphIndex / len(thisFont.glyphs))

				# see if any exclusion applies:

				glyphNameIsExcluded = False
				for particle in excludedGlyphNameParts:
					if particle in thisGlyph.name:
						glyphNameIsExcluded = True
						break

				glyphExportsOrNonExportingIncluded = thisGlyph.export or self.pref("includeNonExporting")

				if glyphExportsOrNonExportingIncluded and not glyphNameIsExcluded:
					self.w.status.set("Processing: %s" % thisGlyph.name)
					for thisLayer in thisGlyph.layers:
						if thisLayer.master == thisFont.selectedFontMaster:
							if thisLayer.isMasterLayer or (thisLayer.isSpecialLayer and self.pref("checkSpecialLayers")):

								# clean previous markings:
								if shouldMark:
									for i in range(len(thisLayer.annotations) - 1, -1, -1):
										a = thisLayer.annotations[i]
										if a and a.text == self.marker:
											del (thisLayer.annotations[i])

								# decompose components if necessary:
								if self.pref("includeCompounds"):
									checkLayer = thisLayer.copyDecomposedLayer()
									checkLayer.parent = thisLayer.parent
								else:
									checkLayer = thisLayer.copy()
									checkLayer.parent = thisLayer.parent
									if Glyphs.versionNumber >= 3:
										# Glyphs 3 code

										for comp in checkLayer.components:

											del checkLayer.shapes[checkLayer.shapes.index(comp)]

									else:
										# Glyphs 2 code
										checkLayer.components = None

								# go on if there are any paths:
								if checkLayer.paths:
									checkLayer.removeOverlap()
									measurements, centers = self.measureStraighStemsInLayer(checkLayer, glyphName=thisGlyph.name)
									if not measurements:
										if self.pref("reportNonMeasurements"):
											print(u"⚠️ %s, layer '%s': no stem measurements. Wrong path direction or no line segments?" % (
												thisGlyph.name,
												thisLayer.name,
											))
									else:
										deviatingStems = []
										for i, measurement in enumerate(measurements):
											if measurement not in stems:
												for stem in stems:
													if stem - deviationMax < measurement < stem - deviationMin or stem + deviationMin < measurement < stem + deviationMax:
														deviatingStems.append(measurement)
														if shouldMark:
															centerOfStem = centers[i]
															marker = GSAnnotation()
															marker.position = centerOfStem
															marker.type = PLUS
															# marker.type = TEXT
															# marker.text = self.marker
															thisLayer.annotations.append(marker)

										if deviatingStems:
											print(
												u"❌ %s, layer '%s': found %i stem%s off: %s." % (
													thisGlyph.name,
													thisLayer.name,
													len(deviatingStems),
													"" if len(deviatingStems) == 1 else "s",
													", ".join(["%.1f" % s for s in deviatingStems]),
												)
											)
											if thisLayer not in affectedLayers:
												affectedLayers.append(thisLayer)

			self.w.progress.set(100)
			self.w.status.set("✅ Done.")

			if not affectedLayers:
				Message(title="No Deviances Found", message="No point distances deviating from supplied stem widths within the given limits.", OKButton=None)
			elif self.pref("openTab"):
				tab = thisFont.currentTab
				if not tab or not self.pref("reuseTab"):
					tab = thisFont.newTab()
				tab.layers = affectedLayers
			else:
				# brings macro window to front:
				Glyphs.showMacroWindow()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Straight Stem Cruncher Error: %s" % e)
			import traceback
			print(traceback.format_exc())


StraightStemCruncher()
