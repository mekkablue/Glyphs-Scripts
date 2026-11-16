# MenuTitle: Fix Math Operator Spacing
__doc__ = """
Syncs widths and centers glyphs for +−×÷=≠±≈¬, optionally also Less/greater symbols and asciicircum/asciitilde.
"""

import math

import vanilla
from AppKit import NSAffineTransform, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSMidY, NSTextAlignmentRight
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject

mathOperators = "+−×÷=≠±≈¬"
lessGreater = "><≥≤"
asciiOperators = "~^"
heightSyncOperators = "+−×÷=≠≈~"


def isBracketLayer(layer):
	# WORKAROUND (Glyphs 4.0): isBracketLayer is a property in Glyphs 4, but was a method in Glyphs 3
	if Glyphs.versionNumber >= 4:
		return layer.isBracketLayer
	elif Glyphs.versionNumber >= 3:
		return layer.isBracketLayer()
	return "[" in layer.name and "]" in layer.name


def isBraceLayer(layer):
	# WORKAROUND (Glyphs 4.0): isBraceLayer is a property in Glyphs 4, but was a method in Glyphs 3
	if Glyphs.versionNumber >= 4:
		return layer.isBraceLayer
	elif Glyphs.versionNumber >= 3:
		return layer.isBraceLayer()
	return "{" in layer.name and "}" in layer.name


def italicize(y, italicAngle=0.0, pivotalY=0.0):
	yOffset = y - pivotalY  # calculate vertical offset
	italicAngle = math.radians(italicAngle)  # convert to radians
	tangens = math.tan(italicAngle)  # math.tan needs radians
	horizontalDeviance = tangens * yOffset  # vertical distance from pivotal point
	return horizontalDeviance  # x for yOffset from pivotal point


