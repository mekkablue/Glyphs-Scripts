# MenuTitle: Spacing Checker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Look for glyphs with unusual spacings and open them in a new tab.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton


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
		windowHeight = 260
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Spacing Checker",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Find glyphs with unusual sidebearings. Open tab with glyphs where", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.asymmetricSBs = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "LSB & RSB differ more than", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.asymmetricDifference = vanilla.EditText((inset + 165, linePos, -inset - 32, 19), "50", callback=self.SavePreferences, sizeStyle='small')
		self.w.asymmetricUpdateButton = UpdateButton((-inset - 20, linePos - 1, -inset - 2, 18), title="K", callback=self.updateValues)
		self.w.asymmetricUpdateButton.getNSButton().setToolTip_("Update the entry with the measurements for uppercase K, presumably the largest difference in most designs.")
		linePos += lineHeight

		self.w.largeLSB = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "LSBs larger than", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.lsbThreshold = vanilla.EditText((inset + 108, linePos, -inset - 32, 19), "70", callback=self.SavePreferences, sizeStyle='small')
		self.w.lsbThresholdUpdateButton = UpdateButton((-inset - 20, linePos - 1, -inset - 2, 18), title="H", callback=self.updateValues)
		self.w.lsbThresholdUpdateButton.getNSButton().setToolTip_("Update the entry with the measurements for uppercase H, presumably the largest LSB in most designs.")
		linePos += lineHeight

		self.w.largeRSB = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "RSBs larger than", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.rsbThreshold = vanilla.EditText((inset + 108, linePos, -inset - 32, 19), "70", callback=self.SavePreferences, sizeStyle='small')
		self.w.rsbThresholdUpdateButton = UpdateButton((-inset - 20, linePos - 1, -inset - 2, 18), title="H", callback=self.updateValues)
		self.w.rsbThresholdUpdateButton.getNSButton().setToolTip_("Update the entry with the measurements for uppercase H, presumably the largest RSB in most designs.")
		linePos += lineHeight

		self.w.whiteGlyphs = vanilla.CheckBox((inset + 2, linePos, 180, 20), "LSB+RSB make up more than", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.whitePercentage = vanilla.EditText((inset + 173, linePos, 50, 19), "50", callback=self.SavePreferences, sizeStyle='small')
		self.w.whiteGlyphsText = vanilla.TextBox((inset + 173 + 52, linePos + 3, 105, 14), "% of overall width", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.includeBraceAndBracketLayers = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "Include brace and bracket layers", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "Look on all masters (otherwise current master only)", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.ignoreNonexportingGlyphs = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Ignore glyphs that do not export", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Open Tab", callback=self.SpacingCheckerMain)
		self.w.setDefaultButton(self.w.runButton)

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
				self.w.asymmetricDifference.set(updatedValue)

			if sender == self.w.lsbThresholdUpdateButton:
				if uppercaseH:
					referenceLayer = uppercaseH.layers[thisMaster.id]
					updatedValue = referenceLayer.LSB
				self.w.lsbThreshold.set(updatedValue)

			if sender == self.w.rsbThresholdUpdateButton:
				if uppercaseH:
					referenceLayer = uppercaseH.layers[thisMaster.id]
					updatedValue = referenceLayer.RSB
				self.w.rsbThreshold.set(updatedValue)

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
						percentage = (lsb + rsb) / thisLayer.width
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

			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			print("Space Checker Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
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
