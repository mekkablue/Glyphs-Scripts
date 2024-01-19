# MenuTitle: Steal Metrics
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Copy sidebearings, widths and/or metric keys (both on layer and glyph) from one font master to another.
"""

import vanilla
import traceback
from GlyphsApp import Glyphs
from mekkablue import mekkaObject
from mekkablue.geometry import transform


class MetricsCopy(mekkaObject):
	"""GUI for copying glyph metrics from one font to another"""
	prefDict = {
		"ignoreSuffixes": 0,
		"suffixToBeIgnored": ".alt",
		"lsb": 0,
		"rsb": 0,
		"width": 0,
		"preferMetricKeys": 0,
		"onlyMetricsKeys": 0,
		"updateMetrics": 1,
	}

	def __init__(self):
		self.listOfMasters = []
		self.updateListOfMasters()

		# Window 'self.w':
		windowWidth = 400
		windowHeight = 250
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Steal Metrics",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), u"Open two fonts and select glyphs in the target font.", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.text_anchor = vanilla.TextBox((inset, linePos + 2, 130, 17), "Transfer metrics from:", sizeStyle='small')
		self.w.from_font = vanilla.PopUpButton((inset + 130, linePos, -inset, 17), self.listOfMasterNames(), sizeStyle='small', callback=self.buttonCheck)

		linePos += lineHeight
		self.w.text_value = vanilla.TextBox((inset, linePos + 2, 130, 17), "To selected glyphs in:", sizeStyle='small')
		self.w.to_font = vanilla.PopUpButton((inset + 130, linePos, -inset, 17), self.listOfMasterNames()[::-1], sizeStyle='small', callback=self.buttonCheck)

		linePos += lineHeight
		self.w.lsb = vanilla.CheckBox((inset, linePos - 1, 80, 20), "LSB", value=True, callback=self.buttonCheck, sizeStyle='small')
		self.w.rsb = vanilla.CheckBox((inset + 80, linePos - 1, 80, 20), "RSB", value=True, callback=self.buttonCheck, sizeStyle='small')
		self.w.width = vanilla.CheckBox((inset + 80 * 2, linePos - 1, 80, 20), "Width", value=False, callback=self.buttonCheck, sizeStyle='small')
		self.w.lsb.getNSButton().setToolTip_("If enabled, will transfer values for left sidebearings.")
		self.w.rsb.getNSButton().setToolTip_("If enabled, will transfer values for right sidebearings.")
		self.w.width.getNSButton().setToolTip_("If enabled, will transfer values for advance widths.")

		linePos += lineHeight
		self.w.updateMetrics = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Update Metrics in Source Font", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.updateMetrics.getNSButton().setToolTip_("Updates metrics in the source layer before transfering the values to the target font. Recommended. (Also circumvents an issue in Glyphs 3 where metrics would not get transfered.)")

		linePos += lineHeight
		self.w.preferMetricKeys = vanilla.CheckBox((inset, linePos, -inset, 20), "Prefer (glyph and layer) metrics keys whenever available", value=False, sizeStyle='small', callback=self.buttonCheck)
		self.w.preferMetricKeys.getNSButton().setToolTip_("If enabled, will transfer the metrics key rather than the metric value, if a metrics key is persent in the source font.")

		linePos += lineHeight
		self.w.onlyMetricsKeys = vanilla.CheckBox((inset * 2, linePos - 1, -inset, 20), u"Only transfer metrics keys (ignore LSB, RSB, Width)", value=False, callback=self.buttonCheck, sizeStyle='small')
		self.w.onlyMetricsKeys.enable(False)
		self.w.onlyMetricsKeys.getNSButton().setToolTip_("If enabled, will only transfer metrics keys and not change any metric values. The checkboxes for LSB, RSB and Width will be disabled.")

		linePos += lineHeight
		self.w.ignoreSuffixes = vanilla.CheckBox((inset, linePos, 190, 20), "Ignore dotsuffix in source glyph:", value=False, sizeStyle='small', callback=self.buttonCheck)
		self.w.suffixToBeIgnored = vanilla.EditText((inset + 190, linePos, -inset, 20), ".alt", sizeStyle='small')
		self.w.suffixToBeIgnored.getNSTextField(
		).setToolTip_(u"Will copy metrics from source glyph ‘eacute’ to target glyph ‘eacute.xxx’. Useful for transfering metrics to dotsuffixed glyph variants.")

		self.w.copybutton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Transfer", sizeStyle='regular', callback=self.copyMetrics)
		self.w.setDefaultButton(self.w.copybutton)

		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()

		self.buttonCheck(None)

	def updateListOfMasters(self):
		try:
			masterList = []

			for thisFont in Glyphs.fonts:
				for thisMaster in thisFont.masters:
					masterList.append(thisMaster)

			masterList.reverse()  # so index accessing works as expected, and the default is: current font = target
			self.listOfMasters = masterList
		except:
			print(traceback.format_exc())

	def listOfMasterNames(self):
		try:
			myMasterNameList = ["%i: %s - %s" % (i + 1, self.listOfMasters[i].font.familyName, self.listOfMasters[i].name) for i in range(len(self.listOfMasters))]
			return myMasterNameList
		except:
			print(traceback.format_exc())

	def outputError(self, errMsg):
		print("Steal Sidebearings Warning:", errMsg)

	def buttonCheck(self, sender):
		try:
			# check if both font selection point to the same font
			# and disable action button if they do:
			fromFont = self.w.from_font.getItems()[self.w.from_font.get()]
			toFont = self.w.to_font.getItems()[self.w.to_font.get()]

			if fromFont == toFont:
				self.w.copybutton.enable(onOff=False)
			else:
				self.w.copybutton.enable(onOff=True)

			# check if checkbox is enabled
			# and sync availability of text box
			suffixCheckBoxChecked = self.w.ignoreSuffixes.get()
			if suffixCheckBoxChecked:
				self.w.suffixToBeIgnored.enable(onOff=True)
			else:
				self.w.suffixToBeIgnored.enable(onOff=False)

			# All of LSB, RSB and Width must not be on at the same time:
			if self.w.rsb.get() and self.w.lsb.get() and self.w.width.get():
				if sender == self.w.rsb:
					self.w.width.set(False)
				else:
					self.w.rsb.set(False)

			# enable Only Keys option only if
			if not self.w.preferMetricKeys.get():
				self.w.onlyMetricsKeys.set(False)

			self.w.onlyMetricsKeys.enable(bool(self.w.preferMetricKeys.get()))
			metricValuesOnOff = not self.w.onlyMetricsKeys.get()
			self.w.lsb.enable(metricValuesOnOff)
			self.w.rsb.enable(metricValuesOnOff)
			self.w.width.enable(metricValuesOnOff)

			self.SavePreferences()
		except:
			print(traceback.format_exc())

	def copyMetrics(self, sender):
		self.SavePreferences()

		preferMetricKeys = self.pref("preferMetricKeys")
		onlyMetricsKeys = self.pref("onlyMetricsKeys")
		fromFontIndex = self.w.from_font.get()
		toFontIndex = self.w.to_font.get() * -1 - 1
		sourceMaster = self.listOfMasters[fromFontIndex]
		targetMaster = self.listOfMasters[toFontIndex]
		sourceMasterID = sourceMaster.id
		targetMasterID = targetMaster.id
		sourceFont = sourceMaster.font
		targetFont = targetMaster.font
		ignoreSuffixes = self.pref("ignoreSuffixes")
		lsbIsSet = self.pref("lsb")
		rsbIsSet = self.pref("rsb")
		widthIsSet = self.pref("width")
		updateMetrics = self.pref("updateMetrics")
		suffixToBeIgnored = self.w.suffixToBeIgnored.get().strip(".")
		selectedTargetLayers = targetFont.selectedLayers

		countTargetLayers = len(selectedTargetLayers) if selectedTargetLayers else 0
		print(
			"Transfering %i glyph metric%s from %s %s to %s %s:" % (
				countTargetLayers,
				"s" if abs(countTargetLayers) != 1 else "",
				sourceFont.familyName,
				sourceMaster.name,
				targetFont.familyName,
				targetMaster.name,
			)
		)

		targetLayers = [targetFont.glyphs[layer.parent.name].layers[targetMasterID] for layer in selectedTargetLayers]
		for targetLayer in targetLayers:
			try:
				targetGlyph = targetLayer.parent
				targetGlyphName = targetGlyph.name
				sourceGlyphName = targetGlyphName

				if ignoreSuffixes:
					# replace suffix in the middle of the name:
					sourceGlyphName = targetGlyphName.replace(".%s." % suffixToBeIgnored, ".")
					# replace suffix at the end of the name:
					if sourceGlyphName.endswith(".%s" % suffixToBeIgnored):
						sourceGlyphName = sourceGlyphName[:-len(suffixToBeIgnored) - 1]

				sourceGlyph = sourceFont.glyphs[sourceGlyphName]
				if not sourceGlyph:
					print("     %s: not found in source font" % sourceGlyphName)
				else:
					sourceLayer = sourceGlyph.layers[sourceMasterID]
					if updateMetrics:
						sourceLayer.updateMetrics()

					# go through metrics keys:
					metricsL, metricsR, metricsW = False, False, False
					if preferMetricKeys:
						if sourceGlyph.leftMetricsKey:
							targetGlyph.leftMetricsKey = sourceGlyph.leftMetricsKey
							metricsL = True
							print("     %s, left glyph key: '%s'" % (targetGlyphName, targetGlyph.leftMetricsKey))
						if sourceGlyph.rightMetricsKey:
							targetGlyph.rightMetricsKey = sourceGlyph.rightMetricsKey
							metricsR = True
							print("     %s, right glyph key: '%s'" % (targetGlyphName, targetGlyph.rightMetricsKey))
						if sourceGlyph.widthMetricsKey:
							targetGlyph.widthMetricsKey = sourceGlyph.widthMetricsKey
							metricsW = True
							print("     %s, width glyph key: '%s'" % (targetGlyphName, targetGlyph.widthMetricsKey))
						if sourceLayer.leftMetricsKey:
							targetLayer.leftMetricsKey = sourceLayer.leftMetricsKey
							metricsL = True
							print("     %s, left layer key: '%s'" % (targetGlyphName, targetLayer.leftMetricsKey))
						if sourceLayer.rightMetricsKey:
							targetLayer.rightMetricsKey = sourceLayer.rightMetricsKey
							metricsR = True
							print("     %s, right layer key: '%s'" % (targetGlyphName, targetLayer.rightMetricsKey))
						if sourceLayer.widthMetricsKey:
							targetLayer.widthMetricsKey = sourceLayer.widthMetricsKey
							metricsW = True
							print("     %s, width layer key: '%s'" % (targetGlyphName, targetLayer.widthMetricsKey))

					if not onlyMetricsKeys:
						# transfer numeric metrics:
						if lsbIsSet and not metricsL:
							targetLayer.LSB = sourceLayer.LSB
						if widthIsSet and not metricsW:
							targetLayer.width = sourceLayer.width
							if rsbIsSet and not metricsR:  # set width AND rsb, i.e. adjust lsb:
								shift = targetLayer.RSB - sourceLayer.RSB
								shiftTransform = transform(shiftX=shift)
								targetLayer.transform_checkForSelection_doComponents_(shiftTransform, False, True)
						elif rsbIsSet and not metricsR:
							targetLayer.RSB = sourceLayer.RSB

						# update metrics:
						syncMessage = ""
						if metricsL or metricsR or metricsW:
							targetLayer.updateMetrics()
							targetLayer.syncMetrics()
							syncMessage = ", synced metric keys"

						# report in macro window
						print("     %s: L %i, R %i, W %i%s" % (
							targetGlyphName,
							targetLayer.LSB,
							targetLayer.RSB,
							targetLayer.width,
							syncMessage,
						))

			except Exception as e:
				self.outputError(e)
				print(traceback.format_exc())

		# update metrics keys:
		if preferMetricKeys:
			for targetLayer in targetLayers:
				targetLayer.updateMetrics()


MetricsCopy()