class FixMathOperatorSpacing(mekkaObject):
	prefDict = {
		"referenceOperator": 0,
		"suffix": "",
		"SyncWidths": 0,
		"centerMathOperators": 0,
		"metricKeysForMathOperators": 0,
		"syncWidthsLessGreater": 0,
		"SyncWidthsAscii": 0,
		"lessGreaterRadioButtons": 0,
		"lessGreaterMetricReference": 0,
		"syncWidthOfLessGreaterReference": 0,
		"ignoreAutoAligned": 0,
		"deleteLayerMetricsKeys": 0,
		"syncHeights": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Fix Math Operator Spacing",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.decriptionText = vanilla.TextBox("auto", "Sync widths between math operators", sizeStyle='small')

		# MATH OPERATORS:

		suffixTooltip = "Script only applies operators and reference glyphs that have this dot suffix. Enter with or without dot. Leave blank for default operators."
		self.w.suffixText = vanilla.TextBox("auto", "With suffix", sizeStyle='small')
		self.w.suffixText.setToolTip(suffixTooltip)
		self.w.suffix = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle='small')
		self.w.suffix.setToolTip(suffixTooltip)

		referenceTooltip = "The glyph that is used for the reference width and for the metrics keys. And for vertical centering if the option is chosen."
		self.w.referenceOperatorText = vanilla.TextBox("auto", "Reference glyph", sizeStyle='small')
		self.w.referenceOperatorText.setToolTip(referenceTooltip)
		self.w.referenceOperator = vanilla.PopUpButton("auto", ["%s %s" % (c, Glyphs.niceGlyphName(c)) for c in mathOperators + lessGreater + asciiOperators], sizeStyle='small', callback=self.SavePreferences)
		self.w.referenceOperator.setToolTip(referenceTooltip)

		self.w.SyncWidths = vanilla.CheckBox("auto", "Sync widths of: %s" % mathOperators, value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.SyncWidths.setToolTip("Syncs the width of the math operators with the reference glyph.")

		self.w.centerMathOperators = vanilla.CheckBox("auto", "Center shapes for: %s" % mathOperators, value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.centerMathOperators.setToolTip("Centers the shape of the operator glyph in its width.")

		self.w.metricKeysForMathOperators = vanilla.CheckBox("auto", "Set width metrics key", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.metricKeysForMathOperators.setToolTip("Also applies metrics keys for the width, so you can update later with Glyph > Update Metrics.")

		# LESS AND GREATER:

		self.w.syncWidthsLessGreater = vanilla.CheckBox("auto", "Sync widths of: %s" % lessGreater, value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.syncWidthsLessGreater.setToolTip("Also syncs widths of less, greater, lessequal and greaterequal.")

		radioOptions = (
			"Same options as above",
			"Same options as above, but no centering",
			"Metrics keys based on",
		)
		self.w.lessGreaterRadioButtons = vanilla.VerticalRadioGroup("auto", radioOptions, callback=self.SavePreferences, sizeStyle='small')
		self.w.lessGreaterRadioButtons.set(0)

		self.w.lessGreaterMetricReference = vanilla.PopUpButton("auto", ["%s %s" % (c, Glyphs.niceGlyphName(c)) for c in lessGreater + mathOperators + asciiOperators], sizeStyle='small', callback=self.SavePreferences)
		self.w.lessGreaterMetricReference.setToolTip("Override the reference glyph for <>≤≥. Useful if you do not want to center <>≤≥.")

		self.w.syncWidthOfLessGreaterReference = vanilla.CheckBox("auto", "Sync width of this reference glyph", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.syncHeights = vanilla.CheckBox("auto", "Vertically center: %s" % heightSyncOperators, value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.syncHeights.setToolTip("Syncs the vertical center of the math operators with the reference glyph.")

		# ASCII OPERATORS:
		self.w.SyncWidthsAscii = vanilla.CheckBox("auto", "Sync widths of: %s" % asciiOperators, value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.SyncWidthsAscii.setToolTip("Syncs widths of asciicircum and asciitilde, with the same options as for the main math operators.")

		self.w.ignoreAutoAligned = vanilla.CheckBox("auto", "Ignore auto-aligned composites", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreAutoAligned.setToolTip("Skips centering and metrics keys for layers that are built from components and are auto-aligned.")

		self.w.deleteLayerMetricsKeys = vanilla.CheckBox("auto", "Reset layer metrics keys", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.deleteLayerMetricsKeys.setToolTip("In glyphs that receive new metric keys, delete all layer-specific metric keys (e.g., ‘==100’).")

		# Buttons:
		self.w.tabButton = vanilla.Button("auto", "Open Tab", callback=self.OpenTab)
		self.w.tabButton.setToolTip("Opens a new Edit tab with +−×÷=≠±≈¬ <>≤≥ ^~")

		self.w.runButton = vanilla.Button("auto", "Sync", callback=self.FixMathOperatorSpacingMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes and the radio group stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels: right-aligned, one shared width
		labelNames = ("suffixText", "referenceOperatorText")
		widestLabel = "referenceOperatorText"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[decriptionText]-inset-|",
				"H:|-inset-[suffixText]-gap-[suffix]-inset-|",
				"H:|-inset-[referenceOperatorText]-gap-[referenceOperator]-inset-|",
				"H:|-inset-[SyncWidths]-(>=inset)-|",
				"H:|-indent-[centerMathOperators]-(>=inset)-|",
				"H:|-indent-[metricKeysForMathOperators]-(>=inset)-|",
				"H:|-inset-[syncWidthsLessGreater]-(>=inset)-|",
				"H:|-indent-[lessGreaterRadioButtons]-(>=inset)-|",
				"H:[lessGreaterMetricReference(>=100)]-inset-|",
				"H:|-indentRadio-[syncWidthOfLessGreaterReference]-(>=inset)-|",
				"H:|-inset-[syncHeights]-(>=inset)-|",
				"H:|-inset-[SyncWidthsAscii]-(>=inset)-|",
				"H:|-inset-[ignoreAutoAligned]-(>=inset)-|",
				"H:|-inset-[deleteLayerMetricsKeys]-(>=inset)-|",
				"H:|-(>=inset)-[tabButton(>=80)]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[decriptionText]-headlineGap-[suffix]-row-[referenceOperator]-headlineGap-[SyncWidths]-checkRow-[centerMathOperators]-checkRow-[metricKeysForMathOperators]-checkRow-[syncWidthsLessGreater]-checkRow-[lessGreaterRadioButtons]-checkRow-[syncWidthOfLessGreaterReference]-checkRow-[syncHeights]-checkRow-[SyncWidthsAscii]-checkRow-[ignoreAutoAligned]-checkRow-[deleteLayerMetricsKeys]-inset-[runButton]-inset-|",
				"V:[tabButton]-inset-|",
				{"view1": self.w.suffixText, "attribute1": "centerY", "view2": self.w.suffix, "attribute2": "centerY"},
				{"view1": self.w.referenceOperatorText, "attribute1": "centerY", "view2": self.w.referenceOperator, "attribute2": "centerY"},
				# the popup sits on the third radio button, which is the last row of the group:
				{"view1": self.w.lessGreaterMetricReference, "attribute1": "bottom", "view2": self.w.lessGreaterRadioButtons, "attribute2": "bottom", "constant": 2},
				{"view1": self.w.lessGreaterMetricReference, "attribute1": "left", "view2": self.w.lessGreaterRadioButtons, "attribute2": "left", "constant": 150},
			] + widthRules,
			metrics={"inset": inset, "indent": inset + 18, "indentRadio": inset + 36, "gap": 8, "row": 6, "headlineGap": 10, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		enteredSuffix = self.suffixWithDot(self.w.suffix.get().strip())

		referenceOperator = self.w.referenceOperator.getTitle().split()[-1]
		title = "Set metrics key for width: ‘=%s’" % (referenceOperator + enteredSuffix)
		self.w.metricKeysForMathOperators.setTitle(title)

		lessGreaterReferenceOperator = self.w.lessGreaterMetricReference.getTitle().split()[-1]
		title = "Set width key for %s: ‘=%s’" % (lessGreaterReferenceOperator + enteredSuffix, referenceOperator + enteredSuffix)
		self.w.syncWidthOfLessGreaterReference.setTitle(title)

		onOff = self.w.SyncWidths.get()
		self.w.centerMathOperators.enable(onOff)
		self.w.metricKeysForMathOperators.enable(onOff)

		onOff = self.w.syncWidthsLessGreater.get()
		self.w.lessGreaterRadioButtons.enable(onOff)
		self.w.lessGreaterMetricReference.enable(onOff)
		self.w.syncWidthOfLessGreaterReference.enable(onOff)

	def OpenTab(self, sender):
		# update prefs:
		self.SavePreferences(sender)

		# all operators
		tabText = "+−×÷=≠±≈¬\n<>≤≥\n^~"
		suffix = self.suffixWithDot(self.pref("suffix"))

		# opens new Edit tab:
		thisFont = Glyphs.font
		if thisFont:
			if suffix:
				escapedTabText = ""
				for tabLine in tabText.splitlines():
					for char in tabLine:
						escapedTabText += "/%s%s" % (Glyphs.niceGlyphName(char), suffix)
					escapedTabText += "\n"
				tabText = escapedTabText[:-1]
			thisFont.newTab(tabText)
		else:
			Message(title="No Font Error", message="Could not determine a frontmost font. Open a font and try again.", OKButton="😬 Oops")

	def suffixWithDot(self, suffix):
		if suffix:
			suffix = suffix.strip()
			if suffix and suffix[0] != ".":
				suffix = ".%s" % suffix
		else:
			suffix = ""
		return suffix

	def centerLayerInWidth(self, layer):
		oldWidth = layer.width
		newSB = (layer.LSB + layer.RSB) / 2
		layer.LSB = round(newSB)
		layer.width = oldWidth
		print("   ✅ Centered shape on layer: %s" % layer.name)

	def updateMetricKeys(self, layer):
		if self.pref("deleteLayerMetricsKeys"):
			layer.leftMetricsKey = None
			layer.rightMetricsKey = None
			layer.widthMetricsKey = None
		layer.updateMetrics()
		layer.syncMetrics()

	def warnAboutMissingGlyph(self, glyphName):
		print("❌ Warning: glyph %s is missing." % glyphName)
		# brings macro window to front:
		Glyphs.showMacroWindow()

	def warnAboutAutoAlignedLayer(self, layer):
		print("   ℹ️ Layer ‘%s’ is auto-aligned compound: skipping" % layer.name)

	def reportProcessing(self, glyphName):
		print("🔣 %s" % glyphName)

	def FixMathOperatorSpacingMain(self, sender):
		try:
			self.SavePreferences(None)  # get the current UI state (in case two windows are open)

			suffix = self.suffixWithDot(self.pref("suffix"))

			syncWidths = self.pref("SyncWidths")
			syncWidthsLessGreater = self.pref("syncWidthsLessGreater")
			syncWidthsAscii = self.pref("SyncWidthsAscii")
			syncHeights = self.pref("syncHeights")

			centerMathOperators = self.pref("centerMathOperators")
			metricKeysForMathOperators = self.pref("metricKeysForMathOperators")
			lessGreaterRadioButtons = self.prefInt("lessGreaterRadioButtons")
			lessGreaterMetricReferenceName = "%s%s" % (self.w.lessGreaterMetricReference.getTitle().split()[-1], suffix)
			syncWidthOfLessGreaterReference = self.pref("syncWidthOfLessGreaterReference")

			Glyphs.clearLog()
			thisFont = Glyphs.font  # frontmost font
			if not thisFont:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			print("Fixing Math Operator Spacing for %s" % thisFont.familyName)
			print(thisFont.filepath if thisFont.filepath else f"{thisFont.familyName} (unsaved)")
			print()

			referenceOperatorName = "%s%s" % (self.w.referenceOperator.getTitle().split()[-1], suffix)
			referenceOperatorGlyph = thisFont.glyphs[referenceOperatorName]
			if not referenceOperatorGlyph and (syncWidths or syncWidthsAscii or syncHeights or syncWidthsLessGreater):
				self.warnAboutMissingGlyph(referenceOperatorName)
				return

			# SYNC MATH AND ASCII OPERATORS
			charsToProcess = ""
			if syncWidthsAscii:
				charsToProcess += asciiOperators
			if syncWidths:
				charsToProcess += mathOperators
			if syncWidthOfLessGreaterReference and lessGreaterRadioButtons == 2 and syncWidthsLessGreater:
				charsToProcess += self.w.lessGreaterMetricReference.getTitle().split()[0]
			if charsToProcess:
				for mathOperatorChar in charsToProcess:
					mathOperatorGlyphName = "%s%s" % (Glyphs.niceGlyphName(mathOperatorChar), suffix)
					mathOperatorGlyph = thisFont.glyphs[mathOperatorGlyphName]
					if not mathOperatorGlyph:
						self.warnAboutMissingGlyph(mathOperatorGlyphName)
					else:
						self.reportProcessing(mathOperatorGlyphName)

						# add metrics keys if necessary
						if metricKeysForMathOperators:
							widthKey = "=%s" % referenceOperatorName
							mathOperatorGlyph.widthMetricsKey = widthKey
							mathOperatorGlyph.leftMetricsKey = None
							mathOperatorGlyph.rightMetricsKey = None
							print("   ✅ Set width metrics key: %s" % widthKey)

						for layer in mathOperatorGlyph.layers:
							if layer.isAligned:
								self.warnAboutAutoAlignedLayer(layer)
							else:
								# check if layer is relevant in the first place:
								master = layer.associatedFontMaster()
								isMasterLayer = layer.layerId == master.id
								if isMasterLayer or isBraceLayer(layer) or isBracketLayer(layer):
									referenceLayer = referenceOperatorGlyph.layers[master.id]

									# sync width with reference glyph (only for other glyphs):
									if mathOperatorGlyph != referenceOperatorGlyph:

										# update width
										layer.width = referenceLayer.width

										# update metrics keys if necessary
										if metricKeysForMathOperators:
											self.updateMetricKeys(layer)

									# center shape (also for reference glyph):
									if centerMathOperators and mathOperatorGlyphName != lessGreaterMetricReferenceName:
										self.centerLayerInWidth(layer)
										# add metricskey if necessary:
										# if metricKeysForMathOperators:
										# 	mathOperatorGlyph.rightMetricsKey = "=|"
										# update metrics:
										# layer.updateMetrics()
										# layer.syncMetrics()

			# center +−×÷=≠≈~
			if syncHeights:
				for mathOperatorChar in heightSyncOperators:
					mathOperatorGlyphName = "%s%s" % (Glyphs.niceGlyphName(mathOperatorChar), suffix)
					mathOperatorGlyph = thisFont.glyphs[mathOperatorGlyphName]
					if not mathOperatorGlyph:
						self.warnAboutMissingGlyph(mathOperatorGlyphName)
					else:
						self.reportProcessing(mathOperatorGlyphName)
						for layer in mathOperatorGlyph.layers:
							if layer.isAligned:
								self.warnAboutAutoAlignedLayer(layer)
							else:
								# check if layer is relevant in the first place:
								master = layer.associatedFontMaster()
								isMasterLayer = layer.layerId == master.id
								if isMasterLayer or isBraceLayer(layer) or isBracketLayer(layer):
									referenceLayer = referenceOperatorGlyph.layers[master.id]

									# sync height with reference glyph:
									if mathOperatorGlyph != referenceOperatorGlyph:
										yOffset = NSMidY(referenceLayer.bounds) - NSMidY(layer.bounds)
										if abs(yOffset) > 1.0:
											xOffset = italicize(yOffset, master.italicAngle)
											shiftTransform = NSAffineTransform.transform()
											shiftTransform.translateXBy_yBy_(xOffset, yOffset)
											layer.applyTransform(shiftTransform.transformStruct())

			# SYNC LESS/GREATER:
			if syncWidthsLessGreater:

				# overwrite options:
				if lessGreaterRadioButtons > 0:
					centerMathOperators = False
				if lessGreaterRadioButtons == 2:
					referenceOperatorName = lessGreaterMetricReferenceName
					referenceOperatorGlyph = thisFont.glyphs[referenceOperatorName]

				if not referenceOperatorGlyph:
					self.warnAboutMissingGlyph(referenceOperatorName)
				else:
					for lessGreaterChar in lessGreater:
						lessGreaterGlyphName = "%s%s" % (Glyphs.niceGlyphName(lessGreaterChar), suffix)
						lessGreaterGlyph = thisFont.glyphs[lessGreaterGlyphName]
						if not lessGreaterGlyph:
							self.warnAboutMissingGlyph(lessGreaterGlyphName)
						else:
							# do not process reference glyph twice:
							lessGreaterReferenceAlreadyProcessed = syncWidthOfLessGreaterReference and lessGreaterRadioButtons == 2 and syncWidthsLessGreater
							if not (lessGreaterGlyphName == referenceOperatorName and lessGreaterReferenceAlreadyProcessed):
								self.reportProcessing(lessGreaterGlyphName)

								# add metrics keys if necessary
								if metricKeysForMathOperators:
									widthKey = "=%s" % referenceOperatorName
									sbKey = widthKey

									notBothLess = "less" in referenceOperatorName and "less" not in lessGreaterGlyphName
									notBothGreater = "great" in referenceOperatorName and "great" not in lessGreaterGlyphName
									if notBothLess or notBothGreater:
										sbKey = "=|%s" % referenceOperatorName
										lessGreaterGlyph.rightMetricsKey = sbKey
										sb = "RSB"
									else:
										lessGreaterGlyph.leftMetricsKey = sbKey
										sb = "LSB"
									lessGreaterGlyph.widthMetricsKey = widthKey
									print("   ✅ Set keys for width: %s, %s: %s" % (widthKey, sb, sbKey))

								for layer in lessGreaterGlyph.layers:
									if layer.isAligned:
										self.warnAboutAutoAlignedLayer(layer)
									else:
										# check if layer is relevant in the first place:
										master = layer.associatedFontMaster()
										isMasterLayer = layer.layerId == master.id
										if isMasterLayer or isBraceLayer(layer) or isBracketLayer(layer):
											referenceLayer = referenceOperatorGlyph.layers[master.id]

											# sync width with reference glyph (only for other glyphs):
											if lessGreaterGlyph != referenceOperatorGlyph:

												# update width
												layer.width = referenceLayer.width

												# update metrics keys if necessary
												if metricKeysForMathOperators:
													self.updateMetricKeys(layer)

											# center shape (also for reference glyph):
											if centerMathOperators:
												self.centerLayerInWidth(layer)

												# add metricskey if necessary:
												# if metricKeysForMathOperators:
												# 	mathOperatorGlyph.rightMetricsKey = "=|"
												# update metrics:
												# layer.updateMetrics()
												# layer.syncMetrics()

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Fix Math Operator Spacing Error: %s" % e)
			import traceback
			print(traceback.format_exc())


FixMathOperatorSpacing()
