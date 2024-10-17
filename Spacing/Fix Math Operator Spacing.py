# MenuTitle: Fix Math Operator Spacing
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Syncs widths and centers glyphs for +−×÷=≠±≈¬, optionally also Less/greater symbols and asciicircum/asciitilde.
"""

import vanilla
import math
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject
from AppKit import NSMidY, NSAffineTransform

mathOperators = "+−×÷=≠±≈¬"
lessGreater = "><≥≤"
asciiOperators = "~^"
heightSyncOperators = "+−×÷=≠≈~"


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
		windowWidth = 305
		windowHeight = 394
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Fix Math Operator Spacing",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 23

		self.w.decriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Sync widths between math operators", sizeStyle='small')
		linePos += lineHeight

		# MATH OPERATORS:

		self.w.suffixText = vanilla.TextBox((inset, linePos + 2, 100, 14), "With suffix", sizeStyle='small')
		self.w.suffix = vanilla.EditText((inset + 92, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.suffix.getNSTextField(
		).setToolTip_("Script only applies operators and reference glyphs that have this dot suffix. Enter with or without dot. Leave blank for default operators.")
		linePos += lineHeight

		self.w.referenceOperatorText = vanilla.TextBox((inset, linePos + 2, 100, 14), "Reference glyph", sizeStyle='small')
		self.w.referenceOperator = vanilla.PopUpButton((inset + 92, linePos, -inset, 17), ["%s %s" % (c, Glyphs.niceGlyphName(c)) for c in mathOperators + lessGreater + asciiOperators], sizeStyle='small', callback=self.SavePreferences)
		self.w.referenceOperator.getNSPopUpButton().setToolTip_("The glyph that is used for the reference width and for the metrics keys. And for vertical centering if the option is chosen.")
		linePos += lineHeight

		self.w.SyncWidths = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Sync widths of: %s" % mathOperators, value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.SyncWidths.getNSButton().setToolTip_("Syncs the width of the math operators with the reference glyph.")
		linePos += lineHeight

		self.w.centerMathOperators = vanilla.CheckBox((inset * 2 + 3, linePos - 1, -inset, 20), "Center shapes for: %s" % mathOperators, value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.centerMathOperators.getNSButton().setToolTip_("Centers the shape of the operator glyph in its width.")
		linePos += lineHeight

		self.w.metricKeysForMathOperators = vanilla.CheckBox((inset * 2 + 3, linePos - 1, -inset, 20), "Set width metrics key", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.metricKeysForMathOperators.getNSButton().setToolTip_("Also applies metrics keys for the width, so you can update later with Glyph > Update Metrics.")
		linePos += lineHeight

		# LESS AND GREATER:

		self.w.syncWidthsLessGreater = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Sync widths of: %s" % lessGreater, value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.syncWidthsLessGreater.getNSButton().setToolTip_("Also syncs widths of less, greater, lessequal and greaterequal.")
		linePos += lineHeight

		radioOptions = (
			"Same options as above",
			"Same options as above, but no centering",
			"Metrics keys based on",
		)
		self.w.lessGreaterRadioButtons = vanilla.RadioGroup((inset * 2, linePos, -inset, (lineHeight - 2) * len(radioOptions)), radioOptions, callback=self.SavePreferences, sizeStyle='small')
		self.w.lessGreaterRadioButtons.set(0)
		linePos += (lineHeight - 2) * (len(radioOptions) - 1)

		self.w.lessGreaterMetricReference = vanilla.PopUpButton((inset + 155, linePos + 2, -inset, 17), ["%s %s" % (c, Glyphs.niceGlyphName(c)) for c in lessGreater + mathOperators + asciiOperators], sizeStyle='small', callback=self.SavePreferences)
		self.w.lessGreaterMetricReference.getNSPopUpButton().setToolTip_("Override the reference glyph for <>≤≥. Useful if you do not want to center <>≤≥.")
		linePos += lineHeight

		self.w.syncWidthOfLessGreaterReference = vanilla.CheckBox((inset * 3.5, linePos - 1, -inset, 20), "Sync width of this reference glyph", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.syncHeights = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Vertically center: %s" % heightSyncOperators, value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.syncHeights.getNSButton().setToolTip_("Syncs the vertical center of the math operators with the reference glyph.")
		linePos += lineHeight

		# ASCII OPERATORS:
		self.w.SyncWidthsAscii = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Sync widths of: %s" % asciiOperators, value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.SyncWidthsAscii.getNSButton().setToolTip_("Syncs widths of asciicircum and asciitilde, with the same options as for the main math operators.")
		linePos += lineHeight

		self.w.ignoreAutoAligned = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Ignore auto-aligned composites", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreAutoAligned.getNSButton().setToolTip_("Skips centering and metrics keys for layers that are built from components and are auto-aligned.")
		linePos += lineHeight

		self.w.deleteLayerMetricsKeys = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Reset layer metrics keys", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.deleteLayerMetricsKeys.getNSButton().setToolTip_("In glyphs that receive new metric keys, delete all layer-specific metric keys (e.g., ‘==100’).")
		linePos += lineHeight

		# Buttons:
		self.w.tabButton = vanilla.Button((-200 - inset, -20 - inset, -90 - inset, -inset), "Open Tab", callback=self.OpenTab)
		self.w.tabButton.getNSButton().setToolTip_("Opens a new Edit tab with +−×÷=≠±≈¬ <>≤≥ ^~")

		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Sync", callback=self.FixMathOperatorSpacingMain)
		self.w.setDefaultButton(self.w.runButton)

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
			print("Fixing Math Operator Spacing for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()

			referenceOperatorName = "%s%s" % (self.w.referenceOperator.getTitle().split()[-1], suffix)
			referenceOperatorGlyph = thisFont.glyphs[referenceOperatorName]

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
								if Glyphs.versionNumber >= 3:
									# GLYPHS 3
									isBracketLayer = layer.isBracketLayer()
									isBraceLayer = layer.isBraceLayer()
								else:
									# GLYPHS 2
									isBracketLayer = "[" in layer.name and "]" in layer.name
									isBraceLayer = "{" in layer.name and "}" in layer.name

								if isMasterLayer or isBraceLayer or isBracketLayer:
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
								if Glyphs.versionNumber >= 3:
									# GLYPHS 3
									isBracketLayer = layer.isBracketLayer()
									isBraceLayer = layer.isBraceLayer()
								else:
									# GLYPHS 2
									isBracketLayer = "[" in layer.name and "]" in layer.name
									isBraceLayer = "{" in layer.name and "}" in layer.name

								if isMasterLayer or isBraceLayer or isBracketLayer:
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
										isBracketLayer = "[" in layer.name and "]" in layer.name
										isBraceLayer = "{" in layer.name and "}" in layer.name
										if isMasterLayer or isBraceLayer or isBracketLayer:
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
