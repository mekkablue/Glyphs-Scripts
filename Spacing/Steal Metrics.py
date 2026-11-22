# MenuTitle: Steal Metrics
__doc__ = """
Copy sidebearings, widths and/or metric keys (both on layer and glyph) from one font master to another.
"""

import traceback

import vanilla
from AppKit import NSColor, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, makeWindowResizable
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
		if not Glyphs.fonts:
			Message(title="No Font Open", message="The script requires two open fonts (or two masters). Open them and run the script again.", OKButton=None)
			return

		self.listOfMasters = []
		self.updateListOfMasters()

		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Steal Metrics",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", u"Open two fonts and select glyphs in the target font.", sizeStyle='small', selectable=True)

		self.w.text_anchor = vanilla.TextBox("auto", "Transfer metrics from:", sizeStyle='small')
		self.w.from_font = vanilla.PopUpButton("auto", self.listOfMasterNames(), sizeStyle='small', callback=self.buttonCheck)
		tooltipText = "The font master the metrics are taken from."
		self.w.text_anchor.setToolTip(tooltipText)
		self.w.from_font.setToolTip(tooltipText)

		self.w.text_value = vanilla.TextBox("auto", "To selected glyphs in:", sizeStyle='small')
		self.w.to_font = vanilla.PopUpButton("auto", self.listOfMasterNames()[::-1], sizeStyle='small', callback=self.buttonCheck)
		tooltipText = "The font master that receives the metrics in its selected glyphs."
		self.w.text_value.setToolTip(tooltipText)
		self.w.to_font.setToolTip(tooltipText)

		self.w.lsb = vanilla.CheckBox("auto", "LSB", value=True, callback=self.buttonCheck, sizeStyle='small')
		self.w.rsb = vanilla.CheckBox("auto", "RSB", value=True, callback=self.buttonCheck, sizeStyle='small')
		self.w.width = vanilla.CheckBox("auto", "Width", value=False, callback=self.buttonCheck, sizeStyle='small')
		self.w.lsb.setToolTip("If enabled, will transfer values for left sidebearings.")
		self.w.rsb.setToolTip("If enabled, will transfer values for right sidebearings.")
		self.w.width.setToolTip("If enabled, will transfer values for advance widths.")

		self.w.updateMetrics = vanilla.CheckBox("auto", "Update Metrics in Source Font", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.updateMetrics.setToolTip("Updates metrics in the source layer before transfering the values to the target font. Recommended. (Also circumvents an issue in Glyphs 3 where metrics would not get transfered.)")

		self.w.preferMetricKeys = vanilla.CheckBox("auto", "Prefer (glyph and layer) metrics keys whenever available", value=False, sizeStyle='small', callback=self.buttonCheck)
		self.w.preferMetricKeys.setToolTip("If enabled, will transfer the metrics key rather than the metric value, if a metrics key is persent in the source font.")

		self.w.onlyMetricsKeys = vanilla.CheckBox("auto", u"Only transfer metrics keys (ignore LSB, RSB, Width)", value=False, callback=self.buttonCheck, sizeStyle='small')
		self.w.onlyMetricsKeys.enable(False)
		self.w.onlyMetricsKeys.setToolTip("If enabled, will only transfer metrics keys and not change any metric values. The checkboxes for LSB, RSB and Width will be disabled.")

		suffixTooltip = u"Will copy metrics from source glyph ‘eacute’ to target glyph ‘eacute.xxx’. Useful for transfering metrics to dotsuffixed glyph variants."
		self.w.ignoreSuffixes = vanilla.CheckBox("auto", "Ignore dotsuffix in source glyph:", value=False, sizeStyle='small', callback=self.buttonCheck)
		self.w.ignoreSuffixes.setToolTip(suffixTooltip)
		self.w.suffixToBeIgnored = vanilla.EditText("auto", ".alt", sizeStyle='small', callback=self.SavePreferences)
		self.w.suffixToBeIgnored.setToolTip(suffixTooltip)

		self.w.copybutton = vanilla.Button("auto", "Transfer", callback=self.copyMetrics)
		self.w.copybutton.setToolTip("Transfers the metrics to the selected glyphs in the target font.")
		self.w.setDefaultButton(self.w.copybutton)

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.copybutton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.copybutton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels: right-aligned, one shared width
		labelNames = ("text_anchor", "text_value")
		widestLabel = "text_anchor"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# the checkbox in front of the suffix field hugs its title, the field takes the rest:
		self.w.ignoreSuffixes.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.suffixToBeIgnored.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[text_anchor]-gap-[from_font]-inset-|",
				"H:|-inset-[text_value]-gap-[to_font]-inset-|",
				"H:|-inset-[lsb]-gap-[rsb]-gap-[width]-(>=inset)-|",
				"H:|-inset-[updateMetrics]-(>=inset)-|",
				"H:|-inset-[preferMetricKeys]-(>=inset)-|",
				"H:|-indent-[onlyMetricsKeys]-(>=inset)-|",
				"H:|-inset-[ignoreSuffixes]-gap-[suffixToBeIgnored(>=50)]-inset-|",
				"H:|-inset-[status]-gap-[copybutton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-headlineGap-[from_font]-row-[to_font]-headlineGap-[lsb]-stackRow-[updateMetrics]-stackRow-[preferMetricKeys]-stackRow-[onlyMetricsKeys]-stackRow-[ignoreSuffixes]-inset-[copybutton]-inset-|",
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.copybutton, "attribute2": "centerY"},
				{"view1": self.w.text_anchor, "attribute1": "centerY", "view2": self.w.from_font, "attribute2": "centerY"},
				{"view1": self.w.text_value, "attribute1": "centerY", "view2": self.w.to_font, "attribute2": "centerY"},
				{"view1": self.w.rsb, "attribute1": "centerY", "view2": self.w.lsb, "attribute2": "centerY"},
				{"view1": self.w.width, "attribute1": "centerY", "view2": self.w.lsb, "attribute2": "centerY"},
				{"view1": self.w.suffixToBeIgnored, "attribute1": "centerY", "view2": self.w.ignoreSuffixes, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "indent": inset + 18, "gap": 8, "row": 6, "headlineGap": 10, "stackRow": 8},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

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
			myMasterNameList = [f"{i + 1}: {self.listOfMasters[i].font.familyName} - {self.listOfMasters[i].name}" for i in range(len(self.listOfMasters))]
			return myMasterNameList
		except:
			print(traceback.format_exc())

	def outputError(self, errMsg):
		print(f"Steal Sidebearings Warning: {errMsg}")

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

		targetLayers = [targetFont.glyphs[layer.parent.name].layers[targetMasterID] for layer in selectedTargetLayers if targetFont.glyphs[layer.parent.name]]
		if not targetLayers:
			self.setStatus("⚠️ No glyphs selected in the target font.")
			return

		self.setStatus(f"🛠️ Processing {len(targetLayers)} glyphs…")
		for targetLayer in targetLayers:
			try:
				targetGlyph = targetLayer.parent
				targetGlyphName = targetGlyph.name
				self.setStatus(f"🔠 {targetGlyphName}")
				sourceGlyphName = targetGlyphName

				if ignoreSuffixes:
					# replace suffix in the middle of the name:
					sourceGlyphName = targetGlyphName.replace(f".{suffixToBeIgnored}.", ".")
					# replace suffix at the end of the name:
					if sourceGlyphName.endswith(f".{suffixToBeIgnored}"):
						sourceGlyphName = sourceGlyphName[:-len(suffixToBeIgnored) - 1]

				sourceGlyph = sourceFont.glyphs[sourceGlyphName]
				if not sourceGlyph:
					print(f"     {sourceGlyphName}: not found in source font")
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
							print(f"     {targetGlyphName}, left glyph key: '{targetGlyph.leftMetricsKey}'")
						if sourceGlyph.rightMetricsKey:
							targetGlyph.rightMetricsKey = sourceGlyph.rightMetricsKey
							metricsR = True
							print(f"     {targetGlyphName}, right glyph key: '{targetGlyph.rightMetricsKey}'")
						if sourceGlyph.widthMetricsKey:
							targetGlyph.widthMetricsKey = sourceGlyph.widthMetricsKey
							metricsW = True
							print(f"     {targetGlyphName}, width glyph key: '{targetGlyph.widthMetricsKey}'")
						if sourceLayer.leftMetricsKey:
							targetLayer.leftMetricsKey = sourceLayer.leftMetricsKey
							metricsL = True
							print(f"     {targetGlyphName}, left layer key: '{targetLayer.leftMetricsKey}'")
						if sourceLayer.rightMetricsKey:
							targetLayer.rightMetricsKey = sourceLayer.rightMetricsKey
							metricsR = True
							print(f"     {targetGlyphName}, right layer key: '{targetLayer.rightMetricsKey}'")
						if sourceLayer.widthMetricsKey:
							targetLayer.widthMetricsKey = sourceLayer.widthMetricsKey
							metricsW = True
							print(f"     {targetGlyphName}, width layer key: '{targetLayer.widthMetricsKey}'")

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
				self.setStatus(f"❌ Error at {targetGlyphName}. Details in Macro Window.")

		# update metrics keys:
		if preferMetricKeys:
			for targetLayer in targetLayers:
				targetLayer.updateMetrics()

		self.setStatus(f"✅ Transferred metrics to {len(targetLayers)} glyphs.")


MetricsCopy()
