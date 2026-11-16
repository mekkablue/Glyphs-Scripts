# MenuTitle: Spacing Checker
__doc__ = """
Look for glyphs with unusual spacings and open them in a new tab.
"""

import objc
import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSNumberFormatter
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


class SpacingChecker(mekkaObject):
	prefDict = {
		"asymmetricDifference": 90,
		"asymmetricSBs": 0,
		"largeLSB": 0,
		"lsbThreshold": 100,
		"largeRSB": 0,
		"rsbThreshold": 100,
		"whiteGlyphs": 0,
		"whitePercentage": 10,
		"allMasters": 0,
		"includeBraceAndBracketLayers": 1,
		"ignoreNonexportingGlyphs": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Spacing Checker",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Find glyphs with unusual sidebearings. Open tab with glyphs where", sizeStyle='small', selectable=True)

		def integerFormatter(minimum=0, maximum=None):
			formatter = NSNumberFormatter.alloc().init()
			formatter.setAllowsFloats_(False)
			formatter.setMinimum_(minimum)
			if maximum is not None:
				formatter.setMaximum_(maximum)
			return formatter

		self.w.asymmetricSBs = vanilla.CheckBox("auto", "LSB & RSB differ more than", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.asymmetricDifference = SteppingEditText("auto", "50", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter())
		self.w.asymmetricUpdateButton = UpdateButton("auto", title="K", callback=self.updateValues)
		self.w.asymmetricUpdateButton.setToolTip("Update the entry with the measurements for uppercase K, presumably the largest difference in most designs.")

		self.w.largeLSB = vanilla.CheckBox("auto", "LSBs larger than", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.lsbThreshold = SteppingEditText("auto", "70", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter())
		self.w.lsbThresholdUpdateButton = UpdateButton("auto", title="H", callback=self.updateValues)
		self.w.lsbThresholdUpdateButton.setToolTip("Update the entry with the measurements for uppercase H, presumably the largest LSB in most designs.")

		self.w.largeRSB = vanilla.CheckBox("auto", "RSBs larger than", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.rsbThreshold = SteppingEditText("auto", "70", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter())
		self.w.rsbThresholdUpdateButton = UpdateButton("auto", title="H", callback=self.updateValues)
		self.w.rsbThresholdUpdateButton.setToolTip("Update the entry with the measurements for uppercase H, presumably the largest RSB in most designs.")

		self.w.whiteGlyphs = vanilla.CheckBox("auto", "LSB+RSB make up more than", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.whitePercentage = SteppingEditText("auto", "50", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter(0, 100))
		self.w.whiteGlyphsText = vanilla.TextBox("auto", "% of overall width", sizeStyle='small', selectable=True)

		self.w.includeBraceAndBracketLayers = vanilla.CheckBox("auto", "Include brace and bracket layers", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.allMasters = vanilla.CheckBox("auto", "Look on all masters (otherwise current master only)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreNonexportingGlyphs = vanilla.CheckBox("auto", "Ignore glyphs that do not export", value=True, callback=self.SavePreferences, sizeStyle='small')

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Open Tab", callback=self.SpacingCheckerMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# checkboxes with a follower hug their text, the followers take the rest:
		followerCheckBoxNames = ("asymmetricSBs", "largeLSB", "largeRSB", "whiteGlyphs")
		for checkBoxName in followerCheckBoxNames:
			getattr(self.w, checkBoxName).getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			getattr(self.w, checkBoxName).getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		for fieldName in ("asymmetricDifference", "lsbThreshold", "rsbThreshold", "whitePercentage"):
			getattr(self.w, fieldName).getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.whiteGlyphsText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		columnRules = [
			{"view1": getattr(self.w, checkBoxName), "attribute1": "width", "view2": self.w.whiteGlyphs, "attribute2": "width"}
			for checkBoxName in followerCheckBoxNames if checkBoxName != "whiteGlyphs"
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[asymmetricSBs]-gap-[asymmetricDifference]-gap-[asymmetricUpdateButton]-inset-|",
				"H:|-inset-[largeLSB]-gap-[lsbThreshold]-gap-[lsbThresholdUpdateButton]-inset-|",
				"H:|-inset-[largeRSB]-gap-[rsbThreshold]-gap-[rsbThresholdUpdateButton]-inset-|",
				"H:|-inset-[whiteGlyphs]-gap-[whitePercentage(50)]-gap-[whiteGlyphsText]-(>=inset)-|",
				"H:|-inset-[includeBraceAndBracketLayers]-(>=inset)-|",
				"H:|-inset-[allMasters]-(>=inset)-|",
				"H:|-inset-[ignoreNonexportingGlyphs]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-headlineGap-[asymmetricSBs]-stackRow-[largeLSB]-stackRow-[largeRSB]-stackRow-[whiteGlyphs]-stackRow-[includeBraceAndBracketLayers]-stackRow-[allMasters]-stackRow-[ignoreNonexportingGlyphs]-barGap-[progress(16)]-inset-[runButton]-inset-|",
				{"view1": self.w.asymmetricDifference, "attribute1": "centerY", "view2": self.w.asymmetricSBs, "attribute2": "centerY"},
				{"view1": self.w.asymmetricUpdateButton, "attribute1": "centerY", "view2": self.w.asymmetricSBs, "attribute2": "centerY"},
				{"view1": self.w.lsbThreshold, "attribute1": "centerY", "view2": self.w.largeLSB, "attribute2": "centerY"},
				{"view1": self.w.lsbThresholdUpdateButton, "attribute1": "centerY", "view2": self.w.largeLSB, "attribute2": "centerY"},
				{"view1": self.w.rsbThreshold, "attribute1": "centerY", "view2": self.w.largeRSB, "attribute2": "centerY"},
				{"view1": self.w.rsbThresholdUpdateButton, "attribute1": "centerY", "view2": self.w.largeRSB, "attribute2": "centerY"},
				{"view1": self.w.whitePercentage, "attribute1": "centerY", "view2": self.w.whiteGlyphs, "attribute2": "centerY"},
				{"view1": self.w.whiteGlyphsText, "attribute1": "centerY", "view2": self.w.whiteGlyphs, "attribute2": "centerY"},
			] + columnRules,
			metrics={"inset": inset, "gap": 8, "headlineGap": 10, "stackRow": 8, "barGap": 12},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		anyOptionSelected = self.w.asymmetricSBs.get() or self.w.largeLSB.get() or self.w.largeRSB.get() or self.w.whiteGlyphs.get()
		self.w.runButton.enable(anyOptionSelected)

	def updateValues(self, sender):
		updatedValue = 0.0  # fallback value

		thisFont = Glyphs.font
		if thisFont:
			thisMaster = thisFont.selectedFontMaster
			uppercaseK = thisFont.glyphs["K"]
			uppercaseH = thisFont.glyphs["H"]

			if sender == self.w.asymmetricUpdateButton:
				if uppercaseK:
					referenceLayer = uppercaseK.layers[thisMaster.id]
					updatedValue = abs(referenceLayer.LSB - referenceLayer.RSB)
				self.w.asymmetricDifference.set(round(updatedValue))

			if sender == self.w.lsbThresholdUpdateButton:
				if uppercaseH:
					referenceLayer = uppercaseH.layers[thisMaster.id]
					updatedValue = referenceLayer.LSB
				self.w.lsbThreshold.set(round(updatedValue))

			if sender == self.w.rsbThresholdUpdateButton:
				if uppercaseH:
					referenceLayer = uppercaseH.layers[thisMaster.id]
					updatedValue = referenceLayer.RSB
				self.w.rsbThreshold.set(round(updatedValue))

		self.SavePreferences(sender)

	def isLayerAffected(self, thisLayer):
		try:
			if self.pref("asymmetricSBs"):
				try:
					asymmetricDifference = self.prefFloat("asymmetricDifference")
					if abs(thisLayer.LSB - thisLayer.RSB) > asymmetricDifference:
						return True
				except Exception as e:
					raise e

			if self.pref("largeLSB"):
				try:
					lsbThreshold = self.prefFloat("lsbThreshold")
					if thisLayer.LSB > lsbThreshold:
						return True
				except Exception as e:
					raise e

			if self.pref("largeRSB"):
				try:
					rsbThreshold = self.prefFloat("rsbThreshold")
					if thisLayer.RSB > rsbThreshold:
						return True
				except Exception as e:
					raise e

			if self.pref("whiteGlyphs"):
				try:
					if not thisLayer.width > 0.0:
						return False
					else:
						whitePercentage = self.prefFloat("whitePercentage")
						lsb = max(0.0, thisLayer.LSB)
						rsb = max(0.0, thisLayer.RSB)
						percentage = 100.0 * (lsb + rsb) / thisLayer.width  # whitePercentage is in percent
						if percentage > whitePercentage:
							return True
				except Exception as e:
					raise e

			return False

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Spacing Checker Error while checking glyph '%s', layer '%s':\n%s" % (thisLayer.parent, thisLayer.name, e))
			import traceback
			print(traceback.format_exc())

	def SpacingCheckerMain(self, sender):
		try:
			thisFont = Glyphs.font  # frontmost font
			if not thisFont:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			# clears the macro window log:
			Glyphs.clearLog()
			print("Space Checker Report for %s" % thisFont.familyName)
			print(thisFont.filepath if thisFont.filepath else f"{thisFont.familyName} (unsaved)")
			print()

			collectedLayers = []
			braceAndBracketIncluded = self.pref("includeBraceAndBracketLayers")
			if self.pref("allMasters"):
				mastersToCheck = thisFont.masters
				print("Searching %i masters..." % len(mastersToCheck))
			else:
				currentMaster = thisFont.selectedFontMaster
				mastersToCheck = (currentMaster, )
				print("Searching master: %s" % currentMaster.name)

			print()

			ignoreNonexportingGlyphs = self.pref("ignoreNonexportingGlyphs")

			numOfGlyphs = len(thisFont.glyphs)
			for index, thisGlyph in enumerate(thisFont.glyphs):
				self.w.progress.set(int(100 * (float(index) / numOfGlyphs)))
				if thisGlyph.export or not ignoreNonexportingGlyphs:
					for thisLayer in thisGlyph.layers:
						layerMaster = thisLayer.associatedFontMaster()
						if thisLayer.name and layerMaster in mastersToCheck:
							isMasterLayer = layerMaster.id == thisLayer.layerId
							if isMasterLayer or (braceAndBracketIncluded and thisLayer.isSpecialLayer):
								if self.isLayerAffected(thisLayer):
									collectedLayers.append(thisLayer)

			if not collectedLayers:
				Message(title="No Affected Glyphs Found", message="No glyphs found that fulfil the chosen criteria.", OKButton=u"🙌 High Five!")
			else:
				if self.pref("allMasters"):
					newTab = thisFont.newTab()
					newTab.layers = collectedLayers
				else:
					# enable Cmd+1,2,3,...:
					glyphNames = [layer.parent.name for layer in collectedLayers]
					tabText = "/" + "/".join(glyphNames)
					thisFont.newTab(tabText)
			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Spacing Checker Error: %s" % e)
			import traceback
			print(traceback.format_exc())


SpacingChecker()
